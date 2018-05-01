#!/bin/bash
sleep 1
systemctl restart hostapd
sleep 1
journalctl -n 60 | grep brcmfmac | while read output;
do
	echo $output
	systemctl restart hostapd
	sleep 2
done
#systemctl restart dnsmasq
