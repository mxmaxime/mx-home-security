#!/bin/bash

# The idea of this script was to find raspberrypi's on the network
# and setup them: ssh keys + assign device_id + create a file to automatically register
# these devices to the core app.

SELF_LAN_IP=$(hostname -I | awk '{print $1}')

echo "My IP in the LAN is: $SELF_LAN_IP"

exclude_my_self="--exclude $SELF_LAN_IP"

gateway_ip=$(ip route show 0.0.0.0/0 | cut -d\  -f3)

# ip/mask, ex: 192.168.1.0/24
network_ip_cidr=$(ipcalc $gateway_ip | grep 'Network' | awk '{print $2}')

for raspberry_pi_ip in `sudo nmap -sn $network_ip_cidr | awk 'f==2{print s; f=s=""}/^(Nmap scan|MAC Address)/{sub(/^.*(for|:..) /,"");f++;s=(s?s OFS :"")$0}END{if(f==2)print s}' | grep 'Raspberry' | grep -o '[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}'`
do
    echo "I've found another RPI on the network: $raspberry_pi_ip."

    # check if we've already setup ssh for this rpi's
    nb_line=$(cat ~/.ssh/config| grep -o $raspberry_pi_ip | wc -l)

    # gt 0
    if [ "$nb_line" -gt 0 ]; then
        echo "The system already knows this device."
    else
        # connect with SSH
        # Change the hostname with the device id. raspberrypi_deviceid
        DEVICE_ID=$(cat /proc/sys/kernel/random/uuid | cut -d "-" -f 1)

        # Default HOSTNAME given by RPI by default.
        CURRENT_HOSTNAME="raspberrypi"
        NEW_HOSTNAME="rpi-$DEVICE_ID"

        # echo "This device id is: $DEVICE_ID"
        # echo "I'm configuring SSH with keys."

        # KEYNAME="id_$DEVICE_ID"

        # ssh-keygen -t ed25519 -f ~/.ssh/$KEYNAME
        # eval "$(ssh-agent -s)" >> /dev/null
        # ssh-add ~/.ssh/$KEYNAME

        # ssh-copy-id -i ~/.ssh/$KEYNAME pi@$raspberry_pi_ip

        # conf="Host $DEVICE_ID \n\t HostName $raspberry_pi_ip \n\t User pi \n\t IdentityFile ~/.ssh/$KEYNAME \n\t IdentitiesOnly yes"
        # echo -e $conf >> ~/.ssh/config

        # echo "Use ssh pi@$DEVICE_ID to connect."

        # echo "Changing the hostname from $CURRENT_HOSTNAME to $NEW_HOSTNAME"    

        # ssh pi@$DEVICE_ID 'bash -s' < change_hostname.sh $CURRENT_HOSTNAME $NEW_HOSTNAME
    fi
done
