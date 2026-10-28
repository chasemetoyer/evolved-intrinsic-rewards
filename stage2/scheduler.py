"""Provider-independent scheduling loop shared by every Stage 2 plan.

Rules carried over from Stage 1: reserve and persist before each paid submission;
record the provider call ID before any waiting; reattach recorded calls on resume;
never respawn a key the ledger already knows; cancel and mark in-flight calls
uncertain if the loop stops unexpectedly. A plan decides which specs are ready.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from stage2.budget import BudgetStop, Stage2Ledger
from stage2.common import canonical_sha


@dataclass
class Hooks:
    persist: Callable[[], None]
    sync: Callable[[dict], Path]                 # download a result; return its local attempt directory
    sync_existing: Callable[[str], tuple[dict, Path]]  # re-sync an already completed key on resume
    submitted: Callable[[dict, object], None] = lambda spec, call: None
    completed: Callable[[str, dict], None] = lambda key, result: None
    after_completions: Callable[[], None] = lambda: None
    heartbeat: Callable[[dict], None] = lambda active: None
    sleep: Callable[[float], None] = time.sleep
    now: Callable[[], float] = time.time


@dataclass
class RunState:
    active: dict = field(default_factory=dict)
    submitted: list = field(default_factory=list)


def run_plan(plan, ledger: Stage2Ledger, backend, hooks: Hooks, concurrency: int) -> RunState:
    state = RunState()
    try:
        for key, record in sorted(ledger.data["calls"].items()):
            if not plan.owns(key):
                continue
            spec = plan.spec_for_key(key)
            if record["spec_sha256"] != canonical_sha(spec):
                raise BudgetStop("Existing run specification differs: " + key)
            if record["status"] == "complete":
                result, directory = hooks.sync_existing(key)
                plan.record(key, result, directory)
            elif record["status"] in {"reserved", "running"}:
                if not record.get("function_call_id"):
                    ledger.uncertain(key, "Pending submission lacks a recoverable provider handle")
                    hooks.persist()
                    raise BudgetStop("Inspect provider state for interrupted submission: " + key)
                state.active[key] = backend.reattach(record["function_call_id"])
            else:
                raise BudgetStop("Uncertain call requires provider billing reconciliation: " + key)
        while True:
            blocked = None
            queue = [s for s in plan.ready_specs(ledger) if s["id"] not in ledger.data["calls"]]
            while queue and len(state.active) < concurrency:
                spec = queue.pop(0)
                try:
                    reservation = ledger.reserve(spec["id"], canonical_sha(spec), plan.deadline_seconds(spec))
                except BudgetStop as exc:
                    blocked = exc
                    break
                hooks.persist()  # durability boundary BEFORE the paid invocation
                try:
                    call = backend.spawn(spec, reservation["absolute_deadline"])
                except BaseException as exc:
                    ledger.uncertain(spec["id"], f"Submission outcome unknown: {type(exc).__name__}: {exc}")
                    hooks.persist()
                    raise
                state.active[spec["id"]] = call
                state.submitted.append(spec["id"])
                ledger.associate(spec["id"], call.object_id, backend.app_id)
                hooks.persist()
                hooks.submitted(spec, call)
            if not state.active:
                if blocked is not None:
                    raise blocked
                if plan.done(ledger):
                    return state
                raise RuntimeError("Plan is not done but has nothing in flight and nothing ready to submit")
            completed = False
            for key, call in list(state.active.items()):
                record = ledger.data["calls"][key]
                result = backend.poll(call)
                if result is None:
                    if hooks.now() >= record["absolute_deadline"]:
                        raise BudgetStop("Shared call deadline reached: " + key)
                    continue
                # Charge submit-to-observed-result wall time, including queueing,
                # startup and any automatic preemption restarts.
                ledger.complete(key, hooks.now() - record["submitted_unix_seconds"], result["usage"])
                del state.active[key]
                hooks.persist()
                directory = hooks.sync(result)
                plan.record(key, result, directory)
                hooks.completed(key, result)
                completed = True
            if completed:
                hooks.after_completions()
                hooks.persist()
                ledger.assert_can_launch()
            hooks.heartbeat(state.active)
            if state.active and not completed:
                hooks.sleep(5)
    except BaseException:
        for key, call in list(state.active.items()):
            error = None
            try:
                backend.cancel(call)
            except Exception as exc:
                error = f"; cancellation failed: {type(exc).__name__}: {exc}"
            ledger.uncertain(key, "Controller stopped before recording a completed result" + (error or ""))
        hooks.persist()
        raise
