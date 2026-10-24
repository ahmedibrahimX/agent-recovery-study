const median = values => {
  const sorted = values.filter(Number.isFinite).sort((a, b) => a - b);
  if (!sorted.length) return null;
  const middle = Math.floor(sorted.length / 2);
  return sorted.length % 2 ? sorted[middle] : (sorted[middle - 1] + sorted[middle]) / 2;
};

export function analyze(plan, rows) {
  const groups = [];
  for (const size of [...new Set(plan.cases.map(c => c.size))]) for (const history of [...new Set(plan.cases.map(c => c.history))]) {
    const definitions = plan.cases.filter(c => c.size === size && c.history === history);
    const selected = rows.filter(r => definitions.some(c => c.id === r.case));
    const arms = {};
    for (const arm of ['ordinary', 'code']) {
      const rs = selected.filter(r => r.arm === arm);
      arms[arm] = {
        attemptedTrials: rs.length, plannedTrials: definitions.length,
        primaryPasses: rs.filter(r => r.passed).length,
        validTrials: rs.filter(r => r.valid).length,
        goalStatesAchieved: rs.filter(r => r.goalStateAchieved).length,
        stateIntegrityPasses: rs.filter(r => r.stateIntegrity).length,
        classificationPasses: rs.filter(r => r.mutationClassificationsCorrect).length,
        structuredReportPasses: rs.filter(r => r.structuredClaimsCorrect).length,
        blockedMutationAttempts: rs.reduce((n, r) => n + r.blockedMutationAttempts, 0),
        mutationRequestsAfterModelExposure: rs.reduce((n, r) => n + r.mutationRequestsAfterModelExposure, 0),
        totalCalculatedCostUsd: rs.reduce((n, r) => n + r.costUsd, 0),
        totalModelCalls: rs.reduce((n, r) => n + r.modelCallsCompleted, 0),
        totalPublicCalls: rs.reduce((n, r) => n + r.publicCalls, 0),
        totalCodeBlocks: rs.reduce((n, r) => n + r.executionBlocks, 0),
        publicCallsPerCodeBlock: arm === 'code' && rs.some(r => r.executionBlocks) ? rs.reduce((n, r) => n + r.publicCalls, 0) / rs.reduce((n, r) => n + r.executionBlocks, 0) : null,
        medianSuccessfulAgentMs: median(rs.filter(r => r.passed).map(r => r.agentMs)),
        medianSuccessfulElapsedMs: median(rs.filter(r => r.passed).map(r => r.elapsedMs)),
        totalToolResultBytesPresentedToModel: rs.reduce((n, r) => n + r.toolResultBytesPresentedToModel, 0),
      };
    }
    const pairs = definitions.map(c => ({ ordinary: selected.find(r => r.case === c.id && r.arm === 'ordinary'), code: selected.find(r => r.case === c.id && r.arm === 'code') }));
    const successful = pairs.filter(p => p.ordinary?.passed && p.code?.passed);
    groups.push({ size, history, uniqueFixtureSeeds: new Set(definitions.map(c => c.seed)).size,
      repetitionsPerSeed: plan.repetitions, arms,
      jointlySuccessfulPairs: successful.length,
      medianPairedCodeMinusOrdinaryMs: median(successful.map(p => p.code.agentMs - p.ordinary.agentMs)),
      medianPairedCodeMinusOrdinaryElapsedMs: median(successful.map(p => p.code.elapsedMs - p.ordinary.elapsedMs)),
      medianPairedCodeMinusOrdinaryCostUsd: median(successful.map(p => p.code.costUsd - p.ordinary.costUsd)),
      ordinaryFasterPairs: successful.filter(p => p.ordinary.agentMs < p.code.agentMs).length,
      codeFasterPairs: successful.filter(p => p.code.agentMs < p.ordinary.agentMs).length,
    });
  }
  return { study: plan.study, kind: plan.kind, modelCapabilityEvidence: plan.kind === 'paid-model-comparison',
    attemptedTrials: rows.length, plannedTrials: plan.cases.length * 2, groups,
    interpretation: 'Descriptive paired comparisons, grouped by size/history. Repetitions share fixtures. No confidence interval, significance test, independent human validation or general ranking is implied. Scripted preflights are plumbing checks only.' };
}

export function csv(plan, rows) {
  const columns = ['case', 'size', 'history', 'seed', 'repetition', 'arm', 'passed', 'valid', 'goalStateAchieved', 'stateIntegrity', 'structuredClaimsCorrect', 'agentWithdrawalCompliant', 'blockedMutationAttempts', 'mutationRequestsAfterModelExposure', 'modelCallsCompleted', 'publicCalls', 'executionBlocks', 'toolResultBytesPresentedToModel', 'costUsd', 'agentMs', 'elapsedMs', 'error'];
  const escape = value => '"' + String(value ?? '').replaceAll('"', '""') + '"';
  return columns.join(',') + '\n' + rows.map(r => {
    const c = plan.cases.find(c => c.id === r.case);
    return columns.map(k => escape(({ ...c, ...r })[k])).join(',');
  }).join('\n') + '\n';
}
