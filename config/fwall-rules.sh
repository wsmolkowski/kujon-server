#!/usr/bin/env bash

IPTABLES=/sbin/iptables

echo " * flushing old rules"
${IPTABLES} --flush
${IPTABLES} --delete-chain
${IPTABLES} --table nat --flush
${IPTABLES} --table nat --delete-chain

echo " * setting default policies"
${IPTABLES} -P INPUT DROP
${IPTABLES} -P FORWARD DROP
${IPTABLES} -P OUTPUT ACCEPT

echo " * allowing loopback devices"
${IPTABLES} -A INPUT -i lo -j ACCEPT
${IPTABLES} -A OUTPUT -o lo -j ACCEPT

${IPTABLES} -A INPUT -p tcp ! --syn -m state --state NEW -j DROP
${IPTABLES} -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT

## BLOCK ABUSING IPs HERE ##
#echo " * BLACKLIST"
#${IPTABLES} -A INPUT -s _ABUSIVE_IP_ -j DROP
#${IPTABLES} -A INPUT -s _ABUSIVE_IP2_ -j DROP

echo " * allowing ssh on port 22"
${IPTABLES} -A INPUT -p tcp --dport 22  -m state --state NEW -j ACCEPT

#echo " * allowing ftp on port 21"
#${IPTABLES} -A INPUT -p tcp --dport 21  -m state --state NEW -j ACCEPT

#echo " * allowing dns on port 53 udp"
#${IPTABLES} -A INPUT -p udp -m udp --dport 53 -j ACCEPT

#echo " * allowing dns on port 53 tcp"
#${IPTABLES} -A INPUT -p tcp -m tcp --dport 53 -j ACCEPT

echo " * allowing http on port 80"
${IPTABLES} -A INPUT -p tcp --dport 80  -m state --state NEW -j ACCEPT

echo " * allowing https on port 443"
${IPTABLES} -A INPUT -p tcp --dport 443 -m state --state NEW -j ACCEPT

echo " * allowing ping responses"
${IPTABLES} -A INPUT -p ICMP --icmp-type 8 -j ACCEPT

# DROP everything else and Log it
${IPTABLES} -A INPUT -j LOG
${IPTABLES} -A INPUT -j DROP

#
# Save settings
#
echo " * SAVING RULES"

if [[ -d /etc/network/if-pre-up.d ]]; then
    if [[ ! -f /etc/network/if-pre-up.d/iptables ]]; then
        echo -e "#!/bin/bash" > /etc/network/if-pre-up.d/iptables
        echo -e "test -e /etc/iptables.rules && iptables-restore -c /etc/iptable
s.rules" >> /etc/network/if-pre-up.d/iptables
        chmod +x /etc/network/if-pre-up.d/iptables
    fi
fi

iptables-save > /etc/fwall.rules
iptables-restore -c /etc/fwall.rules