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

# # TODO: This doesn't work
# # Add the following to /etc/init.d/traffic_controller
# echo "description \"Starts the MiniCity server\"" | sudo tee -a /etc/init.d/traffic_controller
# echo "start on startup" | sudo tee -a /etc/init.d/traffic_controller
# echo "task" | sudo tee -a /etc/init.d/traffic_controller
# echo "exec python /home/pi/traffic_controller/controller/app.py" | sudo tee -a /etc/init.d/traffic_controller
