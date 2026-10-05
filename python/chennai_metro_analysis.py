"""
Chennai Metro Ridership & Station Analytics
Senior Data Analyst portfolio project

Run:
    pip install -r requirements.txt
    python chennai_metro_analysis.py

The script:
1. Loads all supplied CMRL datasets.
2. Performs data-quality checks.
3. Performs descriptive EDA.
4. Produces business KPIs and station segmentation.
5. Calculates correlations between station attributes and predicted ridership.
6. Produces visualizations under outputs/.
7. Exports cleaned/derived tables for downstream SQL/BI use.
"""

from pathlib import Path
import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

BASE = Path(__file__).resolve().parent
DATA = BASE / "data"
OUT = BASE / "outputs"
OUT.mkdir(exist_ok=True)

# -----------------------------
# 1. LOAD DATA
# -----------------------------
pred = pd.read_csv(DATA / "chennai_metro_ridership_predictions.csv")
stations = pd.read_csv(DATA / "chennai_metro_stations.csv")
catchment = pd.read_csv(DATA / "chennai_station_catchment_features.csv")
hourly = pd.read_csv(DATA / "cmrl_hourly_ridership.csv")
station_summary = pd.read_csv(DATA / "cmrl_station_summary.csv")
station_daily = pd.read_csv(DATA / "cmrl_stationflow_daily.csv")
ticket = pd.read_csv(DATA / "cmrl_ticket_mix.csv")
monthly = pd.read_csv(DATA / "cmrl_system_monthly.csv")

xlsx = pd.ExcelFile(DATA / "cmrl_ridership_data.xlsx")
daily_xlsx = pd.read_excel(DATA / "cmrl_ridership_data.xlsx", sheet_name="Daily summary")
station_xlsx = pd.read_excel(DATA / "cmrl_ridership_data.xlsx", sheet_name="Station x date")
target_xlsx = pd.read_excel(DATA / "cmrl_ridership_data.xlsx", sheet_name="Model target")

# Parse dates
for df, col in [(hourly, "date"), (station_daily, "date"), (ticket, "date"),
                (daily_xlsx, "date")]:
    if col in df.columns:
        df[col] = pd.to_datetime(df[col], errors="coerce")

monthly["Month"] = pd.to_datetime(monthly["Month"], format="%b-%y", errors="coerce")
for c in monthly.columns[1:]:
    monthly[c] = (
        monthly[c].astype(str)
        .str.replace(",", "", regex=False)
        .str.replace("%", "", regex=False)
    )
    monthly[c] = pd.to_numeric(monthly[c], errors="coerce")

# -----------------------------
# 2. DATA QUALITY
# -----------------------------
quality = []
for name, df in {
    "predictions": pred,
    "stations": stations,
    "catchment": catchment,
    "hourly": hourly,
    "station_summary": station_summary,
    "station_daily": station_daily,
    "ticket_mix": ticket,
    "system_monthly": monthly,
}.items():
    quality.append({
        "dataset": name,
        "rows": len(df),
        "columns": len(df.columns),
        "duplicate_rows": int(df.duplicated().sum()),
        "missing_cells": int(df.isna().sum().sum()),
        "missing_pct": round(df.isna().mean().mean() * 100, 3),
    })
quality_df = pd.DataFrame(quality)
quality_df.to_csv(OUT / "data_quality_summary.csv", index=False)

# -----------------------------
# 3. CORE KPI TABLES
# -----------------------------
daily = (
    station_daily.groupby("date", as_index=False)
    .agg(total_boardings=("boardings", "sum"),
         stations_reporting=("cmrl_name", "nunique"))
)
daily["day_name"] = daily["date"].dt.day_name()
daily["day_num"] = daily["date"].dt.dayofweek

dow = (
    daily.groupby(["day_num", "day_name"], as_index=False)
    .agg(avg_boardings=("total_boardings", "mean"),
         min_boardings=("total_boardings", "min"),
         max_boardings=("total_boardings", "max"),
         days=("date", "nunique"))
    .sort_values("day_num")
)

station_kpi = (
    station_daily.groupby("cmrl_name", as_index=False)
    .agg(avg_daily_boardings=("boardings", "mean"),
         median_daily_boardings=("boardings", "median"),
         max_daily_boardings=("boardings", "max"),
         min_daily_boardings=("boardings", "min"),
         boardings_sd=("boardings", "std"),
         days_observed=("date", "nunique"))
    .sort_values("avg_daily_boardings", ascending=False)
)

monthly["mom_growth_pct"] = monthly["Total Passenger Flow"].pct_change() * 100

# Ticket mix
ticket_numeric = ticket.copy()
for c in ticket_numeric.columns[1:]:
    ticket_numeric[c] = pd.to_numeric(ticket_numeric[c], errors="coerce")

ticket_total = ticket_numeric["totalTickets"].sum()
ticket_channels = {
    "NCMC card": ticket_numeric["noOfNCMCcard"].sum(),
    "Total QR": ticket_numeric["noOfTotal_QR"].sum(),
    "Paper QR": ticket_numeric["noOfPaperQR"].sum(),
    "Mobile QR": ticket_numeric["noOfMobileQR"].sum(),
    "Paytm QR": ticket_numeric["noOfPaytmQR"].sum(),
    "WhatsApp QR": ticket_numeric["noOfWhatsAppQR"].sum(),
    "PhonePe QR": ticket_numeric["noOfPhonePeQR"].sum(),
    "Rapido QR": ticket_numeric["noOfRapidoQR"].sum(),
    "ONDC QR": ticket_numeric["noOfONDCQR"].sum(),
    "Uber QR": ticket_numeric["noOfUberQR"].sum(),
    "CUMTA QR": ticket_numeric["noOfCumtaQR"].sum(),
}
ticket_kpi = (
    pd.DataFrame({"channel": list(ticket_channels.keys()),
                  "tickets": list(ticket_channels.values())})
    .assign(share_pct=lambda x: x["tickets"] / ticket_total * 100)
    .sort_values("tickets", ascending=False)
)
ticket_kpi.to_csv(OUT / "ticket_channel_mix.csv", index=False)

# Prediction + station features
pred_rank = pred[
    ["station_id", "name", "Line", "phase", "Layout", "prediction", "lower",
     "upper", "population", "population_2030", "poi_total", "bus_stops_500m",
     "parking_area_m2", "dist_cbd_km", "dist_nearest_centre_km",
     "is_interchange", "is_terminal"]
].copy()
pred_rank["prediction_interval_width"] = pred_rank["upper"] - pred_rank["lower"]
pred_rank["forecast_rank"] = pred_rank["prediction"].rank(method="min", ascending=False).astype(int)
pred_rank = pred_rank.sort_values("prediction", ascending=False)
pred_rank.to_csv(OUT / "station_prediction_rank.csv", index=False)

# Correlations with prediction
numeric_pred = pred.select_dtypes(include=np.number)
corr = numeric_pred.corr(numeric_only=True)["prediction"].drop("prediction").sort_values(ascending=False)
corr_df = corr.reset_index()
corr_df.columns = ["feature", "correlation_with_prediction"]
corr_df.to_csv(OUT / "prediction_feature_correlations.csv", index=False)

# -----------------------------
# 4. STATION SEGMENTATION
# -----------------------------
p75 = pred["prediction"].quantile(0.75)
p25 = pred["prediction"].quantile(0.25)

def segment(x):
    if x >= p75:
        return "High demand"
    if x <= p25:
        return "Low demand"
    return "Mid demand"

seg = pred[["station_id", "name", "Line", "prediction", "poi_total",
            "population", "bus_stops_500m", "is_interchange"]].copy()
seg["demand_segment"] = seg["prediction"].apply(segment)

# A simple planning-priority score: normalized demand + accessibility + activity.
for c in ["prediction", "bus_stops_500m", "poi_total"]:
    mn, mx = seg[c].min(), seg[c].max()
    seg[c + "_norm"] = (seg[c] - mn) / (mx - mn) if mx != mn else 0
seg["planning_priority_score"] = (
    0.60 * seg["prediction_norm"] +
    0.25 * seg["bus_stops_500m_norm"] +
    0.15 * seg["poi_total_norm"]
) * 100
seg = seg.sort_values("planning_priority_score", ascending=False)
seg.to_csv(OUT / "station_planning_priority.csv", index=False)

# -----------------------------
# 5. PRINT EXECUTIVE FINDINGS
# -----------------------------
print("\n=== CHENNAI METRO RIDERSHIP ANALYSIS ===")
print(f"Stations in prediction dataset: {len(pred):,}")
print(f"Observed station-flow rows: {len(station_daily):,}")
print(f"Observed daily system records: {daily['date'].nunique():,}")
print(f"Average observed daily boardings: {daily['total_boardings'].mean():,.0f}")
print(f"Peak observed daily boardings: {daily['total_boardings'].max():,.0f}")
print(f"Average predicted station boardings: {pred['prediction'].mean():,.0f}")
print("\nTop 10 predicted stations:")
print(pred_rank.head(10)[["name", "Line", "prediction", "lower", "upper"]].to_string(index=False))

print("\nAverage observed boardings by day:")
print(dow[["day_name", "avg_boardings"]].to_string(index=False))

print("\nMonthly system flow: latest 6 months")
print(monthly[["Month", "Total Passenger Flow", "mom_growth_pct"]].tail(6).to_string(index=False))

print("\nTicket mix:")
print(ticket_kpi.to_string(index=False))

print("\nStrongest numeric associations with predicted ridership:")
print(corr_df.head(10).to_string(index=False))

# -----------------------------
# 6. VISUALIZATIONS
# -----------------------------
sns.set_theme(style="whitegrid")

# 6.1 Monthly passenger flow
plt.figure(figsize=(12, 6))
plt.plot(monthly["Month"], monthly["Total Passenger Flow"], marker="o")
plt.title("CMRL Monthly Passenger Flow")
plt.xlabel("Month")
plt.ylabel("Passenger flow")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(OUT / "01_monthly_passenger_flow.png", dpi=180)
plt.close()

# 6.2 Daily system ridership
plt.figure(figsize=(12, 6))
plt.plot(daily["date"], daily["total_boardings"], marker="o")
plt.title("Observed Daily Metro Boardings")
plt.xlabel("Date")
plt.ylabel("Boardings")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(OUT / "02_daily_boardings.png", dpi=180)
plt.close()

# 6.3 Day-of-week comparison
plt.figure(figsize=(10, 5))
plt.bar(dow["day_name"], dow["avg_boardings"])
plt.title("Average System Boardings by Day of Week")
plt.xlabel("Day")
plt.ylabel("Average boardings")
plt.xticks(rotation=30)
plt.tight_layout()
plt.savefig(OUT / "03_day_of_week.png", dpi=180)
plt.close()

# 6.4 Hourly profile
hourly_profile = hourly.groupby("hour", as_index=False)["boardings"].mean()
plt.figure(figsize=(12, 6))
plt.plot(hourly_profile["hour"], hourly_profile["boardings"], marker="o")
plt.title("Average Hourly Ridership Profile")
plt.xlabel("Hour")
plt.ylabel("Average boardings")
plt.xticks(range(0, 24))
plt.tight_layout()
plt.savefig(OUT / "04_hourly_profile.png", dpi=180)
plt.close()

# 6.5 Top predicted stations
top20 = pred_rank.head(20).sort_values("prediction")
plt.figure(figsize=(11, 8))
plt.barh(top20["name"], top20["prediction"])
plt.title("Top 20 Stations by Predicted Daily Boardings")
plt.xlabel("Predicted boardings")
plt.tight_layout()
plt.savefig(OUT / "05_top20_predictions.png", dpi=180)
plt.close()

# 6.6 Prediction vs bus connectivity
plt.figure(figsize=(8, 6))
plt.scatter(pred["bus_stops_500m"], pred["prediction"], alpha=0.75)
plt.title("Predicted Ridership vs Bus Stops within 500m")
plt.xlabel("Bus stops within 500m")
plt.ylabel("Predicted boardings")
plt.tight_layout()
plt.savefig(OUT / "06_bus_connectivity_vs_prediction.png", dpi=180)
plt.close()

# 6.7 Prediction vs POI intensity
plt.figure(figsize=(8, 6))
plt.scatter(pred["poi_total"], pred["prediction"], alpha=0.75)
plt.title("Predicted Ridership vs POI Count")
plt.xlabel("POI count")
plt.ylabel("Predicted boardings")
plt.tight_layout()
plt.savefig(OUT / "07_poi_vs_prediction.png", dpi=180)
plt.close()

# 6.8 Ticket mix
plot_ticket = ticket_kpi.head(10).sort_values("share_pct")
plt.figure(figsize=(10, 6))
plt.barh(plot_ticket["channel"], plot_ticket["share_pct"])
plt.title("Top Ticket / Access Channels")
plt.xlabel("Share of observed tickets (%)")
plt.tight_layout()
plt.savefig(OUT / "08_ticket_mix.png", dpi=180)
plt.close()

# 6.9 Prediction distribution
plt.figure(figsize=(9, 5))
plt.hist(pred["prediction"], bins=20)
plt.title("Distribution of Station Ridership Predictions")
plt.xlabel("Predicted daily boardings")
plt.ylabel("Number of stations")
plt.tight_layout()
plt.savefig(OUT / "09_prediction_distribution.png", dpi=180)
plt.close()

# 6.10 Correlation heatmap for selected business features
features = [
    "prediction", "population", "population_2030", "poi_total",
    "bus_stops_500m", "parking_area_m2", "dist_cbd_km",
    "dist_nearest_centre_km", "metro_betweenness", "metro_closeness"
]
features = [f for f in features if f in pred.columns]
plt.figure(figsize=(10, 7))
sns.heatmap(pred[features].corr(), annot=True, fmt=".2f", cmap="coolwarm", center=0)
plt.title("Correlation Matrix: Ridership and Station Context")
plt.tight_layout()
plt.savefig(OUT / "10_correlation_heatmap.png", dpi=180)
plt.close()

print(f"\nOutputs written to: {OUT}")
