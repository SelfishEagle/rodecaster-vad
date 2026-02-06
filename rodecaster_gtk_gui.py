#!/usr/bin/env python3
"""
RØDECaster Control Panel - Fixed sink name lookup
"""

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, GLib
import subprocess
import hid
import re

VENDOR_ID = 0x19f7
PRODUCT_ID = 0x0072

class FaderControl(Gtk.Box):
    """Individual fader with app routing - supports multiple apps!"""
    
    def __init__(self, fader_num, name, icon, sink_name):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.fader_num = fader_num
        self.sink_name = sink_name
        
        self.set_margin_top(10)
        self.set_margin_bottom(10)
        self.set_margin_start(10)
        self.set_margin_end(10)
        
        # Header with icon and name
        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        header_icon = Gtk.Label(label=icon)
        header_icon.set_markup(f"<span font='24'>{icon}</span>")
        header_box.append(header_icon)
        
        header_text = Gtk.Label(label=f"Fader {fader_num}: {name}")
        header_text.add_css_class("title-3")
        header_box.append(header_text)
        
        self.append(header_box)
        
        # Currently routed apps - scrollable list
        apps_frame = Gtk.Frame()
        apps_frame.set_label("Apps on this fader:")
        
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_min_content_height(80)
        scrolled.set_max_content_height(150)
        
        self.current_apps_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        self.current_apps_box.set_margin_top(5)
        self.current_apps_box.set_margin_bottom(5)
        self.current_apps_box.set_margin_start(5)
        self.current_apps_box.set_margin_end(5)
        
        # Default empty message
        self.empty_label = Gtk.Label(label="No apps routed")
        self.empty_label.add_css_class("dim-label")
        self.current_apps_box.append(self.empty_label)
        
        scrolled.set_child(self.current_apps_box)
        apps_frame.set_child(scrolled)
        self.append(apps_frame)
        
        # Add app section
        add_label = Gtk.Label(label="Add app to this fader:")
        add_label.set_xalign(0)
        add_label.set_margin_top(5)
        self.append(add_label)
        
        self.app_dropdown = Gtk.DropDown()
        self.app_dropdown.connect("notify::selected", self.on_app_selected)
        self.append(self.app_dropdown)
        
        # Store app list
        self.app_ids = {}
        self.routed_apps = []
    
    def refresh_apps(self, apps_data, sink_map):
        """Refresh the list of available apps
        apps_data is list of (app_name, sink_input_id, current_sink_id)
        sink_map is dict of {sink_id: sink_name}
        """
        # Build new list
        app_names = ["-- Select App to Add --"]
        self.app_ids = {}
        self.routed_apps = []
        
        print(f"\n=== Fader {self.fader_num} ({self.sink_name}) ===")
        
        for app_name, sink_input_id, current_sink_id in apps_data:
            app_names.append(app_name)
            
            # Look up the sink name from ID
            current_sink_name = sink_map.get(current_sink_id, f"unknown-{current_sink_id}")
            
            self.app_ids[app_name] = (sink_input_id, current_sink_name)
            
            print(f"  App: {app_name}")
            print(f"    Sink ID: {current_sink_id}")
            print(f"    Sink Name: {current_sink_name}")
            print(f"    Match: {self.sink_name in current_sink_name}")
            
            # Check if routed to this fader
            if self.sink_name in current_sink_name:
                self.routed_apps.append(app_name)
                print(f"    ✓ ROUTED TO THIS FADER")
        
        # Update dropdown
        string_list = Gtk.StringList()
        for name in app_names:
            string_list.append(name)
        self.app_dropdown.set_model(string_list)
        
        # Update display of routed apps
        self.update_routed_apps_display()
    
    def update_routed_apps_display(self):
        """Update the visual list of apps on this fader"""
        # Clear current display
        while True:
            child = self.current_apps_box.get_first_child()
            if child is None:
                break
            self.current_apps_box.remove(child)
        
        if not self.routed_apps:
            # Show empty message
            self.empty_label = Gtk.Label(label="No apps routed\n(Add apps using dropdown below)")
            self.empty_label.add_css_class("dim-label")
            self.current_apps_box.append(self.empty_label)
        else:
            # Show each app with a nice label
            for app in self.routed_apps:
                app_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
                app_box.set_margin_top(3)
                app_box.set_margin_bottom(3)
                
                # Icon/indicator
                indicator = Gtk.Label(label="🔊")
                app_box.append(indicator)
                
                # App name
                app_label = Gtk.Label(label=app)
                app_label.set_xalign(0)
                app_label.set_hexpand(True)
                app_label.set_wrap(True)
                app_box.append(app_label)
                
                # Add a subtle background
                app_box.add_css_class("card")
                
                self.current_apps_box.append(app_box)
    
    def on_app_selected(self, dropdown, param):
        selected = dropdown.get_selected()
        if selected == 0:  # "-- Select App to Add --"
            return
        
        model = dropdown.get_model()
        app_name = model.get_string(selected)
        
        if app_name in self.app_ids:
            sink_input_id, _ = self.app_ids[app_name]
            self.route_app(sink_input_id, app_name)
    
    def route_app(self, sink_input_id, app_name):
        """Route an app to this fader's sink"""
        try:
            subprocess.run([
                'pactl', 'move-sink-input',
                str(sink_input_id),
                self.sink_name
            ], check=True)
            
            print(f"✓ Routed {app_name} to {self.sink_name}")
            
            # Reset dropdown
            self.app_dropdown.set_selected(0)
            
            # Force immediate refresh
            GLib.timeout_add(500, lambda: self.parent_refresh() or False)
            
        except subprocess.CalledProcessError as e:
            print(f"Failed to route app: {e}")
    
    def parent_refresh(self):
        """Callback to trigger parent refresh"""
        pass


class RodecasterWindow(Gtk.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.set_title("RØDECaster Control Panel")
        self.set_default_size(950, 750)
        
        # Main scrolled window
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        
        # Main box
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        main_box.set_margin_top(20)
        main_box.set_margin_bottom(20)
        main_box.set_margin_start(20)
        main_box.set_margin_end(20)
        
        # Header
        header = Gtk.Label(label="RØDECaster Pro 2 Control Panel")
        header.add_css_class("title-1")
        main_box.append(header)
        
        # Status group
        status_frame = Gtk.Frame()
        status_frame.set_label("Status")
        status_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        status_box.set_margin_top(10)
        status_box.set_margin_bottom(10)
        status_box.set_margin_start(10)
        status_box.set_margin_end(10)
        
        self.service_label = Gtk.Label(label="Service: Checking...")
        self.device_label = Gtk.Label(label="Device: Checking...")
        status_box.append(self.service_label)
        status_box.append(self.device_label)
        status_frame.set_child(status_box)
        main_box.append(status_frame)
        
        # Service controls
        controls_frame = Gtk.Frame()
        controls_frame.set_label("Service Control")
        controls_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        controls_box.set_margin_top(10)
        controls_box.set_margin_bottom(10)
        controls_box.set_margin_start(10)
        controls_box.set_margin_end(10)
        
        start_btn = Gtk.Button(label="▶ Start")
        start_btn.connect("clicked", self.on_start)
        controls_box.append(start_btn)
        
        restart_btn = Gtk.Button(label="🔄 Restart")
        restart_btn.connect("clicked", self.on_restart)
        controls_box.append(restart_btn)
        
        stop_btn = Gtk.Button(label="⏹ Stop")
        stop_btn.connect("clicked", self.on_stop)
        controls_box.append(stop_btn)
        
        refresh_btn = Gtk.Button(label="🔄 Refresh Apps")
        refresh_btn.connect("clicked", lambda x: self.refresh_apps())
        controls_box.append(refresh_btn)
        
        controls_frame.set_child(controls_box)
        main_box.append(controls_frame)
        
        # Faders
        faders_frame = Gtk.Frame()
        faders_frame.set_label("App Routing - Multiple Apps Per Fader Supported!")
        faders_grid = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=15)
        faders_grid.set_homogeneous(True)
        
        # Create three fader controls
        self.fader1 = FaderControl(1, "Chat", "🎧", "rodecaster_chat")
        self.fader2 = FaderControl(2, "Game", "🎮", "rodecaster_game")
        self.fader3 = FaderControl(3, "Music", "🎵", "rodecaster_music")
        
        # Set parent refresh callback
        self.fader1.parent_refresh = self.refresh_apps
        self.fader2.parent_refresh = self.refresh_apps
        self.fader3.parent_refresh = self.refresh_apps
        
        faders_grid.append(self.fader1)
        faders_grid.append(self.fader2)
        faders_grid.append(self.fader3)
        
        faders_frame.set_child(faders_grid)
        main_box.append(faders_frame)
        
        # Instructions
        instructions = Gtk.Label()
        instructions.set_markup(
            "<b>💡 How to use:</b>\n"
            "1. Play audio in apps (Firefox, Spotify, Discord, games, etc.)\n"
            "2. Select app from dropdown to add it to a fader\n"
            "3. Add MULTIPLE apps to the same fader - they mix together!\n"
            "4. Control the master volume with your physical Rodecaster fader!\n\n"
            "<small>Check the terminal for debug output</small>"
        )
        instructions.set_wrap(True)
        instructions.set_justify(Gtk.Justification.CENTER)
        instructions.add_css_class("dim-label")
        main_box.append(instructions)
        
        scrolled.set_child(main_box)
        self.set_child(scrolled)
        
        # Auto-update timers
        GLib.timeout_add_seconds(2, self.update_status)
        GLib.timeout_add_seconds(3, self.refresh_apps)
        self.update_status()
        self.refresh_apps()
    
    def get_sink_map(self):
        """Build a map of sink ID to sink name"""
        try:
            result = subprocess.run(
                ['pactl', 'list', 'short', 'sinks'],
                capture_output=True, text=True
            )
            
            sink_map = {}
            for line in result.stdout.strip().split('\n'):
                parts = line.split()
                if len(parts) >= 2:
                    sink_id = parts[0]
                    sink_name = parts[1]
                    sink_map[sink_id] = sink_name
            
            print(f"\n=== Sink Map ===")
            for sid, sname in sink_map.items():
                print(f"  {sid} → {sname}")
            
            return sink_map
            
        except Exception as e:
            print(f"Error getting sink map: {e}")
            return {}
    
    def get_playing_apps(self):
        """Get list of apps currently playing audio"""
        try:
            result = subprocess.run(
                ['pactl', 'list', 'sink-inputs'],
                capture_output=True, text=True
            )
            
            apps = []
            current_id = None
            current_name = None
            current_sink = None
            
            for line in result.stdout.split('\n'):
                if 'Sink Input #' in line:
                    if current_id and current_name:
                        apps.append((current_name, current_id, current_sink or "unknown"))
                    current_id = int(line.split('#')[1])
                    current_name = None
                    current_sink = None
                
                elif 'application.name' in line:
                    current_name = line.split('=')[1].strip().strip('"')
                
                elif line.strip().startswith('Sink:') and 'media.name' not in line:
                    # Get the sink ID (just the number)
                    current_sink = line.split('Sink:')[1].strip()
            
            # Add last one
            if current_id and current_name:
                apps.append((current_name, current_id, current_sink or "unknown"))
            
            print(f"\n=== Found {len(apps)} playing apps ===")
            for name, id, sink in apps:
                print(f"  {name} (#{id}) → Sink {sink}")
            
            return apps
            
        except Exception as e:
            print(f"Error getting apps: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def refresh_apps(self):
        """Refresh app lists in all faders"""
        sink_map = self.get_sink_map()
        apps_data = self.get_playing_apps()
        self.fader1.refresh_apps(apps_data, sink_map)
        self.fader2.refresh_apps(apps_data, sink_map)
        self.fader3.refresh_apps(apps_data, sink_map)
        return True  # Keep timer running
    
    def update_status(self):
        """Update device and service status"""
        # Check service
        result = subprocess.run(
            ['systemctl', '--user', 'is-active', 'rodecaster-vad.service'],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            self.service_label.set_label("Service: 🟢 Running")
        else:
            self.service_label.set_label("Service: ⚫ Stopped")
        
        # Check device
        try:
            devices = hid.enumerate(VENDOR_ID, PRODUCT_ID)
            if devices:
                self.device_label.set_label("Device: 🟢 Connected")
            else:
                self.device_label.set_label("Device: ❌ Not Found")
        except:
            self.device_label.set_label("Device: ❓ Unknown")
        
        return True
    
    def on_start(self, button):
        subprocess.run(['systemctl', '--user', 'start', 'rodecaster-vad.service'])
        GLib.timeout_add(1000, self.update_status)
    
    def on_restart(self, button):
        subprocess.run(['systemctl', '--user', 'restart', 'rodecaster-vad.service'])
        GLib.timeout_add(1000, self.update_status)
    
    def on_stop(self, button):
        subprocess.run(['systemctl', '--user', 'stop', 'rodecaster-vad.service'])
        GLib.timeout_add(1000, self.update_status)


class RodecasterApp(Adw.Application):
    def __init__(self):
        super().__init__(application_id="com.selfisheagle.rodecaster")
    
    def do_activate(self):
        win = RodecasterWindow(application=self)
        win.present()


def main():
    app = RodecasterApp()
    app.run(None)


if __name__ == '__main__':
    main()
