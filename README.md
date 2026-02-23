# RØDECaster Pro 2 Virtual Audio Driver for Linux

<p align="center">
  <img src="https://img.shields.io/badge/Platform-Linux-blue?logo=linux" alt="Platform">
  <img src="https://img.shields.io/badge/License-GPL--3.0-green" alt="License">
  <img src="https://img.shields.io/badge/Python-3.10+-yellow?logo=python" alt="Python">
</p>

Windows-like virtual audio routing for the RØDECaster Pro 2 on Linux. Control your apps with physical mixer faders!

## ✨ Features

- 🎛️ **3 Virtual Outputs** mapped to physical faders
- 🎨 **GTK4 Control Panel** - no command line needed!
- 🔊 **Multiple Apps Per Fader** - software mixing
- 🔄 **Auto-Detection** - plug and play
- ⚡ **Systemd Integration** - runs in background
- 🎯 **No pavucontrol needed** - route apps in the GUI

## 📸 Screenshots

![Control Panel](https://r2.fivemanage.com/twlJi4g2rT1Wmmh5KJ1u9/Preview.png)
*Full-featured GTK4 control panel*

## 🎯 What It Does

Creates virtual audio outputs that route to specific faders on your Rodecaster Pro 2:

| Virtual Output | Physical Fader | Typical Use |
|----------------|----------------|-------------|
| Chat (Discord) | Fader 1 | Voice chat, Discord |
| Game Output | Fader 2 | Games, gameplay audio |
| Music Output | Fader 3 | Music, browsers, media |

**Control volume with your physical mixer faders!**

## 🚀 Installation

### Arch Linux / Manjaro / EndeavourOS
```bash
# Clone the repo
git clone https://github.com/selfisheagle/rodecaster-vad.git
cd rodecaster-vad

# Install dependencies
sudo pacman -S python python-hidapi pipewire pipewire-audio wireplumber python-gobject gtk4 libadwaita

# Install Python packages
pip install --user hid pyudev

# Install the service
sudo cp 90-rodecaster-vad.rules /etc/udev/rules.d/
cp rodecaster-vad.service ~/.config/systemd/user/
systemctl --user enable rodecaster-vad.service
systemctl --user start rodecaster-vad.service

# Install GUI launcher
cp rodecaster-control.desktop ~/.local/share/applications/
chmod +x rodecaster_gtk_gui.py
update-desktop-database ~/.local/share/applications/

# Reload udev
sudo udevadm control --reload-rules
sudo udevadm trigger
```

### Other Distributions

Dependencies needed:
- Python 3.10+
- python-hidapi
- PipeWire with pipewire-pulse
- GTK4 and libadwaita
- systemd

Follow similar steps as above, adjusting package names for your distro.

## 📖 Usage

### GUI Control Panel

1. **Launch the app** from your application menu: "RØDECaster Control Panel"
2. **Play audio** in any application (Firefox, Spotify, Discord, games)
3. **Click "Refresh Apps"** to see available apps
4. **Select app** from dropdown under the fader you want
5. **Control volume** with your physical Rodecaster fader!

### Command Line
```bash
# Check service status
systemctl --user status rodecaster-vad.service

# View logs
journalctl --user -u rodecaster-vad.service -f

# Manual control
rodecaster-ctl status
rodecaster-ctl restart
```

## 🔧 How It Works

1. **HID Communication** - Detects Rodecaster via USB HID
2. **Pro Audio Mode** - Switches to multitrack USB mode
3. **Virtual Sinks** - Creates PipeWire virtual audio devices
4. **Channel Mapping** - Routes to specific hardware channels:
   - Chat → pro-output-0 (2-channel)
   - Game → pro-output-1 AUX2,AUX3
   - Music → pro-output-1 AUX4,AUX5
5. **Software Mixing** - PipeWire mixes multiple apps per fader

## 🛠️ Requirements

### Hardware
- RØDECaster Pro 2 (USB VID:PID 19f7:0072)
- Multitrack mode enabled on Rodecaster

### Software
- Linux kernel with USB Audio Class 2.0 support
- PipeWire audio system
- systemd
- Python 3.10+

## 📋 Project Structure
```
rodecaster-vad/
├── rodecaster_daemon.py          # Background service (main driver)
├── rodecaster_gtk_gui.py         # GTK4 control panel
├── rodecaster-vad.service        # Systemd user service
├── 90-rodecaster-vad.rules       # udev rules
├── rodecaster-ctl                # CLI control tool
├── rodecaster-control.desktop    # Desktop launcher
├── PKGBUILD                      # Arch package build file
└── README.md                     # This file
```

## 🐛 Troubleshooting

**Service won't start:**
```bash
systemctl --user status rodecaster-vad.service
journalctl --user -u rodecaster-vad.service -n 50
```

**Device not detected:**
```bash
lsusb | grep -i rode  # Should show: 19f7:0072
ls -l /dev/hidraw*    # Check permissions
```

**No virtual outputs:**
```bash
pactl list short sinks | grep rodecaster
# Should show 3 virtual outputs
```

**Multitrack not working:**
- Check Rodecaster settings: Enable "Multitrack" mode via USB
- Verify pro-audio profile: `pactl list cards | grep -A50 RODECaster`

## 🤝 Contributing

Contributions welcome! Feel free to:
- 🐛 Report bugs via Issues
- 💡 Suggest features
- 🔧 Submit Pull Requests
- 📖 Improve documentation

### Development Setup
```bash
git clone https://github.com/selfisheagle/rodecaster-vad.git
cd rodecaster-vad

# Test changes
python3 rodecaster_daemon.py      # Test daemon
python3 rodecaster_gtk_gui.py     # Test GUI
```

## 📜 License

GPL-3.0 - See [LICENSE](LICENSE) file

## 🙏 Credits

- **Created by**: SelfishEagle
- **Reverse-engineered with**: Claude (Anthropic AI)
- **Community**: Linux audio enthusiasts
- **Inspired by**: RØDE's Windows driver

## 🔗 Links

- **Issues**: https://github.com/selfisheagle/rodecaster-vad/issues
- **Discussions**: https://github.com/selfisheagle/rodecaster-vad/discussions
- **RØDE**: https://rode.com/

## ⭐ Star History

If this project helped you, consider giving it a star! ⭐

---

**Made with ❤️ for the Linux audio community**
