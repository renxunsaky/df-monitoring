-- Create the metrics table
CREATE TABLE IF NOT EXISTS metrics (
    id SERIAL PRIMARY KEY,
    metric_name VARCHAR(100) NOT NULL,
    value FLOAT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert some sample data
INSERT INTO metrics (metric_name, value, timestamp) VALUES
    ('cpu_usage', 45.2, NOW() - INTERVAL '5 minutes'),
    ('memory_usage', 72.8, NOW() - INTERVAL '5 minutes'),
    ('disk_usage', 68.3, NOW() - INTERVAL '5 minutes'),
    ('network_latency', 12.5, NOW() - INTERVAL '10 minutes'),
    ('cpu_usage', 48.6, NOW() - INTERVAL '15 minutes'),
    ('memory_usage', 75.1, NOW() - INTERVAL '15 minutes'),
    ('disk_usage', 68.5, NOW() - INTERVAL '20 minutes'),
    ('network_latency', 14.2, NOW() - INTERVAL '25 minutes'); 