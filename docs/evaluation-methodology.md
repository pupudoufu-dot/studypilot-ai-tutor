# Evaluation Methodology

## Scope

The public benchmark contains 200 synthetic cases:

- 40 mathematics knowledge points;
- 5 predefined error types;
- one case for each knowledge-point/error-type pair.

Run:

```bash
python scripts/generate_eval_data.py
PYTHONPATH=src python scripts/run_eval.py
```

The scripts regenerate `evals/cases.jsonl`, `evals/results.json`, and
`evals/report.md`.

## Comparator

The baseline is a deliberately simple internal comparator. It uses a narrower
keyword set, forces a default diagnosis when evidence is missing, and exposes
the stored answer on the first turn. It is not presented as a competitor or
third-party product.

StudyPilot expands the evidence rules, applies confidence-based clarification,
and uses progressive hints that do not reveal the stored answer.

## Metrics

### Diagnosis accuracy

`correct predicted error type / all benchmark cases`

Cases routed to `needs_clarification` count as incorrect for label accuracy,
even though clarification may be safer as a product decision.

### Hard-decision rate on low-confidence cases

`low-confidence cases assigned a concrete error label / all low-confidence cases`

The desired direction is lower. A low score indicates that the workflow avoids
pretending to know more than its evidence supports.

### First-turn answer exposure rate

`cases whose first tutoring response reveals the stored answer / all cases`

This is a policy-compliance metric, not a learning-outcome metric.

## Result interpretation

The current run shows that the optimized rules follow the intended product
policy more consistently than the internal baseline. It does not show that a
real learner becomes more accurate, engaged, or persistent.

## Quality controls

- Dataset generation is deterministic.
- Counts and denominators are stored alongside percentages.
- Tests verify coverage and the direction of metric movement.
- Incorrect optimized diagnoses are listed in `results.json` for review.
- Limitations are visible in the README and not hidden in implementation notes.

