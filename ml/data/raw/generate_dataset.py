import csv
import random

random.seed(42)

ROLES = ["Backend Developer", "Frontend Developer", "QA Engineer", "DevOps Engineer", "UI/UX Designer"]


def generate_project():
    num_features = random.randint(3, 15)
    num_tasks = num_features * random.randint(3, 7)
    num_roles = random.randint(2, 5)
    has_payment = random.choice([0, 1])
    has_admin = random.choice([0, 1])
    has_mobile = random.choice([0, 1])
    has_realtime = random.choice([0, 1])
    num_integrations = random.randint(0, 5)
    complexity_score = random.uniform(20, 90)

    # Base formula for "true" hours, then add noise (simulates real-world variance)
    base_hours = (
        num_tasks * 6
        + has_payment * 40
        + has_admin * 35
        + has_mobile * 60
        + has_realtime * 30
        + num_integrations * 15
        + complexity_score * 3
    )
    noise = random.gauss(0, base_hours * 0.15)  # 15% noise
    actual_hours = max(20, base_hours + noise)

    return {
        "num_features": num_features,
        "num_tasks": num_tasks,
        "num_roles": num_roles,
        "has_payment": has_payment,
        "has_admin": has_admin,
        "has_mobile": has_mobile,
        "has_realtime": has_realtime,
        "num_integrations": num_integrations,
        "complexity_score": round(complexity_score, 1),
        "actual_hours": round(actual_hours, 1),
    }


def main():
    rows = [generate_project() for _ in range(800)]

    fieldnames = list(rows[0].keys())
    with open("synthetic_projects.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Generated {len(rows)} synthetic project records -> synthetic_projects.csv")


if __name__ == "__main__":
    main()