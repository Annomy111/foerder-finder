#!/bin/bash
# EduFunds Monitoring Stack Setup Script
# Installs Prometheus + Grafana + Loki on OCI VM (130.61.76.199)
#
# Usage: bash monitoring_setup.sh

set -e

echo "======================================"
echo "EduFunds Monitoring Stack Setup"
echo "======================================"
echo ""

# Detect architecture
ARCH=$(uname -m)
if [[ "$ARCH" == "aarch64" || "$ARCH" == "arm64" ]]; then
    ARCH="arm64"
elif [[ "$ARCH" == "x86_64" ]]; then
    ARCH="amd64"
else
    echo "Unsupported architecture: $ARCH"
    exit 1
fi

echo "Detected architecture: $ARCH"
echo ""

# =============================================================================
# 1. Install Prometheus
# =============================================================================

echo "[1/5] Installing Prometheus..."

PROMETHEUS_VERSION="2.48.0"
PROMETHEUS_URL="https://github.com/prometheus/prometheus/releases/download/v${PROMETHEUS_VERSION}/prometheus-${PROMETHEUS_VERSION}.linux-${ARCH}.tar.gz"

cd /tmp
wget -q "$PROMETHEUS_URL" -O prometheus.tar.gz
tar xzf prometheus.tar.gz
sudo mv prometheus-${PROMETHEUS_VERSION}.linux-${ARCH} /opt/prometheus
sudo rm -f prometheus.tar.gz

# Create Prometheus user
sudo useradd --no-create-home --shell /bin/false prometheus || true

# Create directories
sudo mkdir -p /opt/prometheus/data
sudo mkdir -p /etc/prometheus
sudo chown -R prometheus:prometheus /opt/prometheus

# Create Prometheus config
cat <<'EOF' | sudo tee /etc/prometheus/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  # FastAPI metrics
  - job_name: 'fastapi'
    static_configs:
      - targets: ['localhost:8009']
    metrics_path: '/metrics'

  # Node exporter (system metrics)
  - job_name: 'node'
    static_configs:
      - targets: ['localhost:9100']

  # Prometheus self-monitoring
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']
EOF

sudo chown prometheus:prometheus /etc/prometheus/prometheus.yml

# Create systemd service
cat <<'EOF' | sudo tee /etc/systemd/system/prometheus.service
[Unit]
Description=Prometheus Monitoring System
After=network.target

[Service]
Type=simple
User=prometheus
ExecStart=/opt/prometheus/prometheus \
  --config.file=/etc/prometheus/prometheus.yml \
  --storage.tsdb.path=/opt/prometheus/data \
  --web.listen-address=127.0.0.1:9090 \
  --storage.tsdb.retention.time=15d
Restart=always

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable prometheus
sudo systemctl start prometheus

echo "✓ Prometheus installed and started on http://127.0.0.1:9090"
echo ""

# =============================================================================
# 2. Install Node Exporter (System Metrics)
# =============================================================================

echo "[2/5] Installing Node Exporter..."

NODE_EXPORTER_VERSION="1.7.0"
NODE_EXPORTER_URL="https://github.com/prometheus/node_exporter/releases/download/v${NODE_EXPORTER_VERSION}/node_exporter-${NODE_EXPORTER_VERSION}.linux-${ARCH}.tar.gz"

cd /tmp
wget -q "$NODE_EXPORTER_URL" -O node_exporter.tar.gz
tar xzf node_exporter.tar.gz
sudo mv node_exporter-${NODE_EXPORTER_VERSION}.linux-${ARCH}/node_exporter /usr/local/bin/
sudo rm -rf node_exporter*

# Create systemd service
cat <<'EOF' | sudo tee /etc/systemd/system/node_exporter.service
[Unit]
Description=Node Exporter
After=network.target

[Service]
Type=simple
User=prometheus
ExecStart=/usr/local/bin/node_exporter
Restart=always

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable node_exporter
sudo systemctl start node_exporter

echo "✓ Node Exporter installed and started on http://127.0.0.1:9100"
echo ""

# =============================================================================
# 3. Install Grafana
# =============================================================================

echo "[3/5] Installing Grafana..."

# Add Grafana repository
sudo apt-get install -y software-properties-common apt-transport-https
wget -q -O - https://packages.grafana.com/gpg.key | sudo apt-key add -
echo "deb https://packages.grafana.com/oss/deb stable main" | sudo tee /etc/apt/sources.list.d/grafana.list

# Install Grafana
sudo apt-get update
sudo apt-get install -y grafana

# Enable and start Grafana
sudo systemctl enable grafana-server
sudo systemctl start grafana-server

echo "✓ Grafana installed and started on http://127.0.0.1:3000"
echo "  Default login: admin / admin (change on first login)"
echo ""

# =============================================================================
# 4. Install Loki (Log Aggregation)
# =============================================================================

echo "[4/5] Installing Loki..."

LOKI_VERSION="2.9.3"
LOKI_URL="https://github.com/grafana/loki/releases/download/v${LOKI_VERSION}/loki-linux-${ARCH}.zip"

cd /tmp
wget -q "$LOKI_URL" -O loki.zip
unzip -q loki.zip
sudo mv loki-linux-${ARCH} /opt/loki
sudo rm -f loki.zip

# Create Loki user
sudo useradd --no-create-home --shell /bin/false loki || true

# Create directories
sudo mkdir -p /opt/loki/data
sudo mkdir -p /opt/loki/index
sudo mkdir -p /opt/loki/cache
sudo mkdir -p /opt/loki/chunks
sudo chown -R loki:loki /opt/loki

# Create Loki config
cat <<'EOF' | sudo tee /opt/loki/loki-config.yml
auth_enabled: false

server:
  http_listen_port: 3100

ingester:
  lifecycler:
    ring:
      kvstore:
        store: inmemory
      replication_factor: 1
  chunk_idle_period: 5m
  chunk_retain_period: 30s

schema_config:
  configs:
    - from: 2023-01-01
      store: boltdb-shipper
      object_store: filesystem
      schema: v11
      index:
        prefix: index_
        period: 24h

storage_config:
  boltdb_shipper:
    active_index_directory: /opt/loki/index
    cache_location: /opt/loki/cache
    shared_store: filesystem
  filesystem:
    directory: /opt/loki/chunks

limits_config:
  retention_period: 30d
  ingestion_rate_mb: 10
  ingestion_burst_size_mb: 20
EOF

sudo chown loki:loki /opt/loki/loki-config.yml

# Create systemd service
cat <<'EOF' | sudo tee /etc/systemd/system/loki.service
[Unit]
Description=Loki Log Aggregation System
After=network.target

[Service]
Type=simple
User=loki
ExecStart=/opt/loki -config.file=/opt/loki/loki-config.yml
Restart=always

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable loki
sudo systemctl start loki

echo "✓ Loki installed and started on http://127.0.0.1:3100"
echo ""

# =============================================================================
# 5. Install Promtail (Log Shipper)
# =============================================================================

echo "[5/5] Installing Promtail..."

PROMTAIL_URL="https://github.com/grafana/loki/releases/download/v${LOKI_VERSION}/promtail-linux-${ARCH}.zip"

cd /tmp
wget -q "$PROMTAIL_URL" -O promtail.zip
unzip -q promtail.zip
sudo mv promtail-linux-${ARCH} /opt/promtail
sudo rm -f promtail.zip

# Create Promtail config
cat <<'EOF' | sudo tee /opt/loki/promtail-config.yml
server:
  http_listen_port: 9080

positions:
  filename: /tmp/positions.yaml

clients:
  - url: http://localhost:3100/loki/api/v1/push

scrape_configs:
  # FastAPI application logs
  - job_name: fastapi
    static_configs:
      - targets:
          - localhost
        labels:
          job: fastapi
          env: production
          __path__: /var/log/foerder-api.log
    pipeline_stages:
      - json:
          expressions:
            level: level
            timestamp: timestamp
            message: event
      - labels:
          level:

  # Scraper logs
  - job_name: scraper
    static_configs:
      - targets:
          - localhost
        labels:
          job: scraper
          env: production
          __path__: /var/log/foerder-scraper.log

  # System logs
  - job_name: syslog
    static_configs:
      - targets:
          - localhost
        labels:
          job: syslog
          __path__: /var/log/syslog
EOF

# Create systemd service
cat <<'EOF' | sudo tee /etc/systemd/system/promtail.service
[Unit]
Description=Promtail Log Shipper
After=network.target loki.service

[Service]
Type=simple
User=loki
ExecStart=/opt/promtail -config.file=/opt/loki/promtail-config.yml
Restart=always

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable promtail
sudo systemctl start promtail

echo "✓ Promtail installed and started"
echo ""

# =============================================================================
# Final Status Check
# =============================================================================

echo "======================================"
echo "Installation Complete!"
echo "======================================"
echo ""
echo "Services Status:"
sudo systemctl status prometheus --no-pager | grep "Active:"
sudo systemctl status node_exporter --no-pager | grep "Active:"
sudo systemctl status grafana-server --no-pager | grep "Active:"
sudo systemctl status loki --no-pager | grep "Active:"
sudo systemctl status promtail --no-pager | grep "Active:"

echo ""
echo "Access Points (via SSH tunnel):"
echo "  - Prometheus:  http://localhost:9090"
echo "  - Grafana:     http://localhost:3000 (admin/admin)"
echo "  - Loki:        http://localhost:3100"
echo ""
echo "Next Steps:"
echo "  1. Open SSH tunnel: ssh -L 3000:localhost:3000 -L 9090:localhost:9090 opc@130.61.76.199"
echo "  2. Open Grafana: http://localhost:3000"
echo "  3. Add Prometheus data source: http://localhost:9090"
echo "  4. Add Loki data source: http://localhost:3100"
echo "  5. Import dashboards from /opt/grafana-dashboards/"
echo ""
echo "Configuration files:"
echo "  - Prometheus: /etc/prometheus/prometheus.yml"
echo "  - Loki:       /opt/loki/loki-config.yml"
echo "  - Promtail:   /opt/loki/promtail-config.yml"
echo ""
echo "Logs:"
echo "  - journalctl -u prometheus -f"
echo "  - journalctl -u grafana-server -f"
echo "  - journalctl -u loki -f"
echo ""
