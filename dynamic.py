#####################
#
# Auther: Aizaz Ali
# Date: 25 June 2024
# Version v1
#
#####################


import threading
import time
import os
from prometheus_api_client import PrometheusConnect

# Bandwidth threshold
UPPER_THRESHOLD = 0.9

# Path to your change.sh script
CHANGE_SCRIPT_PATH = "/home/mininet/sdn/sim/change.sh"

# Prometheus URL
PROMETHEUS_URL = "http://localhost:9090"

# Interfaces (ports) configuration for each group
groups = [
    ['s2-eth2', 's2-eth3', 's2-eth4'],  # Group 1
    ['s2-eth5', 's2-eth6', 's2-eth7'],  # Group 2
    ['s2-eth8', 's2-eth9', 's2-eth10']  # Group 3
]

# Assume each port has a known bandwidth in Mbps for comparison purposes
bandwidths = {
    's2-eth2': 10,
    's2-eth3': 20,
    's2-eth4': 30,
    's2-eth5': 40,
    's2-eth6': 50,
    's2-eth7': 60,
    's2-eth8': 70,
    's2-eth9': 80,
    's2-eth10': 90
}

# Initialize Prometheus connection
prometheus = PrometheusConnect(url=PROMETHEUS_URL, disable_ssl=True)
current_group_index = 0  # Start with group 1

def get_bandwidth_usage(interface):
    query = f'rate(node_network_receive_bytes_total{{device="{interface}"}}[2s])'
    result = prometheus.custom_query(query)
    if result:
        return float(result[0]['value'][1]) * 8 / 1e6  # Convert from Bytes/s to Mbps
    return 0.0

def trigger_change_script(group_index):
    os.system(f'bash {CHANGE_SCRIPT_PATH} {group_index + 1}')
    print(f'Triggered change to group {group_index + 1}')

def monitor_and_switch():
    global current_group_index
    switch_time = time.time() + 600  # Switch back after 10 minutes

    while True:
        group_interfaces = groups[current_group_index]
        exceeded = False

        for interface in group_interfaces:
            usage = get_bandwidth_usage(interface)
            max_bandwidth = bandwidths[interface]
            print(f"Current usage on {interface}: {usage} Mbps (max: {max_bandwidth} Mbps)")

            # Check if usage exceeds upper threshold
            if usage > UPPER_THRESHOLD * max_bandwidth:
                exceeded = True
                break

        if exceeded:
            if current_group_index < len(groups) - 1:
                current_group_index += 1
                trigger_change_script(current_group_index)
                print(f'Switched to group {current_group_index + 1} flows.')
        else:
            # Check if it's time to switch back to group 1 after 10 minutes
            if time.time() > switch_time:
                current_group_index = 0
                trigger_change_script(current_group_index)
                print("Switched back to group 1 flows.")
                switch_time = time.time() + 600  # Reset switch time after 10 minutes

        time.sleep(2)

if __name__ == "__main__":
    monitor_thread = threading.Thread(target=monitor_and_switch)
    monitor_thread.start()

