export function compressToACTP(fullContext) {
  return {
    core: {
      goal: extractGoal(fullContext),
      strategy: extractStrategy(fullContext),
      principle: "Speed > perfect architecture"
    },

    constraints: extractConstraints(fullContext),

    architecture: {
      maestro: "Multi-model UI (parallel responses)",
      actp: "Portable JSON context protocol",
      integration: "ACTP export button inside Maestro"
    },

    features: {
      must_have: extractMustHave(fullContext),
      high_priority: extractHighPriority(fullContext)
    },

    ai_pattern: {
      function: "callAI(prompt): Promise<string>",
      rule: "Treat AI as black box"
    },

    current_problem: extractCurrentProblem(fullContext),

    next_steps: extractNextSteps(fullContext)
  };
}

function extractGoal(ctx) {
  return (
    ctx.business_strategy?.goal ||
    ctx.one_sentence_summary ||
    "Goal undefined: Requesting mission alignment..."
  );
}

function extractStrategy(ctx) {
  return ctx.architecture_decisions?.priority_split || null;
}

function extractConstraints(ctx) {
  return ctx.core_constraints?.[0]?.rules || [];
}

function extractMustHave(ctx) {
  return ctx.key_features_discussed
    ?.filter(f => f.status === "MUST_HAVE")
    .map(f => f.feature) || [];
}

function extractHighPriority(ctx) {
  return ctx.key_features_discussed
    ?.filter(f => f.status === "HIGH PRIORITY")
    .map(f => f.feature) || [];
}

function extractCurrentProblem(ctx) {
  if (!ctx.react_ui_debugging) return null;

  return {
    area: "React UI",
    issue: ctx.react_ui_debugging.problem_summary,
    fix: ctx.react_ui_debugging.final_fix_strategy?.approach
  };
}

function extractNextSteps(ctx) {
  return ctx.next_steps || [];
}
