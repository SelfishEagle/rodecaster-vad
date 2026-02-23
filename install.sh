#!/usr/bin/env bash
# RØDECaster Pro 2 Virtual Audio Driver - Installer
# https://github.com/SelfishEagle/rodecaster-vad

set -e

REPO_URL="https://github.com/SelfishEagle/rodecaster-vad.git"
INSTALL_DIR="$HOME/rodecaster-vad"
SERVICE_DIR="$HOME/.config/systemd/user"
RULES_FILE="/etc/udev/rules.d/90-rodecaster-vad.rules"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

banner() {
    echo -e "${CYAN}"
    echo "╔══════════════════════════════════════════╗"
    echo "║   RØDECaster Pro 2 Virtual Audio Driver  ║"
    echo "║         Linux Installer v1.0             ║"
    echo "╚══════════════════════════════════════════╝"
    echo -e "${NC}"
}

info()    { echo -e "${CYAN}[INFO]${NC}  $1"; }
success() { echo -e "${GREEN}[OK]${NC}    $1"; }
warn()    { echo -e "${YELLOW}[WARN]${NC}  $1"; }
error()   { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

check_root() {
    if [[ $EUID -eq 0 ]]; then
        error "Don't run this as root. Run as your normal user — sudo will be used where needed."
    fi
}

check_dependencies() {
    info "Checking dependencies..."

    local missing=()
    command -v git    &>/dev/null || missing+=("git")
    command -v python3 &>/dev/null || missing+=("python")
    command -v pactl  &>/dev/null || missing+=("pipewire-pulse")

    if [[ ${#missing[@]} -gt 0 ]]; then
        warn "Missing packages: ${missing[*]}"
        info "Installing missing dependencies..."
        sudo pacman -S --needed --noconfirm \
            git python python-hidapi \
            pipewire pipewire-pulse pipewire-audio \
            wireplumber python-gobject gtk4 libadwaita
    else
        info "Installing/verifying all system dependencies..."
        sudo pacman -S --needed --noconfirm \
            git python python-hidapi \
            pipewire pipewire-pulse pipewire-audio \
            wireplumber python-gobject gtk4 libadwaita
    fi

    success "Dependencies ready."
}

install_udev_rules() {
    info "Installing udev rules..."

    sudo tee "$RULES_FILE" > /dev/null << 'EOF'
# RØDECaster Pro 2 - VID:PID 19f7:0072
SUBSYSTEM=="hidraw", ATTRS{idVendor}=="19f7", ATTRS{idProduct}=="0072", MODE="0660", GROUP="wheel", TAG+="uaccess"
SUBSYSTEM=="usb", ATTRS{idVendor}=="19f7", ATTRS{idProduct}=="0072", MODE="0660", GROUP="wheel", TAG+="uaccess"
EOF

    sudo udevadm control --reload-rules
    sudo udevadm trigger

    success "udev rules installed. Replug your RØDECaster if it's already connected."
}

install_service() {
    info "Installing systemd user service..."

    mkdir -p "$SERVICE_DIR"

    tee "$SERVICE_DIR/rodecaster-vad.service" > /dev/null << EOF
[Unit]
Description=RØDECaster Pro 2 Virtual Audio Driver
After=pipewire.service wireplumber.service
Wants=pipewire.service wireplumber.service

[Service]
Type=simple
ExecStart=/usr/bin/python3 ${INSTALL_DIR}/rodecaster_daemon.py
Restart=on-failure
RestartSec=5

[Install]
WantedBy=default.target
EOF

    systemctl --user daemon-reload
    systemctl --user enable rodecaster-vad.service
    systemctl --user start rodecaster-vad.service

    success "Service installed and started."
}

install_desktop_entry() {
    info "Installing desktop launcher..."

    local app_dir="$HOME/.local/share/applications"
    mkdir -p "$app_dir"

    tee "$app_dir/rodecaster-control.desktop" > /dev/null << EOF
[Desktop Entry]
Name=RØDECaster Control Panel
Comment=Virtual Audio Driver for RØDECaster Pro 2
Exec=/usr/bin/python3 ${INSTALL_DIR}/rodecaster_gtk_gui.py
Icon=audio-card
Terminal=false
Type=Application
Categories=AudioVideo;Audio;
EOF

    chmod +x "$INSTALL_DIR/rodecaster_gtk_gui.py"
    update-desktop-database "$app_dir" 2>/dev/null || true

    success "Desktop launcher installed."
}

cmd_install() {
    banner
    check_root
    check_dependencies

    if [[ -d "$INSTALL_DIR" ]]; then
        warn "Install directory already exists at $INSTALL_DIR."
        read -rp "Reinstall? This will overwrite local files. [y/N] " confirm
        [[ "$confirm" =~ ^[Yy]$ ]] || { info "Aborted."; exit 0; }
        rm -rf "$INSTALL_DIR"
    fi

    info "Cloning repository..."
    git clone "$REPO_URL" "$INSTALL_DIR"
    success "Repository cloned to $INSTALL_DIR"

    install_udev_rules
    install_service
    install_desktop_entry

    echo ""
    echo -e "${GREEN}╔══════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║         Installation Complete!           ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════╝${NC}"
    echo ""
    info "Service status:"
    systemctl --user status rodecaster-vad.service --no-pager || true
    echo ""
    info "Launch the GUI from your app menu: 'RØDECaster Control Panel'"
    info "Or run: python3 $INSTALL_DIR/rodecaster_gtk_gui.py"
    echo ""
    warn "If the Rodecaster isn't detected, replug its USB cable."
}

cmd_update() {
    banner
    check_root

    if [[ ! -d "$INSTALL_DIR" ]]; then
        error "Not installed. Run '$0 install' first."
    fi

    info "Stopping service..."
    systemctl --user stop rodecaster-vad.service || true

    info "Pulling latest changes from GitHub..."
    cd "$INSTALL_DIR"
    git fetch origin
    local current
    current=$(git rev-parse HEAD)
    git pull origin main

    local updated
    updated=$(git rev-parse HEAD)

    if [[ "$current" == "$updated" ]]; then
        success "Already up to date."
    else
        success "Updated to $(git rev-parse --short HEAD)."
        # Re-run install steps in case service/rules changed
        install_udev_rules
        install_service
        install_desktop_entry
    fi

    info "Restarting service..."
    systemctl --user daemon-reload
    systemctl --user restart rodecaster-vad.service

    echo ""
    success "Update complete!"
    systemctl --user status rodecaster-vad.service --no-pager || true
}

cmd_uninstall() {
    banner
    check_root

    warn "This will remove the service, udev rules, desktop entry, and the install directory."
    read -rp "Are you sure? [y/N] " confirm
    [[ "$confirm" =~ ^[Yy]$ ]] || { info "Aborted."; exit 0; }

    info "Stopping and disabling service..."
    systemctl --user stop rodecaster-vad.service 2>/dev/null || true
    systemctl --user disable rodecaster-vad.service 2>/dev/null || true
    rm -f "$SERVICE_DIR/rodecaster-vad.service"
    systemctl --user daemon-reload

    info "Removing udev rules..."
    sudo rm -f "$RULES_FILE"
    sudo udevadm control --reload-rules

    info "Removing desktop entry..."
    rm -f "$HOME/.local/share/applications/rodecaster-control.desktop"

    info "Removing install directory..."
    rm -rf "$INSTALL_DIR"

    success "Uninstalled successfully."
}

cmd_status() {
    echo ""
    info "Service status:"
    systemctl --user status rodecaster-vad.service --no-pager || true
    echo ""
    info "Virtual audio sinks:"
    pactl list short sinks | grep -i rode || echo "  None found."
    echo ""
    info "USB device:"
    lsusb | grep -i rode || echo "  Not detected."
    echo ""
    info "HID permissions:"
    ls -la /dev/hidraw* 2>/dev/null || echo "  No hidraw devices found."
}

usage() {
    banner
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  install    - Install the driver, service, and GUI"
    echo "  update     - Pull latest changes from GitHub and restart"
    echo "  uninstall  - Remove everything"
    echo "  status     - Check service, sinks, and device"
    echo ""
}

case "${1:-}" in
    install)   cmd_install   ;;
    update)    cmd_update    ;;
    uninstall) cmd_uninstall ;;
    status)    cmd_status    ;;
    *)         usage         ;;
esac
