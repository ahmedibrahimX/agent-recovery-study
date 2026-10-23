import { DynamicWorkerExecutor, generateTypesFromJsonSchema } from '@cloudflare/codemode';

export default {
  async fetch(request: Request, env: { LOADER: WorkerLoader; BROKER: Fetcher }): Promise<Response> {
    const p = await request.json() as any;
    if (p.operation === 'describe') return Response.json({ types: generateTypesFromJsonSchema(p.tools) });
    if (typeof p.code !== 'string' || p.code.length > 32000) return Response.json({ error: 'Code exceeds 32,000 characters' });
    const fns = Object.fromEntries(Object.keys(p.tools).map(name => [name, async (args: unknown = {}) => {
      const response = await env.BROKER.fetch('http://broker/tool', {
        method: 'POST', headers: { authorization: `Bearer ${p.token}`, 'content-type': 'application/json' },
        body: JSON.stringify({ name, args, block: p.block }),
      });
      const result = await response.json() as any;
      if (!response.ok || !result.ok) throw new Error(result.error ?? 'Tool failed');
      return result.result;
    }]));
    const executor = new DynamicWorkerExecutor({ loader: env.LOADER, globalOutbound: null, timeout: 60000 });
    const source = p.code.trim().replace(/;\s*$/, '');
    const code = /^async\s*\(\s*\)\s*=>/.test(source) ? source : `async () => {\n${source}\n}`;
    return Response.json(await executor.execute(code, [{ name: 'codemode', fns }]));
  },
};
