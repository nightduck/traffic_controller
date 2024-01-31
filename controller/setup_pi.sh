# Initial steps:
# Step pi following directions here: https://www.raspberrypi.com/documentation/computers/getting-started.html#installing-the-operating-system
# Use custimization step to enable SSH
# Boot into pi and run the following commands:
# sudo apt-get update
# sudo apt-get upgrade
# sudo apt-get install git python3-flask vim
# git clone https://github.com/nightduck/traffic_controller.git

sudo -v
sudo nmcli device wifi hotspot ssid MiniCity password mckelvey ifname wlan0
uuid=`nmcli connection | grep Hotspot | awk '{print $2}'`
sudo nmcli connection modify $uuid connection.autoconnect yes connection.autoconnect-priority 100
