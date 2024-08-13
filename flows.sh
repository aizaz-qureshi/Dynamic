
# ###############
#
# Author: Aizaz Ali
# Date: 28 june 2024
# version v1
#
#################
#
# CODE DISCRIPTION:
# THESE FLOWS ARE OV-SWITCH
# DIVIDED INTO THREE GROUP
# ETH 2 3 4
# ETH 5 6 7
# ETH 8 9 10
#
# WORKING:
# WHEN ANY GROUP DEFAULT LINK DOWN 2 BACKUP LINKS SUPPORT
# THAT USES BUCKET WATCH TO MONITER THE STATUS WHEN LINK
# IS DOWN IT MOVE THE NEXT


# NOTE
# GROUP SWITCHING OCCURS WHEN THE SEPERATE PYTHON FILE
# TRIGEER THE THERESHOLD BANDWIDTH GROUP 1 TO GROUP 2

# DEFAULT:
# BY DEFAULT THE GROUP 1 IS ACTIVE

sudo ovs-ofctl add-group s1 group_id=1,type=ff,bucket=watch_port=s1-eth2,output=s1-eth2,bucket=watch_port=s1-eth3,output=s1-eth3,bucket=watch_port=s1-eth4,output=s1-eth4
sudo ovs-ofctl add-group s1 group_id=2,type=ff,bucket=watch_port=s1-eth5,output=s1-eth5,bucket=watch_port=s1-eth6,output=s1-eth6,bucket=watch_port=s1-eth7,output=s1-eth7
sudo ovs-ofctl add-group s1 group_id=3,type=ff,bucket=watch_port=s1-eth8,output=s1-eth8,bucket=watch_port=s1-eth9,output=s1-eth9,bucket=watch_port=s1-eth10,output=s1-eth10


sudo ovs-ofctl add-group s2 group_id=1,type=ff,bucket=watch_port=s2-eth2,output=s2-eth2,bucket=watch_port=s2-eth3,output=s2-eth3,bucket=watch_port=s2-eth4,output=s2-eth4
sudo ovs-ofctl add-group s2 group_id=2,type=ff,bucket=watch_port=s2-eth5,output=s2-eth5,bucket=watch_port=s2-eth6,output=s2-eth6,bucket=watch_port=s2-eth7,output=s2-eth7
sudo ovs-ofctl add-group s2 group_id=3,type=ff,bucket=watch_port=s2-eth8,output=s2-eth8,bucket=watch_port=s2-eth9,output=s2-eth9,bucket=watch_port=s2-eth10,output=s2-eth10


# Traffic from h1 to h2 using group 1
sudo ovs-ofctl add-flow s1 priority=200,in_port=1,actions=group:1
sudo ovs-ofctl add-flow s2 priority=200,in_port=1,actions=group:1
# Return traffic from s2 to h1
sudo ovs-ofctl add-flow s1 priority=200,in_port=2,actions=output:1
sudo ovs-ofctl add-flow s1 priority=200,in_port=3,actions=output:1
sudo ovs-ofctl add-flow s1 priority=200,in_port=4,actions=output:1

# Traffic from s1 to h2 using group 1
sudo ovs-ofctl add-flow s2 priority=200,in_port=2,actions=output:1
sudo ovs-ofctl add-flow s2 priority=200,in_port=3,actions=output:1
sudo ovs-ofctl add-flow s2 priority=200,in_port=4,actions=output:1
# Return traffic from h2 to s1
sudo ovs-ofctl add-flow s2 priority=200,in_port=1,actions=output=2
sudo ovs-ofctl add-flow s2 priority=200,in_port=1,actions=output=3
sudo ovs-ofctl add-flow s2 priority=200,in_port=1,actions=output=4


# Traffic from h1 to h2 using group 2

# Return traffic from s2 to h1
sudo ovs-ofctl add-flow s1 priority=200,in_port=5,actions=output:1
sudo ovs-ofctl add-flow s1 priority=200,in_port=6,actions=output:1
sudo ovs-ofctl add-flow s1 priority=200,in_port=7,actions=output:1

# Traffic from s1 to h2 using group 2
sudo ovs-ofctl add-flow s2 priority=200,in_port=5,actions=output:1
sudo ovs-ofctl add-flow s2 priority=200,in_port=6,actions=output:1
sudo ovs-ofctl add-flow s2 priority=200,in_port=7,actions=output:1
# Return traffic from h2 to s1
sudo ovs-ofctl add-flow s2 priority=200,in_port=1,actions=output=5
sudo ovs-ofctl add-flow s2 priority=200,in_port=1,actions=output=6
sudo ovs-ofctl add-flow s2 priority=200,in_port=1,actions=output=7

# Traffic from h1 to h2 using group 3

# Return traffic from s2 to h1
sudo ovs-ofctl add-flow s1 priority=200,in_port=8,actions=output:1
sudo ovs-ofctl add-flow s1 priority=200,in_port=9,actions=output:1
sudo ovs-ofctl add-flow s1 priority=200,in_port=10,actions=output:1

# Traffic from s1 to h2 using group 3
sudo ovs-ofctl add-flow s2 priority=200,in_port=8,actions=output:1
sudo ovs-ofctl add-flow s2 priority=200,in_port=9,actions=output:1
sudo ovs-ofctl add-flow s2 priority=200,in_port=10,actions=output:1
# Return traffic from h2 to s1
sudo ovs-ofctl add-flow s2 priority=200,in_port=1,actions=output=8
sudo ovs-ofctl add-flow s2 priority=200,in_port=1,actions=output=9
sudo ovs-ofctl add-flow s2 priority=200,in_port=1,actions=output=10


#!/bin/bash

if [ $# -ne 1 ]; then
  echo "Usage: ./flows.sh <2|3>"
  exit 1
fi

option=$1

if [ "$option" -eq 2 ]; then
  sudo ovs-ofctl add-flow s1 priority=200,in_port=1,actions=group:2
  sudo ovs-ofctl add-flow s2 priority=200,in_port=1,actions=group:2
elif [ "$option" -eq 3 ]; then
  sudo ovs-ofctl add-flow s1 priority=200,in_port=1,actions=group:3
  sudo ovs-ofctl add-flow s2 priority=200,in_port=1,actions=group:3
else
  echo "Invalid option. Usage: ./flows.sh <2|3>"
  exit 1
fi

