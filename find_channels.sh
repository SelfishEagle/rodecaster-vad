#!/bin/bash
# Test each stereo pair to find correct mapping

echo "We'll play a test sound to each channel pair."
echo "Tell me which FADER controls it on your Rodecaster!"
echo ""
read -p "Press Enter to start..."

# Test AUX0,AUX1
echo ""
echo "▶ Testing AUX0,AUX1..."
pw-loopback --capture-props='media.class=Audio/Source node.name=test_source' \
    --playback-props="node.target=alsa_output.usb-R__DE_RODECaster_Pro_II_GV0147346-00.pro-output-1 audio.position=[ AUX0 AUX1 ]" &
LOOP_PID=$!
sleep 1
paplay /usr/share/sounds/freedesktop/stereo/complete.oga --device=test_source 2>/dev/null
read -p "Which fader controlled this? (main/music/game/chat/etc): " FADER_0_1
kill $LOOP_PID 2>/dev/null
sleep 1

# Test AUX2,AUX3
echo ""
echo "▶ Testing AUX2,AUX3..."
pw-loopback --capture-props='media.class=Audio/Source node.name=test_source' \
    --playback-props="node.target=alsa_output.usb-R__DE_RODECaster_Pro_II_GV0147346-00.pro-output-1 audio.position=[ AUX2 AUX3 ]" &
LOOP_PID=$!
sleep 1
paplay /usr/share/sounds/freedesktop/stereo/complete.oga --device=test_source 2>/dev/null
read -p "Which fader controlled this? (main/music/game/chat/etc): " FADER_2_3
kill $LOOP_PID 2>/dev/null
sleep 1

# Test AUX4,AUX5
echo ""
echo "▶ Testing AUX4,AUX5..."
pw-loopback --capture-props='media.class=Audio/Source node.name=test_source' \
    --playback-props="node.target=alsa_output.usb-R__DE_RODECaster_Pro_II_GV0147346-00.pro-output-1 audio.position=[ AUX4 AUX5 ]" &
LOOP_PID=$!
sleep 1
paplay /usr/share/sounds/freedesktop/stereo/complete.oga --device=test_source 2>/dev/null
read -p "Which fader controlled this? (main/music/game/chat/etc): " FADER_4_5
kill $LOOP_PID 2>/dev/null
sleep 1

# Test AUX6,AUX7
echo ""
echo "▶ Testing AUX6,AUX7..."
pw-loopback --capture-props='media.class=Audio/Source node.name=test_source' \
    --playback-props="node.target=alsa_output.usb-R__DE_RODECaster_Pro_II_GV0147346-00.pro-output-1 audio.position=[ AUX6 AUX7 ]" &
LOOP_PID=$!
sleep 1
paplay /usr/share/sounds/freedesktop/stereo/complete.oga --device=test_source 2>/dev/null
read -p "Which fader controlled this? (main/music/game/chat/etc): " FADER_6_7
kill $LOOP_PID 2>/dev/null
sleep 1

# Test AUX8,AUX9
echo ""
echo "▶ Testing AUX8,AUX9..."
pw-loopback --capture-props='media.class=Audio/Source node.name=test_source' \
    --playback-props="node.target=alsa_output.usb-R__DE_RODECaster_Pro_II_GV0147346-00.pro-output-1 audio.position=[ AUX8 AUX9 ]" &
LOOP_PID=$!
sleep 1
paplay /usr/share/sounds/freedesktop/stereo/complete.oga --device=test_source 2>/dev/null
read -p "Which fader controlled this? (main/music/game/chat/etc): " FADER_8_9
kill $LOOP_PID 2>/dev/null

echo ""
echo "═══════════════════════════════════════"
echo "CHANNEL MAPPING RESULTS:"
echo "═══════════════════════════════════════"
echo "AUX0,AUX1 → $FADER_0_1"
echo "AUX2,AUX3 → $FADER_2_3"
echo "AUX4,AUX5 → $FADER_4_5"
echo "AUX6,AUX7 → $FADER_6_7"
echo "AUX8,AUX9 → $FADER_8_9"
echo "═══════════════════════════════════════"
echo ""
echo "Save this mapping! I'll use it to fix the daemon."
