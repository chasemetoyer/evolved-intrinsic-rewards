# Project entry point

Read `AGENTS.md`, then `handoff-cross-platform/CONTINUE-HERE.md` and the canonical
`session-state.json` it identifies. Follow the user's current instructions and
the registered protocol. These project files carry shared state between agents;
do not assume another model's private conversation or memory is available.

## Auto-loaded handoff (Claude Code)

The canonical handoff lives in the Mac project folder, not in this worktree's
copy. Claude Code loads it through these imports:

@/Users/chasemetoyer/Desktop/evolved-intrinsic-rewards/handoff-cross-platform/CONTINUE-HERE.md
@/Users/chasemetoyer/Desktop/evolved-intrinsic-rewards/handoff-cross-platform/SESSION-RULES.md
@/Users/chasemetoyer/Desktop/evolved-intrinsic-rewards/handoff-cross-platform/DECISIONS.md

If they did not load, read those three files directly before acting.
