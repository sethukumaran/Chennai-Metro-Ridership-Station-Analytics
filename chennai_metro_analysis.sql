-- Chennai Metro Ridership & Station Analytics

-- ============================================================
-- 1. DAILY SYSTEM KPIs
-- ============================================================

SELECT
    date,
    SUM(boardings) AS total_boardings,
    COUNT(DISTINCT cmrl_name) AS stations_reporting
FROM cmrl_stationflow_daily
WHERE is_partial = FALSE
GROUP BY date
ORDER BY date;


-- ============================================================
-- 2. STATION RANKING
-- ============================================================

SELECT
    cmrl_name,
    ROUND(AVG(boardings), 0) AS avg_daily_boardings,
    ROUND(MAX(boardings), 0) AS peak_daily_boardings,
    ROUND(STDDEV_SAMP(boardings), 0) AS boardings_sd,
    COUNT(*) AS observed_days
FROM cmrl_stationflow_daily
WHERE is_partial = FALSE
GROUP BY cmrl_name
ORDER BY avg_daily_boardings DESC;


-- ============================================================
-- 3. DAY-OF-WEEK DEMAND
-- ============================================================

WITH daily AS (
    SELECT
        date,
        SUM(boardings) AS total_boardings
    FROM cmrl_stationflow_daily
    WHERE is_partial = FALSE
    GROUP BY date
)
SELECT
    TO_CHAR(date, 'Day') AS day_name,
    EXTRACT(ISODOW FROM date) AS day_num,
    ROUND(AVG(total_boardings), 0) AS avg_boardings,
    MIN(total_boardings) AS min_boardings,
    MAX(total_boardings) AS max_boardings
FROM daily
GROUP BY day_name, day_num
ORDER BY day_num;


-- ============================================================
-- 4. WEEKDAY VS WEEKEND
-- ============================================================

WITH daily AS (
    SELECT
        date,
        SUM(boardings) AS total_boardings
    FROM cmrl_stationflow_daily
    WHERE is_partial = FALSE
    GROUP BY date
)
SELECT
    CASE
        WHEN EXTRACT(ISODOW FROM date) IN (6,7) THEN 'Weekend'
        ELSE 'Weekday'
    END AS day_type,
    ROUND(AVG(total_boardings), 0) AS avg_boardings
FROM daily
GROUP BY day_type;


-- ============================================================
-- 5. HOURLY RIDERSHIP PROFILE
-- ============================================================

SELECT
    hour,
    ROUND(AVG(boardings), 0) AS avg_boardings,
    MAX(boardings) AS peak_observed_boardings
FROM cmrl_hourly_ridership
WHERE is_partial = FALSE
GROUP BY hour
ORDER BY hour;


-- ============================================================
-- 6. PEAK HOURS
-- ============================================================

WITH hourly_avg AS (
    SELECT
        hour,
        AVG(boardings) AS avg_boardings
    FROM cmrl_hourly_ridership
    WHERE is_partial = FALSE
    GROUP BY hour
)
SELECT
    hour,
    ROUND(avg_boardings, 0) AS avg_boardings,
    RANK() OVER (ORDER BY avg_boardings DESC) AS demand_rank
FROM hourly_avg
ORDER BY demand_rank;


-- ============================================================
-- 7. MONTHLY TREND + MOM GROWTH
-- ============================================================

WITH m AS (
    SELECT
        "Month" AS month,
        "Total Passenger Flow" AS passenger_flow
    FROM cmrl_system_monthly
)
SELECT
    month,
    passenger_flow,
    ROUND(
        100.0 * (
            passenger_flow
            / NULLIF(LAG(passenger_flow) OVER (ORDER BY month), 0) - 1
        ), 2
    ) AS mom_growth_pct
FROM m
ORDER BY month;


-- ============================================================
-- 8. HIGHEST / LOWEST MONTH
-- ============================================================

(
    SELECT 'Highest month' AS metric, "Month" AS month,
           "Total Passenger Flow" AS passenger_flow
    FROM cmrl_system_monthly
    ORDER BY "Total Passenger Flow" DESC
    LIMIT 1
)
UNION ALL
(
    SELECT 'Lowest month' AS metric, "Month" AS month,
           "Total Passenger Flow" AS passenger_flow
    FROM cmrl_system_monthly
    ORDER BY "Total Passenger Flow" ASC
    LIMIT 1
);


-- ============================================================
-- 9. TICKET MIX
-- ============================================================

WITH totals AS (
    SELECT SUM("totalTickets") AS total_tickets
    FROM cmrl_ticket_mix
)
SELECT
    'NCMC' AS channel,
    SUM("noOfNCMCcard") AS tickets,
    ROUND(100.0 * SUM("noOfNCMCcard") / MAX(total_tickets), 2) AS share_pct
FROM cmrl_ticket_mix, totals
UNION ALL
SELECT
    'Total QR',
    SUM("noOfTotal_QR"),
    ROUND(100.0 * SUM("noOfTotal_QR") / MAX(total_tickets), 2)
FROM cmrl_ticket_mix, totals
UNION ALL
SELECT
    'Paper QR',
    SUM("noOfPaperQR"),
    ROUND(100.0 * SUM("noOfPaperQR") / MAX(total_tickets), 2)
FROM cmrl_ticket_mix, totals
ORDER BY tickets DESC;


-- ============================================================
-- 10. TOP DIGITAL PARTNER CHANNELS
-- ============================================================

WITH channels AS (
    SELECT 'Rapido' AS channel, SUM("noOfRapidoQR") AS tickets FROM cmrl_ticket_mix
    UNION ALL SELECT 'ONDC', SUM("noOfONDCQR") FROM cmrl_ticket_mix
    UNION ALL SELECT 'Uber', SUM("noOfUberQR") FROM cmrl_ticket_mix
    UNION ALL SELECT 'WhatsApp', SUM("noOfWhatsAppQR") FROM cmrl_ticket_mix
    UNION ALL SELECT 'Paytm', SUM("noOfPaytmQR") FROM cmrl_ticket_mix
    UNION ALL SELECT 'PhonePe', SUM("noOfPhonePeQR") FROM cmrl_ticket_mix
)
SELECT *
FROM channels
ORDER BY tickets DESC;


-- ============================================================
-- 11. TOP PREDICTED STATIONS
-- ============================================================

SELECT
    name,
    "Line",
    prediction,
    lower,
    upper,
    population,
    poi_total,
    bus_stops_500m,
    is_interchange,
    is_terminal
FROM chennai_metro_ridership_predictions
ORDER BY prediction DESC
LIMIT 20;


-- ============================================================
-- 12. PREDICTION INTERVAL / FORECAST RISK
-- Wider interval = greater planning uncertainty.
-- ============================================================

SELECT
    name,
    prediction,
    lower,
    upper,
    ROUND(upper - lower, 0) AS interval_width,
    ROUND(100.0 * (upper - lower) / NULLIF(prediction,0), 1) AS interval_width_pct
FROM chennai_metro_ridership_predictions
ORDER BY interval_width_pct DESC;


-- ============================================================
-- 13. LINE-LEVEL PREDICTED DEMAND
-- ============================================================

SELECT
    "Line",
    COUNT(*) AS stations,
    ROUND(AVG(prediction), 0) AS avg_prediction,
    ROUND(SUM(prediction), 0) AS aggregate_prediction
FROM chennai_metro_ridership_predictions
GROUP BY "Line"
ORDER BY avg_prediction DESC;


-- ============================================================
-- 14. INTERCHANGE VS NON-INTERCHANGE
-- ============================================================

SELECT
    CASE WHEN is_interchange = 1 THEN 'Interchange' ELSE 'Non-interchange' END AS station_type,
    COUNT(*) AS stations,
    ROUND(AVG(prediction), 0) AS avg_prediction
FROM chennai_metro_ridership_predictions
GROUP BY station_type
ORDER BY avg_prediction DESC;


-- ============================================================
-- 15. ACCESSIBILITY / RIDERSHIP RELATIONSHIP
-- ============================================================

SELECT
    CORR(prediction, bus_stops_500m) AS corr_bus_connectivity,
    CORR(prediction, poi_total) AS corr_poi_intensity,
    CORR(prediction, population) AS corr_population,
    CORR(prediction, parking_area_m2) AS corr_parking,
    CORR(prediction, dist_cbd_km) AS corr_distance_cbd
FROM chennai_metro_ridership_predictions;


-- ============================================================
-- 16. STATIONS WITH HIGH DEMAND BUT WEAK BUS CONNECTIVITY
-- ============================================================

WITH ranked AS (
    SELECT
        *,
        NTILE(4) OVER (ORDER BY prediction DESC) AS demand_quartile,
        NTILE(4) OVER (ORDER BY bus_stops_500m ASC) AS bus_access_quartile
    FROM chennai_metro_ridership_predictions
)
SELECT
    name,
    prediction,
    bus_stops_500m,
    poi_total,
    is_interchange
FROM ranked
WHERE demand_quartile = 1
  AND bus_access_quartile = 1
ORDER BY prediction DESC;


-- ============================================================
-- 17. HIGH-PRIORITY STATIONS FOR LAST-MILE INVESTMENT
-- ============================================================

WITH x AS (
    SELECT *,
           PERCENT_RANK() OVER (ORDER BY prediction) AS demand_pct,
           PERCENT_RANK() OVER (ORDER BY bus_stops_500m) AS bus_pct,
           PERCENT_RANK() OVER (ORDER BY poi_total) AS poi_pct
    FROM chennai_metro_ridership_predictions
)
SELECT
    name,
    "Line",
    ROUND(prediction,0) AS predicted_boardings,
    bus_stops_500m,
    poi_total,
    ROUND(
        100 * (0.60*demand_pct + 0.25*bus_pct + 0.15*poi_pct), 1
    ) AS planning_priority_score
FROM x
ORDER BY planning_priority_score DESC
LIMIT 20;
