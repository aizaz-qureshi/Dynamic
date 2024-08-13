#!/bin/bash

if [ $# -ne 1 ]; then
  echo "Usage: ./change.sh <1|2|3>"
  exit 1
fi

option=$1

if [ "$option" -eq 1 ]; then
  sudo ovs-ofctl add-flow s1 priority=200,in_port=1,actions=group:1
  sudo ovs-ofctl add-flow s2 priority=200,in_port=1,actions=group:1


elif [ "$option" -eq 2 ]; then
  sudo ovs-ofctl add-flow s1 priority=200,in_port=1,actions=group:2
  sudo ovs-ofctl add-flow s2 priority=200,in_port=1,actions=group:2


elif [ "$option" -eq 3 ]; then
  sudo ovs-ofctl add-flow s1 priority=200,in_port=1,actions=group:3
  sudo ovs-ofctl add-flow s2 priority=200,in_port=1,actions=group:3
else
  echo "Invalid option. Usage: ./change.sh <1|2|3>"
  exit 1
fi

