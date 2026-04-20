# Industry Demo: Real-Time Ride-Sharing Analytics with Snowpipe Streaming + Kafka
### Reference Claude model:- https://claude.ai/share/1f1dbc0d-321a-431e-80bb-0d59b3ca5a31
---

## Problem Statement

**Company:** RideFlow (fictional ride-hailing platform like Uber/Ola)

**Challenge:** RideFlow processes 2M+ ride events per hour across 50 cities. Their data team uses nightly batch ETL into Snowflake, creating a **6–12 hour data lag**. This means:

- Surge pricing decisions are based on stale demand signals
- Driver fraud (GPS spoofing) is detected hours after it happens
- City operations teams can't react to real-time demand spikes
- SLA breaches on ride completion are reported next day, not live

**Goal:** Replace batch ETL with **Snowpipe Streaming via Kafka** to achieve sub-60-second data freshness in Snowflake — enabling live dashboards, real-time fraud signals, and dynamic surge pricing.

---

## Demo Scenario

> Stream live ride lifecycle events (ride request → driver assignment → pickup → dropoff → payment) from Kafka into Snowflake in real time, power a live Snowflake Dynamic Table for city-level demand heatmaps, and detect GPS anomalies within seconds of occurrence.

---

## Tech Stack

| Component | Technology |
|---|---|
| Event producer | Python (Faker + confluent-kafka) |
| Message broker | Apache Kafka (Docker / Confluent Cloud) |
| Connector | Snowflake Kafka Connector v2.x (Streaming mode) |
| Data platform | Snowflake (Enterprise or above) |
| Analytics | Snowflake Dynamic Tables + Streamlit in Snowflake |

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│  SOURCES                                                            │
│  ┌──────────────┐ ┌────────────────┐ ┌──────────────┐ ┌──────────┐ │
│  │  Ride App    │ │  Payment Svc   │ │  Ops Svc     │ │  IoT     │ │
│  │  GPS events  │ │  Fare, surge   │ │  Dispatch,   │ │  Vehicle │ │
│  │  Driver/Rider│ │  Promo events  │ │  ETA, cancel │ │  health  │ │
│  └──────┬───────┘ └───────┬────────┘ └──────┬───────┘ └────┬─────┘ │
└─────────┼─────────────────┼────────────────┼──────────────┼────────┘
          │                 │                │              │
┌─────────▼─────────────────▼────────────────▼──────────────▼────────┐
│  TRANSPORT — Apache Kafka Cluster                                   │
│  ┌──────────────┐ ┌────────────────┐ ┌──────────────┐ ┌──────────┐ │
│  │rides.events  │ │payments.txns   │ │ops.dispatch  │ │iot.telem │ │
│  │12 partitions │ │6 partitions    │ │6 partitions  │ │8 partitn │ │
│  └──────────────┘ └────────────────┘ └──────────────┘ └──────────┘ │
└─────────────────────────────────┬───────────────────────────────────┘
                                  │
┌─────────────────────────────────▼───────────────────────────────────┐
│  INGESTION — Snowflake Kafka Connector (Snowpipe Streaming mode)    │
│  • Channel per partition (ordered, exactly-once)                    │
│  • Schema evolution (auto DDL on new columns)                       │
│  • Sub-second latency — no staging files                            │
└─────────────────────────────────┬───────────────────────────────────┘
                                  │
┌─────────────────────────────────▼───────────────────────────────────┐
│  ANALYTICS — Snowflake                                              │
│  ┌──────────────┐ ┌────────────────┐ ┌────────────────┐ ┌────────┐  │
│  │Raw event     │ │Dynamic Tables  │ │Materialized    │ │Dashbrd │  │
│  │tables        │ │(30s refresh)   │ │Views           │ │        │  │
│  └──────────────┘ └────────────────┘ └────────────────┘ └────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Step-by-Step Setup & Execution

### Step 1 — Prerequisites

```bash
# Install tools
pip install confluent-kafka faker snowflake-connector-python

# Docker: Start Kafka locally
docker run -d --name kafka \
  -e KAFKA_ZOOKEEPER_CONNECT=zookeeper:2181 \
  -e KAFKA_ADVERTISED_LISTENERS=PLAINTEXT://localhost:9092 \
  -e KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR=1 \
  -p 9092:9092 confluentinc/cp-kafka:7.5.0
```

---

### Step 2 — Create Kafka Topics

```bash
kafka-topics.sh --create \
  --bootstrap-server localhost:9092 \
  --topic rides.events \
  --partitions 12 \
  --replication-factor 1

kafka-topics.sh --create \
  --bootstrap-server localhost:9092 \
  --topic payments.txns \
  --partitions 6 \
  --replication-factor 1
```

---

### Step 3 — Snowflake Setup

```sql
-- Create database and schema
CREATE DATABASE rideflow_streaming;
CREATE SCHEMA rideflow_streaming.live;

-- Create landing tables (Snowpipe Streaming writes here)
CREATE OR REPLACE TABLE rideflow_streaming.live.ride_events (
  record_metadata  VARIANT,
  record_content   VARIANT,
  ingested_at      TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

CREATE OR REPLACE TABLE rideflow_streaming.live.payment_events (
  record_metadata  VARIANT,
  record_content   VARIANT,
  ingested_at      TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- Create role and user for Kafka connector
CREATE ROLE kafka_streaming_role;
GRANT USAGE ON DATABASE rideflow_streaming TO ROLE kafka_streaming_role;
GRANT USAGE ON SCHEMA rideflow_streaming.live TO ROLE kafka_streaming_role;
GRANT INSERT, SELECT ON ALL TABLES IN SCHEMA rideflow_streaming.live TO ROLE kafka_streaming_role;

CREATE USER kafka_connector_user
  PASSWORD = 'SecurePass@123'
  DEFAULT_ROLE = kafka_streaming_role;
GRANT ROLE kafka_streaming_role TO USER kafka_connector_user;
```

---

### Step 4 — Configure Snowflake Kafka Connector

Create `snowflake-connector.properties`:

```properties
name=snowflake-streaming-demo
connector.class=com.snowflake.kafka.connector.SnowflakeSinkConnector
tasks.max=4

# Kafka topics to consume
topics=rides.events,payments.txns

# ⭐ KEY: Enable Snowpipe Streaming (not legacy Snowpipe)
snowflake.ingestion.method=SNOWPIPE_STREAMING

# Snowflake connection
snowflake.url.name=<your_account>.snowflakecomputing.com
snowflake.user.name=kafka_connector_user
snowflake.private.key=<base64_private_key>
snowflake.database.name=rideflow_streaming
snowflake.schema.name=live

# Topic-to-table mapping
snowflake.topic2table.map=rides.events:ride_events,payments.txns:payment_events

# Converter — use JSON without schema for speed
key.converter=org.apache.kafka.connect.storage.StringConverter
value.converter=com.snowflake.kafka.connector.records.SnowflakeJsonConverter

# Streaming buffer settings (tune for latency vs throughput)
buffer.count.records=1000
buffer.flush.time=10
buffer.size.bytes=5000000

# Schema evolution: auto-add columns on new fields
snowflake.enable.schematization=TRUE
```

Deploy the connector:

```bash
curl -X POST http://localhost:8083/connectors \
  -H "Content-Type: application/json" \
  -d @snowflake-connector.properties
```

---

### Step 5 — Python Event Producer

```python
# producer.py — Simulates real RideFlow event stream
import json, time, uuid, random
from datetime import datetime
from faker import Faker
from confluent_kafka import Producer

fake = Faker('en_IN')
producer = Producer({'bootstrap.servers': 'localhost:9092'})

CITIES = ['Mumbai', 'Delhi', 'Bangalore', 'Hyderabad', 'Chennai']
EVENT_TYPES = ['ride_requested', 'driver_assigned', 'pickup', 'dropoff', 'cancelled']

def generate_ride_event():
    city = random.choice(CITIES)
    return {
        "event_id":           str(uuid.uuid4()),
        "event_type":         random.choice(EVENT_TYPES),
        "ride_id":            str(uuid.uuid4()),
        "driver_id":          f"DRV-{random.randint(1000,9999)}",
        "rider_id":           f"RDR-{random.randint(10000,99999)}",
        "city":               city,
        "lat":                round(random.uniform(12.9, 28.7), 6),
        "lng":                round(random.uniform(77.1, 80.3), 6),
        "surge_multiplier":   round(random.uniform(1.0, 3.5), 2),
        "event_ts":           datetime.utcnow().isoformat()
    }

def generate_payment_event(ride_id):
    return {
        "payment_id":   str(uuid.uuid4()),
        "ride_id":      ride_id,
        "amount_inr":   round(random.uniform(50, 800), 2),
        "method":       random.choice(['UPI', 'Card', 'Wallet', 'Cash']),
        "status":       random.choice(['SUCCESS', 'FAILED', 'PENDING']),
        "gateway_lat":  round(random.uniform(10, 30), 6),
        "event_ts":     datetime.utcnow().isoformat()
    }

print("🚀 Streaming ride events to Kafka...")
while True:
    ride = generate_ride_event()
    producer.produce('rides.events',
                     key=ride['ride_id'],
                     value=json.dumps(ride))

    if ride['event_type'] == 'dropoff':
        payment = generate_payment_event(ride['ride_id'])
        producer.produce('payments.txns',
                         key=payment['ride_id'],
                         value=json.dumps(payment))

    producer.poll(0)
    time.sleep(0.05)  # ~20 events/sec
```

Run the producer:

```bash
python producer.py
```

---

### Step 6 — Real-Time Analytics in Snowflake

#### 6a. Flatten raw VARIANT into typed view

```sql
CREATE OR REPLACE VIEW rideflow_streaming.live.v_ride_events AS
SELECT
  record_content:event_id::STRING        AS event_id,
  record_content:event_type::STRING      AS event_type,
  record_content:ride_id::STRING         AS ride_id,
  record_content:driver_id::STRING       AS driver_id,
  record_content:city::STRING            AS city,
  record_content:lat::FLOAT              AS lat,
  record_content:lng::FLOAT             AS lng,
  record_content:surge_multiplier::FLOAT AS surge_multiplier,
  record_content:event_ts::TIMESTAMP_NTZ AS event_ts,
  ingested_at
FROM rideflow_streaming.live.ride_events;
```

#### 6b. Dynamic Table for live city demand (refreshes every 30 seconds)

```sql
CREATE OR REPLACE DYNAMIC TABLE rideflow_streaming.live.city_demand_live
  TARGET_LAG = '30 seconds'
  WAREHOUSE = 'RIDEFLOW_WH'
AS
SELECT
  city,
  event_type,
  COUNT(*)                         AS event_count,
  AVG(surge_multiplier)            AS avg_surge,
  MAX(surge_multiplier)            AS max_surge,
  COUNT(DISTINCT driver_id)        AS active_drivers,
  MAX(ingested_at)                 AS last_event_at,
  CURRENT_TIMESTAMP()              AS snapshot_at
FROM rideflow_streaming.live.v_ride_events
WHERE ingested_at >= DATEADD('minute', -5, CURRENT_TIMESTAMP())
GROUP BY city, event_type;
```

#### 6c. GPS Fraud Detection — driver spoofing alert

```sql
-- Drivers moving impossibly fast between consecutive GPS pings
CREATE OR REPLACE VIEW rideflow_streaming.live.v_gps_anomalies AS
WITH consecutive AS (
  SELECT
    driver_id,
    event_ts,
    lat, lng,
    LAG(lat)      OVER (PARTITION BY driver_id ORDER BY event_ts) AS prev_lat,
    LAG(lng)      OVER (PARTITION BY driver_id ORDER BY event_ts) AS prev_lng,
    LAG(event_ts) OVER (PARTITION BY driver_id ORDER BY event_ts) AS prev_ts
  FROM rideflow_streaming.live.v_ride_events
  WHERE ingested_at >= DATEADD('minute', -10, CURRENT_TIMESTAMP())
),
speeds AS (
  SELECT *,
    HAVERSINE(prev_lat, prev_lng, lat, lng)
      / NULLIF(DATEDIFF('second', prev_ts, event_ts), 0) * 3600
    AS speed_kmh
  FROM consecutive
  WHERE prev_ts IS NOT NULL
)
SELECT driver_id, event_ts, lat, lng, ROUND(speed_kmh, 1) AS speed_kmh
FROM speeds
WHERE speed_kmh > 200  -- physically impossible for a car
ORDER BY event_ts DESC;
```

#### 6d. Verify data freshness

```sql
-- See how quickly events land in Snowflake after Kafka production
SELECT
  AVG(DATEDIFF('second', event_ts, ingested_at)) AS avg_latency_seconds,
  MAX(DATEDIFF('second', event_ts, ingested_at)) AS max_latency_seconds,
  MIN(DATEDIFF('second', event_ts, ingested_at)) AS min_latency_seconds,
  COUNT(*)                                        AS total_events,
  MAX(ingested_at)                                AS most_recent_ingest
FROM rideflow_streaming.live.v_ride_events
WHERE ingested_at >= DATEADD('minute', -5, CURRENT_TIMESTAMP());
```

---

## Expected Output

### Latency check (Step 6d)

```
avg_latency_seconds | max_latency_seconds | min_latency_seconds | total_events | most_recent_ingest
--------------------+---------------------+---------------------+--------------+--------------------
                  8 |                  22 |                   2 |        6,241 | 2024-01-15 14:32:01
```

### City demand table (Step 6b)

```
city        | event_type      | event_count | avg_surge | active_drivers | last_event_at
------------+-----------------+-------------+-----------+----------------+--------------------
Mumbai      | ride_requested  |         832 |      2.31 |            341 | 2024-01-15 14:31:58
Delhi       | driver_assigned |         711 |      1.87 |            299 | 2024-01-15 14:31:55
Bangalore   | pickup          |         543 |      1.42 |            218 | 2024-01-15 14:31:59
```

### GPS anomaly detection

```
driver_id  | event_ts                    | lat      | lng      | speed_kmh
-----------+-----------------------------+----------+----------+-----------
DRV-4821   | 2024-01-15 14:31:44.000000 | 28.61234 | 77.20981 |    1847.3
DRV-7103   | 2024-01-15 14:31:37.000000 | 12.97441 | 77.59832 |     432.1
```

---

## Key Differentiators vs Legacy Snowpipe

| Capability | Legacy Snowpipe | Snowpipe Streaming |
|---|---|---|
| Latency | 1–5 minutes | **< 10 seconds** |
| Mechanism | Staged files (S3/GCS) | Direct row insert via SDK |
| Ordering guarantee | None | Per-channel ordering |
| Schema evolution | Manual DDL | Auto-detected |
| Cost model | File processing fees | Row-based ingestion |
| Exactly-once | No | Yes (per channel) |

---

## Demo Talking Points

The three strongest moments to highlight during the live demo are:

1. **Live latency query** — Run the latency query live and show single-digit second lag from Kafka production to Snowflake arrival.

2. **Schema evolution** — Add a new field to the producer JSON (e.g. `vehicle_type`) and watch Snowflake auto-create the column with no downtime or manual DDL.

3. **Real-time fraud detection** — Trigger a simulated GPS spoof (set `speed_kmh` artificially high) and show the fraud view catching it within one refresh cycle — under 30 seconds end to end.

---

*Demo prepared for: Snowflake Snowpipe Streaming with Apache Kafka | RideFlow Use Case*
