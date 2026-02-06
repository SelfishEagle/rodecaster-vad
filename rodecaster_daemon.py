#!/usr/bin/env python3
"""
RØDECaster Virtual Audio Driver Daemon
CORRECT MULTITRACK MAPPING:
  Chat  → pro-output-0 (Fader 1)
  Game  → pro-output-1 AUX2,AUX3 (Fader 2)
  Music → pro-output-1 AUX4,AUX5 (Fader 3)
"""

import hid
import subprocess
import time
import logging
import signal

VENDOR_ID = 0x19f7
PRODUCT_ID = 0x0072

VIRTUAL_SINKS = [
    {
        "name": "chat",
        "desc": "Chat (Discord)",
        "target": "alsa_output.usb-R__DE_RODECaster_Pro_II_GV0147346-00.pro-output-0",
        "channels": "FL FR",
        "use_dont_remix": False,
        "fader": 1
    },
    {
        "name": "game",
        "desc": "Game Output",
        "target": "alsa_output.usb-R__DE_RODECaster_Pro_II_GV0147346-00.pro-output-1",
        "channels": "AUX2 AUX3",
        "use_dont_remix": True,
        "fader": 2
    },
    {
        "name": "music",
        "desc": "Music Output",
        "target": "alsa_output.usb-R__DE_RODECaster_Pro_II_GV0147346-00.pro-output-1",
        "channels": "AUX4 AUX5",
        "use_dont_remix": True,
        "fader": 3
    },
]

class RodecasterVAD:
    def __init__(self):
        self.device = None
        self.loopback_pids = []
        self.running = True
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        self.logger.info("Shutdown signal received")
        self.running = False
    
    def detect_device(self):
        devices = hid.enumerate(VENDOR_ID, PRODUCT_ID)
        return len(devices) > 0
    
    def open_device(self):
        try:
            self.device = hid.device()
            self.device.open(VENDOR_ID, PRODUCT_ID)
            
            manufacturer = self.device.get_manufacturer_string()
            product = self.device.get_product_string()
            serial = self.device.get_serial_number_string()
            
            self.logger.info(f"Connected to {manufacturer} {product} (S/N: {serial})")
            return True
        except Exception as e:
            self.logger.error(f"Failed to open device: {e}")
            return False
    
    def read_device_status(self):
        if not self.device:
            return None
        try:
            command = [0x01, 0x49] + [0x00] * 62
            self.device.write(command)
            response = self.device.read(64, timeout_ms=1000)
            if response and len(response) >= 4:
                self.logger.debug(f"Device status: {bytes(response[:4]).hex()}")
                return response
        except Exception as e:
            self.logger.error(f"Failed to read status: {e}")
        return None
    
    def run_command(self, cmd):
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Command failed: {e.stderr}")
            return None
    
    def set_pro_audio_profile(self):
        """Ensure Rodecaster is in Pro Audio mode"""
        self.logger.info("Setting Rodecaster to Pro Audio profile...")
        cmd = "pactl set-card-profile alsa_card.usb-R__DE_RODECaster_Pro_II_GV0147346-00 pro-audio"
        self.run_command(cmd)
        time.sleep(1)
    
    def create_routed_sink(self, sink_config):
        """Create virtual sink with appropriate routing"""
        
        node_name = f"rodecaster_{sink_config['name']}"
        description = f"RØDECaster {sink_config['desc']}"
        target = sink_config['target']
        channels = sink_config['channels']
        fader = sink_config['fader']
        
        if sink_config['use_dont_remix']:
            cmd = f"""pw-loopback \
                --capture-props='media.class=Audio/Sink node.name={node_name} node.description="{description}" audio.position=[ FL FR ]' \
                --playback-props='node.target={target} audio.position=[ {channels} ] stream.dont-remix=true'"""
        else:
            cmd = f"""pw-loopback \
                --capture-props='media.class=Audio/Sink node.name={node_name} node.description="{description}" audio.position=[ FL FR ]' \
                --playback-props='node.target={target} audio.position=[ {channels} ]'"""
        
        proc = subprocess.Popen(
            cmd,
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True
        )
        
        if proc.pid:
            self.logger.info(f"✓ {description} → Fader {fader}")
            self.loopback_pids.append(proc.pid)
            time.sleep(0.3)
            return True
        else:
            self.logger.error(f"Failed to create {node_name}")
            return False
    
    def create_all_sinks(self):
        self.logger.info("Creating virtual audio devices...")
        
        self.set_pro_audio_profile()
        
        success_count = 0
        for sink in VIRTUAL_SINKS:
            if self.create_routed_sink(sink):
                success_count += 1
            time.sleep(0.2)
        
        self.logger.info(f"Created {success_count}/{len(VIRTUAL_SINKS)} virtual sinks")
        return success_count > 0
    
    def cleanup(self):
        self.logger.info("Cleaning up virtual devices...")
        
        for pid in self.loopback_pids:
            try:
                subprocess.run(f"kill {pid}", shell=True, stderr=subprocess.DEVNULL)
            except:
                pass
        
        self.loopback_pids.clear()
        
        if self.device:
            self.device.close()
            self.device = None
        
        self.logger.info("Cleanup complete")
    
    def run(self):
        self.logger.info("RØDECaster Virtual Audio Driver starting...")
        
        self.logger.info("Waiting for Rodecaster Pro 2...")
        while self.running and not self.detect_device():
            time.sleep(2)
        
        if not self.running:
            return
        
        self.logger.info("Device detected!")
        
        if not self.open_device():
            self.logger.error("Failed to open device, exiting")
            return
        
        status = self.read_device_status()
        if status:
            self.logger.info("Device status read successfully")
        
        if not self.create_all_sinks():
            self.logger.error("Failed to create virtual devices")
            self.cleanup()
            return
        
        self.logger.info("")
        self.logger.info("=" * 70)
        self.logger.info("✓ RØDECaster Virtual Audio Driver READY!")
        self.logger.info("=" * 70)
        self.logger.info("Virtual Outputs → Your Rodecaster Faders:")
        self.logger.info("")
        self.logger.info("  🎧 RØDECaster Chat (Discord) → Fader 1 (Chat)")
        self.logger.info("  🎮 RØDECaster Game Output    → Fader 2 (Game)")
        self.logger.info("  🎵 RØDECaster Music Output   → Fader 3 (Music)")
        self.logger.info("")
        self.logger.info("PERFECT! Each app has its own fader! 🎛️")
        self.logger.info("")
        self.logger.info("HOW TO USE:")
        self.logger.info("  1. Open pavucontrol")
        self.logger.info("  2. Route Discord → RØDECaster Chat (Discord)")
        self.logger.info("  3. Route Games → RØDECaster Game Output")
        self.logger.info("  4. Route Spotify → RØDECaster Music Output")
        self.logger.info("  5. Control each with its physical fader!")
        self.logger.info("")
        self.logger.info("EXACTLY like the Windows driver! ✨")
        self.logger.info("=" * 70)
        
        try:
            while self.running:
                if not self.detect_device():
                    self.logger.warning("Device disconnected!")
                    break
                time.sleep(5)
        except KeyboardInterrupt:
            self.logger.info("Interrupted by user")
        finally:
            self.cleanup()

def main():
    daemon = RodecasterVAD()
    daemon.run()

if __name__ == "__main__":
    main()
