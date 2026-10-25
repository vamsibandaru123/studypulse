"""Generate realistic SAMPLE data so you can try StudyPulse immediately.

Run:  python seed_data.py
Note: this is synthetic data. Test marks are generated from the previous week's
study and sleep hours (plus random noise), so the AI model has a pattern to learn.
Replace it with your own logs for real insights.
"""
import random
from collections import defaultdict
from datetime import date, timedelta

import db

SUBJECTS = ["Python", "Maths", "DBMS", "Machine Learning", "Operating Systems"]
random.seed(42)


def seed(days=120):
    db.init_db()
    start = date.today() - timedelta(days=days)
    week_logs = defaultdict(list)  # subject -> [(hours, sleep), ...] for the current week

    for i in range(days):
        day = start + timedelta(days=i)
        for subject in random.sample(SUBJECTS, 3):
            hours = round(random.uniform(0.5, 4.5), 1)
            sleep = round(random.uniform(5, 9), 1)
            db.add_study_log(day.isoformat(), subject, hours, sleep)
            week_logs[subject].append((hours, sleep))

        if i % 7 == 6:  # weekly test
            subject = random.choice(SUBJECTS)
            logs = week_logs[subject]
            if logs:
                avg_h = sum(h for h, _ in logs) / len(logs)
                avg_s = sum(s for _, s in logs) / len(logs)
                marks = 25 + 11 * avg_h + 3 * avg_s + random.uniform(-5, 5)
                db.add_test_score(day.isoformat(), subject, round(min(100, max(0, marks)), 1))
            week_logs.clear()
    print(f"Added sample data for {days} days.")


if __name__ == "__main__":
    seed()
