# Lesson 09 — Reference remediation

`quality-fixtures.js` deliberately retains two inert quality defects so the
default-branch scan has stable Standard findings. Apply these changes only on a
temporary workshop branch, compare the result with any proposed Autofix, and do
not merge the remediation if the repository should remain demo-ready.

## `js/template-syntax-in-string-literal`

The ordinary quoted string contains template syntax, so `${userName}` is
returned literally. Use backticks so JavaScript evaluates the placeholder:

```javascript
function buildGreeting(userName) {
  const preview = `Preview for ${userName}`;

  return {
    preview,
    message: `Welcome, ${userName}!`,
  };
}
```

This is a **Reliability** finding: the original code produces the wrong value.
The real template literal assigned to `preview` is intentionally present
because the high-precision query only considers files that otherwise use
template literals.

## `js/useless-assignment-to-local`

The first value assigned to `completed` is always overwritten before it can be
read. Compute the value once:

```javascript
function countCompleted(tasks) {
  const completed = tasks.filter((task) => task.complete).length;
  return completed;
}
```

This is a **Maintainability** finding. Removing the dead assignment preserves
behavior and removes misleading code. In production, do not remove the
right-hand side of a dead assignment without first checking it for side
effects; this fixture's `tasks.length` access has none.

## Verify the remediation

From this lesson directory:

```bash
node --check quality-fixtures.js
node - <<'NODE'
const assert = require("node:assert/strict");
const fixtures = require("./quality-fixtures");

assert.equal(fixtures.buildGreeting("Ada").message, "Welcome, Ada!");
assert.equal(
  fixtures.countCompleted([{ complete: true }, { complete: false }]),
  1,
);
console.log("Remediated behavior verified.");
NODE
```

Push the temporary branch and wait for **CodeQL - Code Quality / Analyze**. The
two findings should no longer be present in that branch's result. Finding
detection is deterministic CodeQL analysis, but an Autofix patch is
AI-generated and can vary or be unavailable; review it against the properties
above rather than expecting identical formatting.
