# monitoring — Evidently

The "is the deployed model still healthy?" layer. A model accurate at launch
degrades as the world shifts; the dangerous failures are silent (no crash, just
quietly worse predictions). Monitoring surfaces them.

## What it detects

- **Data drift** — input feature distributions move away from training. Detected
  by comparing current serving data against a training reference (KS test etc.).
- **Prediction drift** — the model's output distribution shifts, catchable even
  without ground-truth labels.
- **Training/serving skew** — a feature computed at serving differs from what
  training saw. Closes the loop back to the feature store, which exists to
  prevent exactly this — monitoring is how you catch it when it happens anyway.

## The demo

`gen_current.py` builds a reference set (training distribution) and a current
set with deliberate drift on `clicks_7d` (shifted up) but not `click_rate_7d`
(stable). `drift_report.py` runs Evidently and should correctly flag clicks_7d
as drifted and click_rate_7d as not — proving the detection works.

## Why it matters

"I don't just deploy a model — I monitor it for drift and skew and alert when it
degrades." That operational loop is what separates a built platform from a run
one. In production this feeds alerting (drift over threshold -> page/retrain).

## Landscape

Evidently vs alternatives: whylogs/WhyLabs (profiling-based), Arize &
Fiddler (commercial observability platforms), NannyML (post-deployment
performance estimation). Evidently chosen: open-source, report-first, easy local.

## Running

```bash
pip install evidently
python -m monitoring.gen_current
python -m monitoring.drift_report      # writes drift_report.html
open monitoring/drift_report.html
```
