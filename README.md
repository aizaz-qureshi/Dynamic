# Dynamic
Dynamic link switching and visualization in mininet environment 

# Insall VM-BOX latest verion
https://www.virtualbox.org/wiki/Downloads

# Instal PuTTY
https://www.putty.org/

# Install xming or Xlaunch
https://sourceforge.net/projects/xming/

# Install mininet
https://mininet.org/download/#option-1-mininet-vm-installation-easy-recommended

# Install Prometheusm, Node Exporter and Grafana
If you are new to Prometheus and node_exporter there is a simple step-by-step guide.https://prometheus.io/docs/guides/node-exporter/

The node_exporter listens on HTTP port 9100 by default. See the --help output for more options.

OR Direct installation in the terminal

# Prometheus
wget https://github.com/prometheus/prometheus/releases/download/v2.34.0/prometheus-2.34.0.linux-amd64.tar.gz

tar -zxvf prometheus-2.34.0.linux-amd64.tar.gz

cd prometheus-2.34.0.linux-amd64

./prometheus --config.file=prometheus.yml or download prometheus.yml

# Node Exporter
wget https://github.com/prometheus/node_exporter/releases/download/v1.8.1/node_exporter-1.8.1.linux-amd64.tar.gz

tar -zxvf node_exporter-1.8.1.linux-amd64.tar.gz

cd node_exporter-1.8.1.linux-amd64

Add the Node Exporter targets to prometheus.yml

./node_exporter

# Grafana
wget https://dl.grafana.com/oss/release/grafana-11.1.0.linux-amd64.tar.gz

tar -zxvf grafana-11.1.0.linux-amd64.tar.gz

cd grafana-11.1.0

./bin/grafana-server

Start grafana or download servie2.sh 


