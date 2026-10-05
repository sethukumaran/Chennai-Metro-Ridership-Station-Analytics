# Chennai Metro Ridership & Station Analytics

## Executive summary

This project analyzes Chennai Metro Rail ridership, station-level demand, hourly travel patterns, ticket-channel mix, station catchment characteristics, and modelled future station demand.
The analysis is designed as a **senior data analyst portfolio project** rather than a simple EDA exercise. It combines:
- System-level ridership trends
- Station-level demand ranking
- Peak-hour and day-of-week analysis
- Ticket/payment channel adoption
- Station catchment and accessibility features
- Predicted ridership and prediction uncertainty
- Business-oriented station segmentation
- SQL analysis for repeatable KPI extraction
- Python EDA and visualization

## Dataset inventory

| Dataset | Purpose |
|---|---|
| `cmrl_system_monthly.csv` | Long-term monthly passenger-flow trend |
| `cmrl_stationflow_daily.csv` | Daily station boardings |
| `cmrl_hourly_ridership.csv` | Hourly system ridership profile |
| `cmrl_ticket_mix.csv` | Ticket/channel composition |
| `cmrl_station_summary.csv` | Station-level observed demand summary |
| `chennai_metro_ridership_predictions.csv` | Station catchment features + predicted ridership |
| `chennai_station_catchment_features.csv` | Catchment and urban-form features |
| `chennai_metro_stations.csv` | Station master / geography |
| `cmrl_ridership_data.xlsx` | Consolidated workbook with supporting sheets |

## Business questions

1. Which stations generate the highest observed and predicted demand?
2. When are the strongest demand periods?
3. How different is weekday demand from weekend demand?
4. Which stations may require additional first/last-mile connectivity?
5. Which catchment characteristics are most associated with predicted ridership?
6. How is the ticket ecosystem split between NCMC and QR channels?
7. Which stations have high demand but high forecast uncertainty?
8. Where should operations, feeder transport, parking, and commercial planning be prioritized?


# Key findings

## 1. Demand is concentrated in a relatively small set of stations

The prediction dataset contains **134 stations**. Predicted daily boardings average about **7,990 per station**, but the distribution is highly uneven.

The leading predicted stations are:

1. Puratchi Thalaivar Dr. M.G. Ramachandran Central — ~23,513
2. Thousand Lights — ~16,804
3. Chennai International Airport — ~15,163
4. Guindy — ~14,920
5. Adyar Junction — ~13,964
6. Greenways Road — ~13,722
7. Thirumangalam — ~13,640
8. Mandaveli — ~13,060
9. Thiruvanmiyur — ~12,909
10. Taramani — ~12,778

**Business implication:** network-wide averages hide substantial station-level concentration. Capacity planning should therefore be station-specific rather than applying the same staffing, feeder, parking, or retail assumptions to every station.

## 2. Central and high-activity locations dominate predicted demand

The strongest positive numeric associations with predicted station ridership are:

- Bus stops within 500m: ~0.67 correlation
- Office POIs: ~0.41
- Retail POIs: ~0.40
- Total POIs: ~0.39
- Parking area: ~0.37
- Metro closeness: ~0.36

Distance to the nearest centre is negatively associated with prediction (~-0.33).

**Business implication:** station demand appears strongly connected to multimodal accessibility and surrounding economic activity. Improving feeder-bus connectivity can be a meaningful demand-enablement lever, especially around high-potential stations.

> Correlation is an association, not proof of causality. These relationships should be validated with a proper predictive model and controlled experiments before investment decisions.

## 3. Weekdays materially outperform Sundays

Observed system boardings show a clear weekly pattern.

Approximate average daily boardings in the supplied daily station-flow data:

| Day | Avg. boardings |
|---|---:|
| Thursday | 379,205 |
| Tuesday | 378,768 |
| Monday | 376,875 |
| Wednesday | 352,212 |
| Friday | 338,860 |
| Saturday | 306,317 |
| Sunday | 164,719 |

Sunday demand is therefore substantially below the strongest weekday levels.

**Business implication:** staffing, train frequency, station retail, security, cleaning, and feeder services should use day-type schedules rather than one uniform daily operating model.

## 4. The strongest hourly demand occurs around the commute windows

The hourly data shows pronounced demand around:

- 07:00
- 08:00
- 16:00
- 17:00
- 18:00

The highest average hourly value in the supplied data occurs at **17:00**, followed by **07:00**.

**Business implication:** peak-period train frequency and platform management should focus on the morning and late-afternoon/evening peaks. Demand forecasting at hourly granularity can support dynamic staffing and service planning.

## 5. Long-term monthly passenger flow has grown, but with meaningful volatility

The historical monthly dataset ranges from roughly **6.72 million** passenger flow in Apr-2023 to a peak of about **10.47 million** in Jul-2025.

Recent observations also show volatility: for example, Mar-2026 was about 10.18 million, Apr-2026 about 8.98 million, May-2026 about 8.97 million, and Jun-2026 about 9.64 million.

**Business implication:** annual averages alone are not sufficient for capacity planning. Seasonality, holidays, disruptions, school calendars, events, and service changes should be incorporated into forecasting.

## 6. NCMC and QR are almost evenly split in the observed ticket mix

Across the supplied ticket-mix period:

- NCMC card: ~50.39%
- Total QR: ~49.61%

Within the observed channels, paper QR is also significant at about 21.24% of total tickets.

Digital ecosystem partners include Rapido, ONDC, Uber, WhatsApp, Paytm, and PhonePe.

**Business implication:** CMRL has a balanced card/QR ecosystem. There is an opportunity to shift appropriate use cases toward lower-friction digital journeys while maintaining accessibility for passengers who depend on physical or paper-based channels.

## 7. Forecast uncertainty is strategically important

The prediction dataset provides a lower and upper estimate for each station. The interval width differs substantially across stations.

This means a station with a high predicted value is not automatically a low-risk planning decision.

**Business implication:** investment prioritization should consider both:

- expected demand
- uncertainty around expected demand

For example, stations with high demand and narrow forecast intervals can be treated as more reliable planning anchors, while high-demand/wide-interval stations should receive additional validation or scenario analysis.


# Recommended business actions

## A. Create station-specific capacity tiers

Classify stations into:

- Tier 1 — high-demand / operationally critical
- Tier 2 — medium-demand / growth opportunities
- Tier 3 — lower-demand / optimization candidates

Use predicted demand, observed demand, peak-hour intensity, interchange status, and forecast uncertainty.

## B. Prioritize feeder connectivity

The relationship between predicted demand and bus stops within 500m is one of the strongest associations in the dataset.

Recommended action:

- identify high-demand stations with low bus connectivity
- prioritize feeder-bus routes
- assess walking access and interchange quality
- monitor station-to-feeder transfer conversion

## C. Build a peak-period operating model

Use the hourly profile to create:

- peak train-frequency scenarios
- staffing schedules
- platform crowding thresholds
- station security plans
- cleaning and maintenance windows outside peak periods

## D. Develop station catchment scorecards

Track each station on:

- population
- projected 2030 population
- office density
- retail activity
- POI intensity
- bus connectivity
- parking
- interchange position
- CBD/centre distance

This can become a Power BI station-performance dashboard.

## E. Monitor digital ticket adoption

Track monthly:

- NCMC share
- QR share
- paper QR share
- partner QR share
- channel growth rate
- repeat usage where available

The goal should not simply be "more digital"; it should be **lower friction and lower transaction cost while preserving passenger accessibility**.


# Suggested dashboard

A production Power BI dashboard could contain:

### Page 1 — Executive Overview
- Total passenger flow
- Average daily boardings
- Peak daily boardings
- Top 10 stations
- NCMC vs QR split
- Monthly trend

### Page 2 — Station Performance
- Station ranking
- Observed vs predicted demand
- Forecast interval
- Line / phase filters

### Page 3 — Demand Timing
- Hourly profile
- Weekday vs weekend
- Day-of-week trend
- Peak-hour KPI

### Page 4 — Catchment Analytics
- Population
- POIs
- Bus stops
- Parking
- Distance to CBD
- Predicted demand

### Page 5 — Digital Ticketing
- NCMC share
- QR share
- Partner breakdown
- Paper QR trend


# SQL analysis

`sql/chennai_metro_analysis.sql` contains reusable PostgreSQL queries for:

- daily KPIs
- station ranking
- weekday/weekend comparison
- hourly demand
- monthly MoM growth
- ticket mix
- digital partner channels
- line-level demand
- interchange analysis
- feature correlations
- high-demand/low-connectivity stations
- station planning priority



# Python analysis

`chennai_metro_analysis.py` performs:

### Data preparation
- CSV loading
- Excel sheet loading
- date parsing
- numeric cleaning
- data-quality checks

### EDA
- missing values
- duplicates
- descriptive statistics
- daily demand
- station demand
- day-of-week demand
- hourly demand
- monthly trend
- ticket mix

### Business analytics
- station ranking
- station segmentation
- prediction feature correlations
- forecast interval analysis
- planning-priority score

### Visualizations
The script produces 10 PNG charts in `outputs/`.


# Important analytical caveats

1. **Observed periods are limited** in some station/hourly datasets, so short-window metrics should not automatically be treated as annual seasonality.
2. **Predicted ridership is model output**, not observed actual ridership.
3. Correlation does not establish causation.
4. Some station names differ between CMRL operational data and canonical station datasets; a production pipeline should maintain a formal station-dimension mapping table.
5. Partial records should be excluded from KPIs unless the business definition explicitly requires them.
6. Forecast intervals should be considered during investment decisions rather than using the point prediction alone.

# Conclusion

The dataset supports a strong business narrative: **Chennai Metro demand is not uniform across the network; it is driven by station context, accessibility, economic activity, timing, and passenger behavior.**

The most actionable opportunity is to move from network-wide averages toward **station-level demand management**. High-demand stations should be evaluated alongside their feeder connectivity, catchment activity, interchange role, and forecast uncertainty.

From a senior analyst perspective, the next step would be to operationalize these findings into a station-performance data model and Power BI dashboard, then connect the model to continuously refreshed operational data. This would allow CMRL stakeholders to move from retrospective reporting toward demand forecasting, capacity planning, and targeted infrastructure decisions.

