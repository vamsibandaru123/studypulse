"""SQL-based insights and charts for StudyPulse."""
import matplotlib

matplotlib.use("Agg")  # saves charts to files, no window needed
import matplotlib.pyplot as plt

from db import run_query

CHARTS_DIR = "charts"


def print_table(cols, rows):
    if not rows:
        print("  (no data yet)")
        return
    widths = [max(len(str(c)), *(len(str(r[i])) for r in rows)) for i, c in enumerate(cols)]
    print("  " + " | ".join(str(c).ljust(w) for c, w in zip(cols, widths)))
    print("  " + "-+-".join("-" * w for w in widths))
    for row in rows:
        print("  " + " | ".join(str(v).ljust(w) for v, w in zip(row, widths)))


def hours_per_subject():
    return run_query(
        """
        SELECT subject, ROUND(SUM(hours_studied), 1) AS total_hours
        FROM study_log
        GROUP BY subject
        ORDER BY total_hours DESC
        """
    )


def average_marks_per_subject():
    return run_query(
        """
        SELECT subject, ROUND(AVG(marks), 1) AS avg_marks
        FROM test_scores
        GROUP BY subject
        ORDER BY avg_marks ASC
        """
    )


def best_study_day():
    # strftime('%w') gives day of week: 0 = Sunday ... 6 = Saturday
    return run_query(
        """
        SELECT CASE strftime('%w', log_date)
                 WHEN '0' THEN 'Sunday'    WHEN '1' THEN 'Monday'
                 WHEN '2' THEN 'Tuesday'   WHEN '3' THEN 'Wednesday'
                 WHEN '4' THEN 'Thursday'  WHEN '5' THEN 'Friday'
                 ELSE 'Saturday'
               END AS weekday,
               ROUND(AVG(hours_studied), 2) AS avg_hours
        FROM study_log
        GROUP BY strftime('%w', log_date)
        ORDER BY avg_hours DESC
        """
    )


def sleep_vs_marks():
    """Compare average marks on weeks with low vs. high sleep (joined with SQL)."""
    return run_query(
        """
        SELECT CASE WHEN w.avg_sleep >= 7 THEN 'Sleep >= 7h' ELSE 'Sleep < 7h' END AS sleep_group,
               ROUND(AVG(t.marks), 1) AS avg_marks,
               COUNT(*) AS tests
        FROM test_scores t
        JOIN (
            SELECT subject, strftime('%Y-%W', log_date) AS week, AVG(sleep_hours) AS avg_sleep
            FROM study_log
            GROUP BY subject, week
        ) w
          ON w.subject = t.subject AND w.week = strftime('%Y-%W', t.test_date)
        GROUP BY sleep_group
        """
    )


def show_insights():
    print("\n[1] Total study hours per subject")
    print_table(*hours_per_subject())
    print("\n[2] Average marks per subject (weakest first)")
    print_table(*average_marks_per_subject())
    print("\n[3] Average study hours by weekday")
    print_table(*best_study_day())
    print("\n[4] Does sleep affect marks?")
    print_table(*sleep_vs_marks())


def make_charts():
    import os

    os.makedirs(CHARTS_DIR, exist_ok=True)

    cols, rows = hours_per_subject()
    if rows:
        plt.figure(figsize=(7, 4))
        plt.bar([r[0] for r in rows], [r[1] for r in rows], color="#4C78A8")
        plt.title("Total Study Hours per Subject")
        plt.ylabel("Hours")
        plt.tight_layout()
        plt.savefig(f"{CHARTS_DIR}/hours_per_subject.png", dpi=120)
        plt.close()

    cols, rows = run_query(
        "SELECT test_date, ROUND(AVG(marks), 1) FROM test_scores GROUP BY test_date ORDER BY test_date"
    )
    if rows:
        plt.figure(figsize=(7, 4))
        plt.plot([r[0] for r in rows], [r[1] for r in rows], marker="o", color="#F58518")
        plt.title("Average Marks Over Time")
        plt.ylabel("Marks")
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        plt.savefig(f"{CHARTS_DIR}/marks_over_time.png", dpi=120)
        plt.close()

    print(f"Charts saved in the '{CHARTS_DIR}/' folder.")
