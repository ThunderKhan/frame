# Pull Request

## Summary

Describe what this pull request changes.

<!--
Keep this concise.
Example:
Adds duplicate transaction protection to the stateful risk engine.
-->

---

## Why

Explain why this change is needed.

<!--
What problem does this solve?
What behavior is being improved?
-->

---

## Type of change

Check the relevant option:

- [ ] Feature
- [ ] Bug fix
- [ ] Refactor
- [ ] Test
- [ ] Documentation
- [ ] Performance improvement
- [ ] Security hardening
- [ ] Frontend / UI
- [ ] ML / evaluation
- [ ] CI / tooling

---

## Affected areas

Check all that apply:

- [ ] Risk engine
- [ ] Graph processing
- [ ] Temporal features
- [ ] Model inference
- [ ] Risk policy
- [ ] Evidence layer
- [ ] FastAPI backend
- [ ] Frontend
- [ ] Synthetic data generation
- [ ] Benchmark / evaluation
- [ ] Documentation
- [ ] CI / repository tooling

---

## Behavior impact

Does this change affect:

- [ ] Model behavior
- [ ] Risk-score calculation
- [ ] ALLOW / REVIEW / BLOCK policy behavior
- [ ] API behavior
- [ ] Graph state
- [ ] Temporal state
- [ ] Analyst evidence
- [ ] Benchmark results
- [ ] UI behavior
- [ ] No runtime behavior

If applicable, explain:

<!--
Describe exactly what changed.
-->

---

## Testing

Describe how this change was tested.

Examples:

```text
pytest
ruff check src tests scripts
npm run lint
npm run build
```

Test results:

```text
Paste relevant results here.
```

---

## Evaluation changes

If this pull request changes model features, thresholds, synthetic data generation, or evaluation logic, include:

- benchmark configuration
- random seed
- dataset size
- thresholds
- before/after metrics

If not applicable, write:

```text
Not applicable.
```

---

## Claims and evidence

If this change affects README claims, benchmark results, screenshots, or demo messaging, confirm:

- [ ] Synthetic results are clearly identified as synthetic
- [ ] No production-performance claims are introduced without evidence
- [ ] Observed network evidence is not described as causal model attribution
- [ ] No single signal is claimed to independently cause a risk score

---

## Security and privacy

Confirm:

- [ ] No secrets or credentials are included
- [ ] No real payment or customer data is included
- [ ] No untrusted serialized model artifacts are introduced
- [ ] API changes have considered validation and state safety

---

## Screenshots

If this is a frontend or visualization change, add screenshots or recordings here.

<!--
Drag and drop images into the pull request.
-->

---

## Checklist

- [ ] The change is focused and does not include unrelated modifications
- [ ] Tests pass
- [ ] Lint passes
- [ ] Frontend builds successfully where applicable
- [ ] Documentation is updated where necessary
- [ ] New behavior is tested where practical
- [ ] Commit messages are clear and focused
