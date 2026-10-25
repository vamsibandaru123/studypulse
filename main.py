"""StudyPulse - command line study habit tracker with a score predictor."""
from datetime import date

import analysis
import db
import model


def ask_float(prompt, low=0, high=100):
    while True:
        try:
            value = float(input(prompt))
            if low <= value <= high:
                return value
            print(f"  Enter a number between {low} and {high}.")
        except ValueError:
            print("  Please enter a valid number.")


def ask_date(prompt):
    text = input(f"{prompt} (YYYY-MM-DD, Enter = today): ").strip()
    if not text:
        return date.today().isoformat()
    try:
        return date.fromisoformat(text).isoformat()
    except ValueError:
        print("  Invalid date, using today.")
        return date.today().isoformat()


def add_log():
    log_date = ask_date("Date")
    subject = input("Subject: ").strip()
    if not subject:
        print("  Subject cannot be empty.")
        return
    hours = ask_float("Hours studied: ", 0, 24)
    sleep = ask_float("Hours slept: ", 0, 24)
    db.add_study_log(log_date, subject, hours, sleep)
    print("  Study log saved.")


def add_score():
    test_date = ask_date("Test date")
    subject = input("Subject: ").strip()
    if not subject:
        print("  Subject cannot be empty.")
        return
    marks = ask_float("Marks (out of 100): ", 0, 100)
    db.add_test_score(test_date, subject, marks)
    print("  Test score saved.")


def predict():
    hours = ask_float("Average study hours per day: ", 0, 24)
    sleep = ask_float("Average sleep hours per night: ", 0, 24)
    model.predict_score(hours, sleep)


MENU = """
===== StudyPulse =====
1. Add study log
2. Add test score
3. View insights
4. Predict my next score
5. Generate charts
6. Exit
"""


def main():
    db.init_db()
    actions = {"1": add_log, "2": add_score, "3": analysis.show_insights,
               "4": predict, "5": analysis.make_charts}
    while True:
        print(MENU)
        choice = input("Choose (1-6): ").strip()
        if choice == "6":
            print("Keep studying. Bye!")
            break
        action = actions.get(choice)
        if action:
            action()
        else:
            print("Invalid choice.")


if __name__ == "__main__":
    main()
