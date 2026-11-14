
from src.health_analysis import (
    calculate_health_summary,
    analyze_health_trends
)

print("\n===== HEALTH SUMMARY =====")
summary = calculate_health_summary("AST001")

for key, value in summary.items():
    print(f"{key}: {value}")


print("\n===== HEALTH TREND ANALYSIS =====")
result = analyze_health_trends("AST001")

print("\nStatus:", result["Status"])
print("\nAlerts:")

for alert in result["Alerts"]:
    print("-", alert)

print("\nLatest Record:")
print(result["Latest Record"])
