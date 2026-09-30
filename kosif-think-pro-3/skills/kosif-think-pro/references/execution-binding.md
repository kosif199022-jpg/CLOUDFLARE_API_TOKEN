# Execution binding protocol

## Purpose
Prevent the reasoning layer from selecting one plan while a downstream executor receives or produces a materially different plan.

## Contract model
Create a frozen Execution Contract after material synthesis/arbitration and before execution:
- contract_id
- user_goal
- selected_decision
- required_attributes
- forbidden_attributes
- allowed_flexibility
- executor_type
- success_criteria
- verification_method
- decision_provenance

A new decision creates a new contract. Never silently mutate a contract after preflight.

## Final Executor Brief
The Final Executor Brief is the single active execution instruction derived from the contract. It may translate the decision into tool-specific language but may not reinterpret the decision.

## Drift classes
- `decision_swap`: selected option changes.
- `required_drop`: a material required attribute disappears.
- `forbidden_injection`: a forbidden or rejected attribute appears.
- `tool_mismatch`: executor cannot preserve the contract.
- `result_drift`: produced artifact/state materially violates the contract.

## Gates
### Preflight
PASS only when selected decision, required attributes, forbidden attributes, tool compatibility and verification path are coherent.
REVISE when wording/tool formatting can repair the mismatch without changing the decision.
BLOCK when repair would require changing the selected decision or uncertainty remains material.

### Postcondition
PASS only when the observable artifact/state satisfies the material contract.
FAILED-DRIFT when a material required/forbidden condition is violated.
NOT-VERIFIED when the output cannot be inspected adequately.

## Inferred-prompt host tools
If the host does not expose the literal provider prompt:
- bind at the Final Executor Brief level;
- make it the last material instruction before execution;
- avoid restating rejected alternatives afterward;
- verify observable output;
- never claim exact provider-prompt or cryptographic enforcement.

## Permanent regression: Ronin duck
Selected decision: Edo Ronin duck.
Required: anthropomorphic duck; Edo/ronin visual language; lacquered armor; rain-lit temple/courtyard.
Forbidden: modern tactical armor; assault rifle; camouflage; helicopters; armored vehicles.

Expected:
- brief with rifle/tactical vest => BLOCK before generation;
- generated modern-military duck => FAILED-DRIFT after generation;
- corrected Edo ronin duck => PASS.
