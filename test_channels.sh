#!/bin/bash
echo "Testing Rodecaster Channel Mapping"
echo "Listen to which fader controls each sound..."
echo ""

echo "Testing System (channels FL,FR)..."
paplay /usr/share/sounds/freedesktop/stereo/complete.oga --device=rodecaster_system
sleep 2

echo "Testing Music (channels AUX2,AUX3)..."
paplay /usr/share/sounds/freedesktop/stereo/complete.oga --device=rodecaster_music
sleep 2

echo "Testing Game (channels AUX4,AUX5)..."
paplay /usr/share/sounds/freedesktop/stereo/complete.oga --device=rodecaster_game
sleep 2

echo "Testing Virtual-A (channels AUX6,AUX7)..."
paplay /usr/share/sounds/freedesktop/stereo/complete.oga --device=rodecaster_virtual_a
sleep 2

echo "Testing Virtual-B (channels AUX8,AUX9)..."
paplay /usr/share/sounds/freedesktop/stereo/complete.oga --device=rodecaster_virtual_b

echo ""
echo "Which physical fader controlled each one?"
