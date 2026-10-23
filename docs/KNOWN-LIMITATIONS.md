# Oracle validation limitations

## Approval-question types

The withdrawal contract requires `status=ask`, `reason=approval`, and a nonempty question string. The frozen checker instead converts the question value to text before checking whether it is empty. Consequently, JSON null, numbers, arrays, and objects can be accepted as a question.

A supplemental audit reproduced this with null, 42, an empty array, and an empty object on temporary copies of one passing saved withdrawal case. Every malformed value still received a primary pass. The experiment files and original UAT were not modified.

All saved `ask` submissions in both matrices were inspected: 22 in v6 and 11 in v7. Every recorded question was a nonempty string, so this type gap does not change the reported historical outcomes. The audit checks types and presence; it does not judge whether the question is truthful or useful.

Reproduce the diagnostic from the repository root:

```sh
python3 -E -s -B tools/audit_question_types.py
```

Exit zero means the diagnostic reproduced the documented frozen behavior and found no invalid types in the saved questions. It does not mean the oracle enforces strict question typing. The command works only on temporary local evidence copies, removes them afterward, and makes no model calls.

A future checker should enforce a nonempty string explicitly and add malformed-type negative controls. Such a checker must be separately versioned and distinguished from the frozen historical oracle. Its outcomes must not silently replace the original scores.
