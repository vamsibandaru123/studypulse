"""Simple AI part: predict test marks from study hours and sleep hours."""
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score

from db import get_connection

# Average the logs of the 7 days before each test, then join them with the test marks.
TRAINING_SQL = """
SELECT t.marks,
       AVG(s.hours_studied) AS avg_hours,
       AVG(s.sleep_hours)   AS avg_sleep
FROM test_scores t
JOIN study_log s
  ON s.subject = t.subject
 AND s.log_date BETWEEN date(t.test_date, '-7 day') AND t.test_date
GROUP BY t.id
"""


def load_training_data():
    with get_connection() as conn:
        return pd.read_sql_query(TRAINING_SQL, conn)


def train_model():
    df = load_training_data()
    if len(df) < 5:
        return None, None, len(df)
    X = df[["avg_hours", "avg_sleep"]]
    y = df["marks"]
    model = LinearRegression().fit(X, y)
    score = r2_score(y, model.predict(X))
    return model, score, len(df)


def predict_score(avg_hours, avg_sleep):
    model, r2, n = train_model()
    if model is None:
        print(f"Need at least 5 test records with study logs (found {n}).")
        return None
    X = pd.DataFrame([[avg_hours, avg_sleep]], columns=["avg_hours", "avg_sleep"])
    pred = max(0, min(100, float(model.predict(X)[0])))
    print(f"\nModel trained on {n} tests (R2 = {r2:.2f})")
    print(f"Study {avg_hours}h/day + sleep {avg_sleep}h/night -> predicted marks: {pred:.1f}/100")
    return pred
