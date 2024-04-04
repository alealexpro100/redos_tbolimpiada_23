#!/bin/bash

zone_out=public

# Sometimes there are no public zone
# firewall-cmd --reload

case "$1" in
    add)
        firewall-cmd --zone=$zone_out --add-rich-rule='rule family=ipv4 masquerade'
        firewall-cmd --zone=$zone_out --add-forward-port=port=$2:proto=tcp:toport=$3:toaddr=$4
    ;;
    remove)
        firewall-cmd --zone=$zone_out --remove-rich-rule='rule family=ipv4 masquerade'
        firewall-cmd --zone=$zone_out --remove-forward-port=port=$2:proto=tcp:toport=$3:toaddr=$4
    ;;
    *)
        exit 0
    ;;
esac