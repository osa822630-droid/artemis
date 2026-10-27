# Connected ARTEMIS workflow

Use this only when ARTEMIS MCP tools are actually present. The server's live
schemas take precedence over these examples. Never pretend to call a tool.

## Readiness and device selection

1. Call `mobile_diagnose` to inspect readiness and available devices. Relay the
   ordered `next_steps` when blocked. Ask the user which device to use if multiple
   are available, then pass its `device_serial` consistently.
2. Get approval before `attempt_fix=true`: it may regenerate ADB keys, restart
   ADB, or clear stale locks. Live credential checks and deeper device probes
   should be requested only when needed. Secrets stay in host configuration.
3. Call `mobile_get_device_state(view_type="screenshot", device_serial=...)` or
   `view_type="hierarchy"` to establish the current state. Omit optional fields
   when unknown; never invent serial numbers.

## Delegate a bounded task

Call `mobile_run_task` with a self-contained `task_desc` specifying the goal,
target app, authorized actions, constraints, and termination conditions.

- `model="Flash"`: simple, deterministic UI paths.
- `model="Pro"`: exploration, branching recovery, diagnostics, monitoring, or
  detailed verified results. Use `expected_output_desc` to specify the evidence
  and report needed.
- Pass `device_serial` if selected. `app_path`, if used, refers to a file on the
  **device host**, not a file merely uploaded to Claude Web.
- Omit `conversation_id` unless the client actually supplies a valid one. Do not
  fabricate IDs to enable wakeup notifications.

The call returns immediately with a `trace_id`; it does not mean the task passed.

## Follow up and verify

Use `mobile_manage_task(action="status", trace_id=...)` to check progress. While
the session can continue making tool calls, follow the server's polling guidance
(at least once per minute). Do not rely solely on optional notifications.
If the web client cannot keep polling or schedule timers, say monitoring is
limited to the active conversation and offer a manual status check; do not
promise autonomous background monitoring.

Use `mobile_manage_task(action="stop", trace_id=...)` when the user requests a
stop, the task exceeds its scope, or continuing would be unsafe.

After completion, call `mobile_inspect_trace(action="view_summary", trace_id=...)`
and, when useful, `action="view_step_screenshots"` using the live schema's required
arguments. Inspect reported errors and Pro notes through available tools.
If results contain only host log paths and no file-access tool is connected,
ask the user to upload the relevant redacted files; the chat sandbox cannot read
the device host's filesystem. Distinguish task completion from verified success.

## Failure handling

Call `mobile_diagnose` instead of blindly resubmitting failed tasks. Read returned
errors, readiness findings, and actionable steps. A `degraded` verdict can permit
execution with optional features unavailable; disclose the limitation. A
`blocked` verdict needs remediation first. Never ask the user to expose an
unauthenticated ADB, MCP server, or admin console publicly.
