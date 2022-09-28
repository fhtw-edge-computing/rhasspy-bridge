# for autostart:
# sudo nano /etc/xdg/autostart/display.desktop
# insert:
# [Desktop Entry]
# Name=RhasspyStart
# Exec=/usr/bin/bash /home/pi/rhasspy-bridge/start.sh

# don't do this because it kills this script
# echo "closing everything..."
# pkill -15 -f rhasspy
# pkill -15 python3

echo "start rhasspy..."
rhasspy -p de > /home/pi/log_rhasspy.txt &
echo "start bridge..."
cd /home/pi/rhasspy-bridge/src/ && python3 server.py > /home/pi/log_bridge.txt &

sleep 2
echo "start browser..."
#sensible-browser http://localhost:12101/ &
#sleep 5
chromium-browser --kiosk http://localhost:1234/ &
