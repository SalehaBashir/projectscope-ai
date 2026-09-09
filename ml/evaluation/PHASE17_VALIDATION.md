\# Phase 17 - Hybrid Estimation Validation



\## Status



Phase 17 hybrid estimation implementation is complete.



\## Estimation Components



\- Deterministic rule-based estimation

\- ML effort prediction

\- LLM advisory estimation

\- Reconciliation layer

\- Confidence scoring

\- Estimator versioning



\## Reconciliation Policy



The deterministic estimation is the primary baseline.



ML contributes only when model performance is acceptable.



LLM estimation is advisory and contributes only when structured

data quality is sufficient.



Missing or low-confidence sources are excluded rather than blindly

averaged.



\## ML Historical Validation



Dataset: synthetic\_projects.csv



Samples: 800



MAE: 65.70 hours



RMSE: 84.71 hours



\## Real Feedback Validation



The real feedback export was attempted using the backend database.



Result:



No projects with feedback found.



Therefore, no real feedback dataset was available for historical

Rule + ML + LLM reconciliation validation.



\## Validation Limitation



The current historical dataset contains aggregate ML features and

actual\_hours, but does not contain the task-level base\_hours required

to reproduce the existing deterministic rule estimate.



The system therefore does not fabricate a historical rule estimate.



The current validation confirms the ML component and documents the

limitation for full hybrid historical validation.



\## Estimator Version



hybrid-v1.0

