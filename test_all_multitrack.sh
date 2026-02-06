#!/bin/bash

echo "Testing ALL multitrack channel pairs with dont-remix..."
echo ""

for i in 0 2 4 6 8; do
    j=$((i+1))
    echo "Test: AUX${i},AUX${j}..."
    pw-loopback --capture-props='media.class=Audio/Sink node.name=test_sink' \
        --playback-props="node.target=alsa_output.usb-R__DE_RODECaster_Pro_II_GV0147346-00.pro-output-1 audio.position=[ AUX${i} AUX${j} ] stream.dont-remix=true" &
    LOOP_PID=$!
    sleep 1
    paplay /usr/share/sounds/freedesktop/stereo/complete.oga --device=test_sink 2>/dev/null
    read -p "  Which fader? (1/2/3/none): " FADER
    echo "  AUX${i},AUX${j} → Fader $FADER"
    kill $LOOP_PID 2>/dev/null
    sleep 1
    echo ""
done
