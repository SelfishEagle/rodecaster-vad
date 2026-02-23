# Maintainer: SelfishEagle <your@email.com>
pkgname=rodecaster-vad
pkgver=1.0.0
pkgrel=1
pkgdesc="Virtual Audio Driver for RØDECaster Pro 2 on Linux - Control apps with physical mixer faders"
arch=('any')
url="https://github.com/SelfishEagle/rodecaster-vad"
license=('GPL3')
depends=(
    'python'
    'python-hidapi'
    'pipewire'
    'pipewire-pulse'
    'wireplumber'
    'python-gobject'
    'gtk4'
    'libadwaita'
    'python-pyudev'
)
makedepends=('git')
optdepends=('python-hid: alternative HID backend')
source=("${pkgname}::git+${url}.git")
sha256sums=('SKIP')

package() {
    cd "$srcdir/$pkgname"

    # Install Python scripts
    install -Dm755 rodecaster_daemon.py   "$pkgdir/usr/lib/$pkgname/rodecaster_daemon.py"
    install -Dm755 rodecaster_gtk_gui.py  "$pkgdir/usr/lib/$pkgname/rodecaster_gtk_gui.py"
    install -Dm755 rodecaster_gui.py      "$pkgdir/usr/lib/$pkgname/rodecaster_gui.py"

    # Install shell utilities
    install -Dm755 find_channels.sh         "$pkgdir/usr/lib/$pkgname/find_channels.sh"
    install -Dm755 find_missing_faders.sh   "$pkgdir/usr/lib/$pkgname/find_missing_faders.sh"
    install -Dm755 test_all_multitrack.sh   "$pkgdir/usr/lib/$pkgname/test_all_multitrack.sh"
    install -Dm755 test_channels.sh         "$pkgdir/usr/lib/$pkgname/test_channels.sh"
    install -Dm755 test_each_output.sh      "$pkgdir/usr/lib/$pkgname/test_each_output.sh"

    # Install udev rules
    install -Dm644 /dev/stdin "$pkgdir/usr/lib/udev/rules.d/90-rodecaster-vad.rules" << 'EOF'
SUBSYSTEM=="hidraw", ATTRS{idVendor}=="19f7", ATTRS{idProduct}=="0072", MODE="0660", GROUP="wheel", TAG+="uaccess"
SUBSYSTEM=="usb", ATTRS{idVendor}=="19f7", ATTRS{idProduct}=="0072", MODE="0660", GROUP="wheel", TAG+="uaccess"
EOF

    # Install systemd user service
    install -Dm644 /dev/stdin "$pkgdir/usr/lib/systemd/user/rodecaster-vad.service" << 'EOF'
[Unit]
Description=RØDECaster Pro 2 Virtual Audio Driver
After=pipewire.service wireplumber.service
Wants=pipewire.service wireplumber.service

[Service]
Type=simple
ExecStart=/usr/bin/python3 /usr/lib/rodecaster-vad/rodecaster_daemon.py
Restart=on-failure
RestartSec=5

[Install]
WantedBy=default.target
EOF

    # Install desktop entry
    install -Dm644 /dev/stdin "$pkgdir/usr/share/applications/rodecaster-control.desktop" << 'EOF'
[Desktop Entry]
Name=RØDECaster Control Panel
Comment=Virtual Audio Driver for RØDECaster Pro 2
Exec=/usr/bin/python3 /usr/lib/rodecaster-vad/rodecaster_gtk_gui.py
Icon=audio-card
Terminal=false
Type=Application
Categories=AudioVideo;Audio;
EOF

    # Install CLI wrapper
    install -Dm755 /dev/stdin "$pkgdir/usr/bin/rodecaster-ctl" << 'EOF'
#!/bin/bash
case "$1" in
    start)   systemctl --user start   rodecaster-vad.service ;;
    stop)    systemctl --user stop    rodecaster-vad.service ;;
    restart) systemctl --user restart rodecaster-vad.service ;;
    status)  systemctl --user status  rodecaster-vad.service ;;
    logs)    journalctl --user -u rodecaster-vad.service -f  ;;
    gui)     python3 /usr/lib/rodecaster-vad/rodecaster_gtk_gui.py ;;
    *)
        echo "Usage: rodecaster-ctl {start|stop|restart|status|logs|gui}"
        exit 1
        ;;
esac
EOF

    # Install docs
    install -Dm644 README.md      "$pkgdir/usr/share/doc/$pkgname/README.md"
    install -Dm644 CONTRIBUTING.md "$pkgdir/usr/share/doc/$pkgname/CONTRIBUTING.md"
    install -Dm644 LICENSE         "$pkgdir/usr/share/licenses/$pkgname/LICENSE"
}
