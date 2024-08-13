Prometheus, and Node Exporter simultaneously

# Path configurations (adjust these paths accordingly)
PROMETHEUS_PATH="/home/mininet/prometheus-2.34.0.linux-amd64 "
NODE_EXPORTER_PATH="/home/mininet/node_exporter-1.8.1.linux-amd64 "


# Start Prometheus
echo "Starting Prometheus..."
cd $PROMETHEUS_PATH
./prometheus &

# Start Node Exporter
echo "Starting Node Exporter..."
cd $NODE_EXPORTER_PATH
./node_exporter &


# we can add also the sleep time to continouly running the sciript

# Add an optional message indicating services started
echo "Prometheus, and Node Exporter
