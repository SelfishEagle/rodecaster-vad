#!/bin/bash

echo "═══════════════════════════════════════════════════════"
echo "TESTING EACH VIRTUAL OUTPUT"
echo "Tell me which FADER controls each sound!"
echo "═══════════════════════════════════════════════════════"
echo ""

echo "🔊 Test 1: Playing to 'RØDECaster Chat (Discord)'..."
paplay /usr/share/sounds/freedesktop/stereo/complete.oga --device=rodecaster_chat
read -p "Which fader controlled this? (1/2/3/other): " CHAT_FADER
echo ""

echo "🎮 Test 2: Playing to 'RØDECaster Game Output'..."
paplay /usr/share/sounds/freedesktop/stereo/bell.oga --device=rodecaster_game
read -p "Which fader controlled this? (1/2/3/other): " GAME_FADER
echo ""

echo "🎵 Test 3: Playing to 'RØDECaster Music Output'..."
paplay /usr/share/sounds/freedesktop/stereo/dialog-warning.oga --device=rodecaster_music
read -p "Which fader controlled this? (1/2/3/other): " MUSIC_FADER
echo ""

echo "🔊 Test 4: Playing to 'RØDECaster System Output'..."
paplay /usr/share/sounds/freedesktop/stereo/message.oga --device=rodecaster_system
read -p "Which fader controlled this? (1/2/3/other): " SYSTEM_FADER
echo ""

echo "═══════════════════════════════════════════════════════"
echo "RESULTS:"
echo "═══════════════════════════════════════════════════════"
echo "RØDECaster Chat (Discord) → Fader $CHAT_FADER"
echo "RØDECaster Game Output    → Fader $GAME_FADER"
echo "RØDECaster Music Output   → Fader $MUSIC_FADER"
echo "RØDECaster System Output  → Fader $SYSTEM_FADER"
echo "═══════════════════════════════════════════════════════"
echo ""
echo "Your desired mapping:"
echo "  Fader 1 → Chat (Discord)"
echo "  Fader 2 → Game"
echo "  Fader 3 → Music"
echo ""
echo "Paste these results so I can fix the channel assignments!"
