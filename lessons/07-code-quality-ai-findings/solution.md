# Lesson 07 — AI findings reference remediation

The exact AI suggestions can vary. Review generated changes against these intended properties rather than expecting identical wording or formatting.

## Grammar and spelling

The registration message should use correct subject-verb agreement and spelling:

```javascript
function buildRegistrationMessage(attendeeName) {
  return `${attendeeName}, your registration was successfully saved.`;
}
```

## Missing workshop

`findWorkshopById` should return an explicit missing value when no ID matches. `Array.prototype.find` communicates that behavior directly.

## Caller-owned attendee data

`normalizeAttendees` should create normalized copies before sorting them. It must not reorder the caller's array or rewrite caller-owned objects.

## Independent asynchronous work

`loadWorkshopDetails` should start independent requests together with `Promise.all`. This preserves result order and propagates failures while avoiding unnecessary serialization.

## Review checklist

- Run `node --check ai-findings-fixtures.js`.
- Add behavior tests for missing IDs and input immutability.
- Confirm concurrency is safe for the real service's rate limits and ordering requirements.
- Review user-facing wording with product or localization owners when appropriate.
- Merge remediation only when you want the corresponding AI findings to disappear.
