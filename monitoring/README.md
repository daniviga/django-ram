# Asset telemetry monitoring

> [!CAUTION]
> This is a PoC, not suitable for real world due to lack of any authentication and security

## Pre-requisites

- Python 3.12
- Podman (or Docker)

## Architecture

The `dispatcher.py` script collects data (`cab` commands) from a CommandStation and sends it a MQTT broker. 

The command being monitored is `<l cab reg speedByte functMap>` which is returned by the `<t cab speed dir>` throttle command. See the [DCC-EX command reference](https://dcc-ex.com/reference/software/command-summary-consolidated.html#t-cab-speed-dir-set-cab-loco-speed).

`mosquitto` is the MQTT broker.

The `handler.py` script subscribes to the MQTT broker and saves relevant data to the Timescale database.

Data is finally save into a Timescale hypertable.

## How to run

### Deploy Timescale

```bash
$ podman run -d -p 5432:5432 -v $(pwd)/data:/var/lib/postgresql/data -e "POSTGRES_USER=dccmonitor" -e "POSTGRES_PASSWORD=dccmonitor" --name timescale timescale/timescaledb:latest-pg17
```
> [!IMPORTANT]
> A volume should be created for persistent data

Tables and hypertables are automatically created by the `handler.py` script

### Deploy Mosquitto

```bash
$ podman run --userns=keep-id -d -p 1883:1883 -v $(pwd)/config/mosquitto.conf:/mosquitto/config/mosquitto.conf --name mosquitto eclipse-mosquitto:2.0
```

### Run the dispatcher and the handler

```bash
$ python dispatcher.py
```

```bash
$ python handler.py
```

## Debug data in Timescale

### Create a 10 secs aggregated data table

```sql
CREATE MATERIALIZED VIEW telemetry_10secs
WITH (timescaledb.continuous) AS
SELECT 
    time_bucket('10 seconds', timestamp) AS bucket,
    cab,
    ROUND(CAST(AVG(speed) AS NUMERIC), 1) AS avg_speed,
    MIN(speed) AS min_speed,
    MAX(speed) AS max_speed
FROM telemetry
GROUP BY bucket, cab;
```

and set the update policy:

```sql
SELECT add_continuous_aggregate_policy(
    'telemetry_10secs',
    start_offset => INTERVAL '1 hour',  -- Go back 1 hour for updates
    end_offset   => INTERVAL '1 minute', -- Keep the latest 5 min fresh
    schedule_interval => INTERVAL '1 minute' -- Run every minute
);

```

### Running statistics from 10 seconds table

```sql
WITH speed_durations AS (
    SELECT 
        cab,
        avg_speed,
        max_speed,
        bucket AS start_time,
        LEAD(bucket) OVER (
            PARTITION BY cab ORDER BY bucket
        ) AS end_time,
        LEAD(bucket) OVER (PARTITION BY cab ORDER BY bucket) - bucket AS duration
    FROM telemetry_10secs
)
SELECT * FROM speed_durations WHERE end_time IS NOT NULL;
```

and filtered by `cab` number, via a function

```sql
CREATE FUNCTION get_speed_durations(cab_id INT) 
RETURNS TABLE (
    cab INT, 
    speed DOUBLE PRECISION, 
    dir TEXT, 
    start_time TIMESTAMPTZ, 
    end_time TIMESTAMPTZ, 
    duration INTERVAL
) 
AS $$
WITH speed_durations AS (
    SELECT 
        cab,
        avg_speed,
        max_speed,
        bucket AS start_time,
        LEAD(bucket) OVER (
            PARTITION BY cab ORDER BY bucket
        ) AS end_time,
        LEAD(bucket) OVER (PARTITION BY cab ORDER BY bucket) - bucket AS duration
    FROM telemetry_10secs
)
SELECT * FROM speed_durations WHERE end_time IS NOT NULL AND cab = cab_id;
$$ LANGUAGE sql;

-- Refresh data
CALL refresh_continuous_aggregate('telemetry_10secs', NULL, NULL);
SELECT * FROM get_speed_durations(1);
```
