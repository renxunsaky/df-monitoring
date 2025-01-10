-- name: get_last_hour_metrics
SELECT metric_name, value, timestamp 
FROM metrics 
WHERE timestamp > NOW() - INTERVAL '1 hour';

-- name: get_daily_average
SELECT 
    metric_name,
    AVG(value) as average_value,
    DATE(timestamp) as metric_date
FROM metrics 
WHERE timestamp > NOW() - INTERVAL '24 hours'
GROUP BY metric_name, DATE(timestamp);

-- name: get_metric_by_name
SELECT metric_name, value, timestamp 
FROM metrics 
WHERE metric_name = %s 
ORDER BY timestamp DESC 
LIMIT 100; 