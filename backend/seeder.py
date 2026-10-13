import os
import random
from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv
from sqlalchemy import func, select, text

from app.database import SessionLocal
from app.models import Booking, Facility, Role, Space, SpaceCategory, User
from app.security import hash_password

load_dotenv()
random.seed(42)  # same data on every run

# !!! must match the status values your booking service actually uses
STATUS_ACTIVE = "active"
STATUS_CANCELLED = "cancelled"

# ---------- reference data ----------
CATEGORIES = ["Desk", "Meeting room", "Focus booth", "Training room"]

FACILITIES = [
    "Screen", "Whiteboard", "Projector", "Video conferencing",
    "Standing desk", "Dual monitors", "Docking station",
    "Power outlets", "Air conditioning", "Sound insulation",
]

# (category, name prefix, count, capacity, facilities pool, how many to pick)
SPACE_PLAN = [
    ("Desk", "Desk A", 20, 1,
     ["Standing desk", "Dual monitors", "Docking station", "Power outlets"], (0, 3)),
    ("Meeting room", "Meeting Room B", 8, 6,
     ["Screen", "Whiteboard", "Projector", "Video conferencing", "Air conditioning"], (2, 4)),
    ("Focus booth", "Focus Booth C", 4, 1,
     ["Sound insulation", "Power outlets", "Air conditioning"], (1, 3)),
    ("Training room", "Training Room D", 3, 20,
     ["Projector", "Whiteboard", "Screen", "Video conferencing", "Air conditioning"], (3, 5)),
]
CAPACITY_VARIATION = {"Meeting room": [4, 6, 8, 10], "Training room": [15, 20, 30]}

# ---------- users ----------
FIRST = ["Emma", "Noah", "Sophie", "Liam", "Julia", "Daan", "Mila", "Lucas", "Tess",
         "Finn", "Lotte", "Sem", "Anna", "Bram", "Eva", "Jesse", "Nina", "Ruben",
         "Lisa", "Thijs", "Fleur", "Max", "Iris", "Sven", "Zoë"]
LAST = ["de Vries", "Jansen", "Bakker", "Visser", "Smit", "Meijer", "de Boer",
        "Mulder", "de Groot", "Bos", "Vos", "Peters", "Hendriks", "van Dijk"]

N_STUDENTS = 25
N_TEACHERS = 5
N_ADMINS = 1  # + demo admin

# ---------- bookings ----------
DAYS_BACK = 10
DAYS_FORWARD = 14
DAY_START_H, DAY_END_H = 8, 18
BOOKINGS_PER_SPACE_DAY = (0, 4)
CANCEL_CHANCE = 0.1


def get_or_create(db, model, **kw):
    obj = db.scalar(select(model).filter_by(**kw))
    if obj:
        return obj
    obj = model(**kw)
    db.add(obj)
    db.flush()
    return obj


def seed_roles(db):
    return {n: get_or_create(db, Role, name=n) for n in ("Student", "Teacher", "Admin")}


def seed_users(db, roles, password):
    pwd_hash = hash_password(password)  # hash once - bcrypt is slow
    accounts = [
        ("Demo Student", "student@deskin.test", "Student"),
        ("Demo Teacher", "teacher@deskin.test", "Teacher"),
        ("Demo Admin", "admin@deskin.test", "Admin"),
    ]
    names = [f"{f} {l}" for f in FIRST for l in LAST]
    random.shuffle(names)
    i = 0
    for role, count in (("Student", N_STUDENTS), ("Teacher", N_TEACHERS), ("Admin", N_ADMINS)):
        for n in range(1, count + 1):
            name = names[i]
            i += 1
            accounts.append((name, f"{role.lower()}{n}@deskin.test", role))

    created, users = 0, []
    for name, email, role in accounts:
        u = db.scalar(select(User).where(User.email == email))
        if not u:
            u = User(name=name, email=email, password_hash=pwd_hash, role_id=roles[role].id)
            db.add(u)
            db.flush()
            created += 1
        users.append(u)
    print(f"users: +{created} (total in list {len(users)})")
    return users


def seed_spaces(db):
    cats = {n: get_or_create(db, SpaceCategory, name=n) for n in CATEGORIES}
    facs = {n: get_or_create(db, Facility, name=n) for n in FACILITIES}

    created = 0
    spaces = []
    for cat, prefix, count, cap, pool, (lo, hi) in SPACE_PLAN:
        for n in range(1, count + 1):
            name = f"{prefix}{n}"
            sp = db.scalar(select(Space).where(Space.name == name))
            if not sp:
                capacity = random.choice(CAPACITY_VARIATION[cat]) if cat in CAPACITY_VARIATION else cap
                sp = Space(
                    name=name,
                    capacity=capacity,
                    category_id=cats[cat].id,
                    is_active=random.random() > 0.08,  # ~8% inactive
                )
                db.add(sp)
                db.flush()
                for f in random.sample(pool, random.randint(lo, min(hi, len(pool)))):
                    db.execute(
                        text("INSERT INTO space_facilities (space_id, facility_id) "
                             "VALUES (:s, :f) ON CONFLICT DO NOTHING"),
                        {"s": sp.id, "f": facs[f].id},
                    )
                created += 1
            spaces.append(sp)
    print(f"spaces: +{created}")
    return spaces


def seed_bookings(db, users, spaces):
    if db.scalar(select(func.count()).select_from(Booking)):
        print("bookings: already exist, skipping (clear the table to reseed)")
        return

    today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    total = 0
    for sp in spaces:
        if not sp.is_active:
            continue
        for d in range(-DAYS_BACK, DAYS_FORWARD + 1):
            day = today + timedelta(days=d)
            if day.weekday() >= 5:  # skip weekends
                continue
            # 30-minute slots so bookings never overlap
            free = [True] * ((DAY_END_H - DAY_START_H) * 2)
            for _ in range(random.randint(*BOOKINGS_PER_SPACE_DAY)):
                length = random.choice([2, 2, 3, 4, 6])  # 1h, 1.5h, 2h, 3h
                start = random.randint(0, len(free) - length)
                if not all(free[start:start + length]):
                    continue
                for k in range(start, start + length):
                    free[k] = False
                start_at = day + timedelta(hours=DAY_START_H, minutes=30 * start)
                end_at = start_at + timedelta(minutes=30 * length)
                db.add(Booking(
                    user_id=random.choice(users).id,
                    space_id=sp.id,
                    start_at=start_at,
                    end_at=end_at,
                    status=STATUS_CANCELLED if random.random() < CANCEL_CHANCE else STATUS_ACTIVE,
                ))
                total += 1
    print(f"bookings: +{total}")


def main():
    password = os.environ["DEMO_PASSWORD"]
    with SessionLocal() as db:
        roles = seed_roles(db)
        users = seed_users(db, roles, password)
        spaces = seed_spaces(db)
        seed_bookings(db, users, spaces)
        db.commit()
    print("done")


if __name__ == "__main__":
    main()