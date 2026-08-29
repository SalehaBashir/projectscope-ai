from sqlalchemy.orm import Session
from app.models.role import Role

FIXED_ROLES = [
    {"name": "Backend Developer", "hourly_rate": 15.0},
    {"name": "Frontend Developer", "hourly_rate": 14.0},
    {"name": "QA Engineer", "hourly_rate": 10.0},
    {"name": "DevOps Engineer", "hourly_rate": 18.0},
    {"name": "UI/UX Designer", "hourly_rate": 12.0},
    {"name": "Project Manager", "hourly_rate": 16.0},
]


def seed_roles(db: Session):
    existing = {r.name for r in db.query(Role).all()}
    created = []
    for role in FIXED_ROLES:
        if role["name"] not in existing:
            new_role = Role(name=role["name"], hourly_rate=role["hourly_rate"])
            db.add(new_role)
            created.append(new_role)
    db.commit()
    return created


def list_roles(db: Session):
    return db.query(Role).all()


def get_role_by_name(db: Session, name: str):
    return db.query(Role).filter(Role.name == name).first()