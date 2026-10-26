"""StudyPulse - Streamlit web dashboard.

Run:  streamlit run app.py
"""
from datetime import date

import pandas as pd
import streamlit as st

import analysis
import db
import model
import seed_data

st.set_page_config(page_title="StudyPulse", page_icon="📚", layout="wide")
db.init_db()


def query_df(sql, params=()):
    """Run a SQL query and return a pandas DataFrame."""
    cols, rows = db.run_query(sql, params)
    return pd.DataFrame(rows, columns=cols)


def has_data():
    return not query_df("SELECT 1 FROM study_log LIMIT 1").empty


# ---------------------------------------------------------------- Dashboard
def page_dashboard():
    st.title("📚 StudyPulse")
    st.caption("Your study habits, analyzed with SQL and predicted with machine learning.")

    if not has_data():
        st.info("No data yet. Add entries from the sidebar, or load sample data.")
        return

    totals = query_df(
        """
        SELECT ROUND(SUM(hours_studied), 1) AS hours,
               ROUND(AVG(sleep_hours), 1)   AS sleep,
               COUNT(DISTINCT log_date)     AS days
        FROM study_log
        """
    )
    avg_marks = query_df("SELECT ROUND(AVG(marks), 1) AS m FROM test_scores")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total study hours", totals["hours"][0])
    c2.metric("Avg sleep (hours)", totals["sleep"][0])
    c3.metric("Days logged", int(totals["days"][0]))
    marks_value = avg_marks["m"][0]
    c4.metric("Avg test marks", "-" if pd.isna(marks_value) else marks_value)

    left, right = st.columns(2)

    with left:
        st.subheader("Study hours per subject")
        cols, rows = analysis.hours_per_subject()
        df = pd.DataFrame(rows, columns=cols).set_index("subject")
        st.bar_chart(df)

    with right:
        st.subheader("Average marks over time")
        df = query_df(
            "SELECT test_date, ROUND(AVG(marks), 1) AS avg_marks "
            "FROM test_scores GROUP BY test_date ORDER BY test_date"
        )
        if df.empty:
            st.info("Add test scores to see this chart.")
        else:
            st.line_chart(df.set_index("test_date"))

    left, right = st.columns(2)

    with left:
        st.subheader("Weakest subjects (by avg marks)")
        cols, rows = analysis.average_marks_per_subject()
        st.dataframe(pd.DataFrame(rows, columns=cols), hide_index=True)

    with right:
        st.subheader("Average study hours by weekday")
        cols, rows = analysis.best_study_day()
        st.dataframe(pd.DataFrame(rows, columns=cols), hide_index=True)

    st.subheader("Does sleep affect marks?")
    cols, rows = analysis.sleep_vs_marks()
    if rows:
        st.dataframe(pd.DataFrame(rows, columns=cols), hide_index=True)
    else:
        st.info("Not enough overlapping logs and tests yet.")

    with st.expander("Show the SQL behind 'Does sleep affect marks?'"):
        st.code(
            "SELECT CASE WHEN w.avg_sleep >= 7 THEN 'Sleep >= 7h' ELSE 'Sleep < 7h' END AS sleep_group,\n"
            "       ROUND(AVG(t.marks), 1) AS avg_marks, COUNT(*) AS tests\n"
            "FROM test_scores t\n"
            "JOIN (SELECT subject, strftime('%Y-%W', log_date) AS week, AVG(sleep_hours) AS avg_sleep\n"
            "      FROM study_log GROUP BY subject, week) w\n"
            "  ON w.subject = t.subject AND w.week = strftime('%Y-%W', t.test_date)\n"
            "GROUP BY sleep_group;",
            language="sql",
        )


# ----------------------------------------------------------------- Add data
def page_add_data():
    st.title("➕ Add Data")
    tab_log, tab_score = st.tabs(["Study log", "Test score"])

    with tab_log:
        with st.form("log_form", clear_on_submit=True):
            log_date = st.date_input("Date", value=date.today(), key="log_date")
            subject = st.text_input("Subject", key="log_subject")
            hours = st.number_input("Hours studied", 0.0, 24.0, 2.0, 0.5, key="log_hours")
            sleep = st.number_input("Hours slept", 0.0, 24.0, 7.0, 0.5, key="log_sleep")
            if st.form_submit_button("Save study log"):
                if not subject.strip():
                    st.warning("Please enter a subject.")
                else:
                    db.add_study_log(log_date.isoformat(), subject, hours, sleep)
                    st.success("Study log saved.")

    with tab_score:
        with st.form("score_form", clear_on_submit=True):
            test_date = st.date_input("Test date", value=date.today(), key="score_date")
            subject = st.text_input("Subject", key="score_subject")
            marks = st.number_input("Marks (out of 100)", 0.0, 100.0, 60.0, 1.0, key="score_marks")
            if st.form_submit_button("Save test score"):
                if not subject.strip():
                    st.warning("Please enter a subject.")
                else:
                    db.add_test_score(test_date.isoformat(), subject, marks)
                    st.success("Test score saved.")


# ------------------------------------------------------------------ Predict
def page_predict():
    st.title("🔮 Predict My Score")
    st.write(
        "A Linear Regression model learns from your past tests and the study and "
        "sleep hours in the 7 days before each test."
    )

    trained, r2, n = model.train_model()
    if trained is None:
        st.warning(f"Need at least 5 tests with study logs (found {n}). Add more data first.")
        return

    c1, c2 = st.columns(2)
    hours = c1.slider("Average study hours per day", 0.0, 10.0, 3.0, 0.5)
    sleep = c2.slider("Average sleep hours per night", 3.0, 10.0, 7.0, 0.5)

    X = pd.DataFrame([[hours, sleep]], columns=["avg_hours", "avg_sleep"])
    pred = max(0.0, min(100.0, float(trained.predict(X)[0])))

    st.metric("Predicted marks", f"{pred:.1f} / 100")
    st.caption(f"Model trained on {n} tests. R² score: {r2:.2f} (closer to 1 = better fit).")


# ------------------------------------------------------------------ Sidebar
def sidebar():
    st.sidebar.title("StudyPulse")
    page = st.sidebar.radio("Go to", ["Dashboard", "Add Data", "Predict Score"])

    st.sidebar.divider()
    if not has_data():
        st.sidebar.caption("Try it quickly with synthetic demo data:")
        if st.sidebar.button("Load sample data"):
            seed_data.seed()
            st.rerun()
    return page


PAGES = {
    "Dashboard": page_dashboard,
    "Add Data": page_add_data,
    "Predict Score": page_predict,
}

PAGES[sidebar()]()
