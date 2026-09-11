import pandas as pd

synthetic = pd.read_csv("ml/data/raw/synthetic_projects.csv")
real = pd.read_csv("ml/data/raw/real_feedback.csv")

combined = pd.concat([synthetic, real], ignore_index=True)

combined.to_csv(
    "ml/data/processed/projects_with_feedback.csv",
    index=False
)

print(f"Combined rows: {len(combined)}")
print("Saved: ml/data/processed/projects_with_feedback.csv")
