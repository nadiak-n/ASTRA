
import pandas as pd

from src.data_loader import load_health_data


def calculate_health_summary(astronaut_id=None):
    """Calculate average health measurements."""

    df = load_health_data()

    if astronaut_id:
        df = df[df["astronaut_id"] == astronaut_id]

    if df.empty:
        return {}

    summary = {
        "Average Heart Rate": round(df["heart_rate"].mean(), 2),
        "Average SpO2": round(df["spo2"].mean(), 2),
        "Average Temperature": round(df["temperature"].mean(), 2),
        "Average Sleep Hours": round(df["sleep_hours"].mean(), 2),
        "Average Mood Score": round(df["mood_score"].mean(), 2),
        "Average Activity Level": round(df["activity_level"].mean(), 2)
    }

    return summary


def analyze_health_trends(astronaut_id=None):
    """Compare the latest health record with the astronaut's personal baseline."""

    df = load_health_data()

    if astronaut_id:
        df = df[df["astronaut_id"] == astronaut_id]

    if df.empty:
        return {
            "Latest Record": None,
            "Personal Baseline": None,
            "Alerts": ["No health data available."],
            "Status": "No Data"
        }

    df = df.sort_values("timestamp")

    latest = df.iloc[-1]

    # Use previous records to calculate the personal baseline
    previous_records = df.iloc[:-1]

    if previous_records.empty:
        baseline = df.iloc[0].copy()
    else:
        baseline = previous_records.mean(numeric_only=True)

    alerts = []

    # Heart rate
    if latest["heart_rate"] > baseline["heart_rate"] * 1.10:
        alerts.append("Heart rate is higher than personal baseline.")

    # Oxygen saturation
    if latest["spo2"] < baseline["spo2"] - 1:
        alerts.append("SpO2 is lower than personal baseline.")

    # Body temperature
    if latest["temperature"] > baseline["temperature"] + 0.3:
        alerts.append("Temperature is higher than personal baseline.")

    # Sleep duration
    if latest["sleep_hours"] < baseline["sleep_hours"] - 1:
        alerts.append("Sleep duration is lower than personal baseline.")

    # Mood
    if latest["mood_score"] < baseline["mood_score"] - 1:
        alerts.append("Mood score is lower than personal baseline.")

    # Activity
    if latest["activity_level"] < baseline["activity_level"] - 1.5:
        alerts.append("Activity level is lower than personal baseline.")

    status = "Warning" if alerts else "Stable"

    return {
        "Latest Record": latest,
        "Personal Baseline": baseline,
        "Alerts": alerts,
        "Status": status
    }


def generate_health_recommendations(astronaut_id=None):
    """Generate recommendations based on detected health changes."""

    analysis = analyze_health_trends(astronaut_id)

    alerts = analysis["Alerts"]

    recommendations = []

    recommendation_rules = {
        "Heart rate is higher than personal baseline.": (
            "Heart Rate",
            "Consider taking a rest and repeating the heart rate measurement. "
            "Notify the medical officer if the elevation persists."
        ),

        "SpO2 is lower than personal baseline.": (
            "Oxygen Level",
            "Repeat the oxygen saturation measurement and check the sensor. "
            "Notify the medical officer if the reading remains low."
        ),

        "Temperature is higher than personal baseline.": (
            "Temperature",
            "Recheck body temperature and monitor for additional symptoms. "
            "Notify the medical officer if the elevation persists."
        ),

        "Sleep duration is lower than personal baseline.": (
            "Sleep",
            "Consider improving the sleep schedule and allowing more time for rest."
        ),

        "Mood score is lower than personal baseline.": (
            "Mood",
            "Consider a mental wellness check-in and relaxation activities."
        ),

        "Activity level is lower than personal baseline.": (
            "Activity",
            "Review the activity schedule and consider suitable movement "
            "if the astronaut feels well."
        )
    }

    for alert in alerts:
        if alert in recommendation_rules:
            category, recommendation = recommendation_rules[alert]

            recommendations.append({
                "Category": category,
                "Alert": alert,
                "Recommendation": recommendation
            })

    if not recommendations:
        recommendations.append({
            "Category": "General",
            "Alert": "No unusual changes detected.",
            "Recommendation": (
                "Continue routine health monitoring and maintain "
                "regular sleep, activity, and wellness habits."
            )
        })

    return recommendations

