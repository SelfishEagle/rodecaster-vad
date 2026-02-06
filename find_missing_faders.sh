#!/bin/bash

echo "We need to find which AUX channels map to Fader 1 and Fader 3"
echo ""

# We know:
# AUX2,AUX3 → Fader 2 (currently Chat, should be Game)
# AUX4,AUX5 → Fader 3 (currently Game, should be Music)
# Need to find: Fader 1 and what Music is currently going to

echo "Test A: Playing to AUX6,AUX7..."
pw-loopback --capture-props='media.class=Audio/Sink node.name=test_sink' \
    --playback-props="node.target=alsa_output.usb-R__DE_RODECaster_Pro_II_GV0147346-00.pro-output-1 audio.position=[ AUX6 AUX7 ]" &
LOOP_PID=$!
sleep 1
paplay /usr/share/sounds/freedesktop/stereo/complete.oga --device=test_sink 2>/dev/null
read -p "Which fader? (1/2/3/other): " FADER_6_7
kill $LOOP_PID 2>/dev/null
sleep 1

echo ""
echo "Test B: Playing to AUX8,AUX9..."
pw-loopback --capture-props='media.class=Audio/Sink node.name=test_sink' \
    --playback-props="node.target=alsa_output.usb-R__DE_RODECaster_Pro_II_GV0147346-00.pro-output-1 audio.position=[ AUX8 AUX9 ]" &
LOOP_PID=$!
sleep 1
paplay /usr/share/sounds/freedesktop/stereo/complete.oga --device=test_sink 2>/dev/null
read -p "Which fader? (1/2/3/other): " FADER_8_9
kill $LOOP_PID 2>/dev/null
sleep 1

echo ""
echo "Test C: Playing to AUX0,AUX1..."
pw-loopback --capture-props='media.class=Audio/Sink node.name=test_sink' \
    --playback-props="node.target=alsa_output.usb-R__DE_RODECaster_Pro_II_GV0147346-00.pro-output-1 audio.position=[ AUX0 AUX1 ]" &
LOOP_PID=$!
sleep 1
paplay /usr/share/sounds/freedesktop/stereo/complete.oga --device=test_sink 2>/dev/null
read -p "Which fader? (1/2/3/other): " FADER_0_1
kill $LOOP_PID 2>/dev/null

echo ""
echo "═══════════════════════════════════════════════════════"
echo "CHANNEL MAPPING:"
echo "═══════════════════════════════════════════════════════"
echo "AUX0,AUX1 → Fader $FADER_0_1"
echo "AUX2,AUX3 → Fader 2"
echo "AUX4,AUX5 → Fader 3"
echo "AUX6,AUX7 → Fader $FADER_6_7"
echo "AUX8,AUX9 → Fader $FADER_8_9"
echo "═══════════════════════════════════════════════════════"
