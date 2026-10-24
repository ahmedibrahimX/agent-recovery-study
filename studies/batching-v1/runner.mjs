import { createServer } from 'node:http';
import { spawn } from 'node:child_process';
import { mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { join, resolve } from 'node:path';
import { randomUUID } from 'node:crypto';
import { performance } from 'node:perf_hooks';
import { Miniflare, Response as MFResponse } from 'miniflare';
import { Backend } from './scenario.mjs';
import { tools, reportSchema, policy } from './schema.mjs';
import { Provider, save } from './provider.mjs';
import { scriptedResponse } from './scripted.mjs';
import { check } from './checker.mjs';

const read = path => JSON.parse(readFileSync(path, 'utf8'));

function agentProcess(python, folder, limitMs) {
  return new Promise((resolvePromise, reject) => {
    const env = Object.fromEntries(['PATH', 'HOME', 'TMPDIR', 'TEMP', 'SYSTEMROOT'].filter(k => process.env[k]).map(k => [k, process.env[k]]));
    Object.assign(env, { PYTHONDONTWRITEBYTECODE: '1', PYTHONNOUSERSITE: '1', LANGSMITH_TRACING: 'false', LANGCHAIN_TRACING_V2: 'false' });
    const child = spawn(python, ['-s', '-B', 'agent.py', folder], { env, stdio: ['ignore', 'pipe', 'pipe'] });
    const out = [], err = [];
    let timedOut = false;
    const timer = setTimeout(() => { timedOut = true; child.kill('SIGTERM'); setTimeout(() => child.kill('SIGKILL'), 2000).unref(); }, limitMs);
    child.stdout.on('data', d => out.push(d)); child.stderr.on('data', d => err.push(d));
    child.on('error', e => { clearTimeout(timer); reject(e); });
    child.on('close', code => {
      clearTimeout(timer);
      writeFileSync(join(folder, 'agent-stdout.log'), Buffer.concat(out));
      writeFileSync(join(folder, 'agent-stderr.log'), Buffer.concat(err));
      if (code === 0 && !timedOut) resolvePromise();
      else reject(new Error(timedOut ? 'Trial time limit reached' : `Agent process exited ${code}; inspect its local error log`));
    });
  });
}

export async function runTrial({ definition, arm, folder, config, ledger, python, scripted = false }) {
  mkdirSync(folder, { recursive: true, mode: 0o700 });
  const started = performance.now();
  const backend = new Backend(definition, config.service);
  const token = randomUUID();
  let report = null, submittedAt = null, agentStarted = null, provider, mf, server, error = null;
  let publicCalls = 0, activeTools = 0, activeExecutions = 0, activeModels = 0;
  const blocks = [];
  const publicCall = async (name, args, origin = {}) => {
    if (report) {
      backend.event('post_terminal_request', { name, args, ...origin });
      return { ok: false, error: 'Task already submitted' };
    }
    if (++publicCalls > config.limits.publicCalls) throw new Error('Public API call limit reached');
    activeTools++;
    try { return await backend.invoke(name, args, origin); }
    finally { activeTools--; }
  };
  save(join(folder, 'case.json'), definition);
  try {
    let description;
    if (arm === 'code') {
      mf = new Miniflare({
      modules: true, scriptPath: resolve('.runtime/worker.mjs'), compatibilityDate: '2026-07-30', compatibilityFlags: ['nodejs_compat'],
      workerLoaders: { LOADER: {} }, serviceBindings: { BROKER: async request => {
        if (request.headers.get('authorization') !== `Bearer ${token}`) return new MFResponse('Forbidden', { status: 403 });
        const p = await request.json();
        const r = await publicCall(p.name, p.args, { executionBlock: p.block });
        return new MFResponse(JSON.stringify(r), { headers: { 'content-type': 'application/json' } });
      } },
      });
      await mf.ready;
      description = await (await mf.dispatchFetch('http://worker/describe', { method: 'POST', body: JSON.stringify({ operation: 'describe', tools }) })).json();
    }
    const execute = async code => {
      if (report) return { error: 'Task already submitted' };
      if (blocks.length >= config.limits.codeBlocks) throw new Error('Code execution limit reached');
      const index = blocks.length, begin = performance.now();
      const block = { index, code, callsBefore: publicCalls };
      blocks.push(block); activeExecutions++;
      save(join(folder, `program-${index}.json`), { code });
      try {
        const response = await mf.dispatchFetch('http://worker/execute', { method: 'POST', body: JSON.stringify({ code, tools, token, block: index }) });
        const result = await response.json();
        save(join(folder, `program-${index}-result.json`), result);
        Object.assign(block, { durationMs: performance.now() - begin, resultBytes: Buffer.byteLength(JSON.stringify(result)) });
        return result;
      } finally { activeExecutions--; }
    };
    provider = new Provider({ folder, config, ledger, beforeRequest: (request, index) => backend.modelRequest(request, index),
      scripted: scripted ? (request, index) => scriptedResponse(backend, arm, request, index) : undefined });
    server = createServer(async (req, res) => {
      try {
        const auth = req.url === '/v1/messages' ? req.headers['x-api-key'] === token : req.headers.authorization === `Bearer ${token}`;
        if (!auth) throw new Error('Invalid local run credential');
        const chunks = []; let bytes = 0;
        for await (const chunk of req) { bytes += chunk.length; if (bytes > config.limits.requestBytes) throw new Error('Local request too large'); chunks.push(chunk); }
        const body = JSON.parse(Buffer.concat(chunks).toString());
        let result;
        if (req.url === '/v1/messages') {
          activeModels++;
          try { result = await provider.request(body); }
          finally { activeModels--; }
        }
        else if (req.url === '/tool') result = await publicCall(body.name, body.args);
        else if (req.url === '/execute') result = await execute(body.code);
        else if (req.url === '/messages') result = backend.messages();
        else if (req.url === '/status') result = { submitted: Boolean(report) };
        else if (req.url === '/submit') {
          if (activeTools || activeExecutions) result = { accepted: false, error: 'Wait for outstanding tools before submitting.' };
          else if (report) result = { accepted: false, error: 'Task already submitted' };
          else {
            result = backend.terminal(body);
            if (result.accepted) { report = body; submittedAt = performance.now(); save(join(folder, 'report.json'), report); }
          }
        } else throw new Error('Unknown local endpoint');
        res.writeHead(200, { 'content-type': 'application/json' }); res.end(JSON.stringify(result));
      } catch (e) {
        save(join(folder, 'gateway-error.json'), { error: String(e) });
        res.writeHead(400, { 'content-type': 'application/json' }); res.end(JSON.stringify({ type: 'error', error: { type: 'invalid_request_error', message: String(e) } }));
      }
    });
    await new Promise(r => server.listen(0, '127.0.0.1', r));
    const commonContext = { task: `Reconcile the ${definition.size} assigned pending intents.`, service: config.service };
    // Audit the same underlying information; encode tool documentation through
    // each interface, rather than burdening ordinary tools with duplicate types.
    save(join(folder, 'public-context.json'), { ...commonContext, tools, reportSchema });
    const context = arm === 'code' ? { ...commonContext, types: description.types } : commonContext;
    save(join(folder, 'agent-input.json'), { gateway: `http://127.0.0.1:${server.address().port}`, token, arm, model: config.model,
      tools, reportSchema, context, limits: config.limits,
      systemPrompt: policy + (arm === 'code' ? '\nUse execute to write JavaScript against the supplied codemode API. You may chain calls, process intermediate data and parallelize independent work. Choose your own block size.' : '\nUse the registered structured tools. You may issue multiple independent tool calls in one model response and parallelize where useful.') });
    agentStarted = performance.now();
    await agentProcess(python, folder, config.limits.trialSeconds * 1000);
    if (!report) throw new Error('Agent ended without an accepted terminal report');
  } catch (e) { error = String(e); }
  finally {
    if (activeModels) provider?.cancelPending();
    // The agent has exited. Wait for already-started tool routes before snapshotting.
    const stopWaiting = performance.now() + 65000;
    while ((activeTools || activeExecutions || activeModels) && performance.now() < stopWaiting) await new Promise(r => setTimeout(r, 10));
    if (activeTools || activeExecutions || activeModels) error ??= 'Outstanding operations did not settle';
    if (server) { server.closeAllConnections(); await new Promise(r => server.close(r)); }
    await mf?.dispose();
  }
  const runtime = {
    arm, scripted, error, errorKind: error ? (/limit|budget|Model stopped/.test(error) ? 'resource_or_model_stop' : 'execution_or_provider_failure') : null,
    agentMs: submittedAt && agentStarted ? submittedAt - agentStarted : null,
    elapsedMs: performance.now() - started,
    modelCallsCompleted: provider?.calls.length ?? 0,
    modelMs: (provider?.calls ?? []).reduce((n, c) => n + c.latencyMs, 0),
    costUsd: (provider?.calls ?? []).reduce((n, c) => n + c.costUsd, 0),
    usage: Object.fromEntries(['input_tokens', 'output_tokens', 'cache_creation_input_tokens', 'cache_read_input_tokens'].map(k => [k, (provider?.calls ?? []).reduce((n, c) => n + (c.usage[k] ?? 0), 0)])),
    toolResultBytesPresentedToModel: (provider?.calls ?? []).reduce((n, c) => n + read(join(folder, `model-${c.index}-request.json`)).messages.reduce((m, message) => m + (Array.isArray(message.content) ? message.content.filter(x => x.type === 'tool_result').reduce((k, x) => k + Buffer.byteLength(JSON.stringify(x.content)), 0) : 0), 0), 0),
    executionBlocks: blocks.length,
  };
  const evidence = backend.evidence();
  const requests = backend.events.filter(e => e.kind === 'model_request').map(e => read(join(folder, `model-${e.index}-request.json`)));
  const verdict = check({ definition, evidence, report, runtime, requests });
  save(join(folder, 'evidence.json'), evidence);
  save(join(folder, 'runtime.json'), runtime);
  save(join(folder, 'blocks.json'), blocks.map(b => ({ ...b, nativeCalls: backend.events.filter(e => e.kind === 'request' && e.executionBlock === b.index).length })));
  save(join(folder, 'verdict.json'), verdict);
  return { ...verdict, ...runtime, arm, case: definition.id };
}
