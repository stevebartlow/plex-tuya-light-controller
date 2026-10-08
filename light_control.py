import tinytuya
import logging
from config import LIGHTS, LOAD_FROM_JSON

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LightController:
    def __init__(self):
        self.devices = []
        self.saved_states = {} # dev_id -> status dps
        self.connect_all()

    def connect_all(self):
        # Load from config list first
        start_devices = LIGHTS.copy()
        
        # Optionally load from devices.json if wizard was run
        if LOAD_FROM_JSON:
            try:
                import json
                with open("devices.json") as f:
                    json_devices = json.load(f)
                    # Convert tinytuya json format to our simple list if needed
                    # tinytuya format: [{'id': '...', 'key': '...', 'ip': '...', ...}]
                    for d in json_devices:
                        # Check if already in start_devices (prevent duplicates)
                        if any(sd.get('id') == d.get('id') for sd in start_devices):
                            continue
                        
                        start_devices.append({
                            'id': d.get('id'),
                            'ip': d.get('ip'), # Might be empty if not scanned
                            'key': d.get('key'),
                            'version': d.get('version', 3.3),
                            'name': d.get('name', 'Unknown')
                        })
            except FileNotFoundError:
                pass

        if not start_devices:
            print("No lights configured. Mock Mode active.", flush=True)
            return

        import socket
        socket.setdefaulttimeout(3) # Set global timeout for sockets to 3 seconds

        for d_conf in start_devices:
            print(f"Connecting to {d_conf.get('name', d_conf.get('id', 'Unknown'))} at {d_conf.get('ip')}...", flush=True)
            try:
                # If IP is missing, we can't connect directly efficiently without scanning
                # But let's assume IP is provided or cached
                if not d_conf.get('ip'):
                    print(f"Skipping device {d_conf.get('id')} - No IP address", flush=True)
                    continue
                    
                d = tinytuya.BulbDevice(
                    dev_id=d_conf['id'],
                    address=d_conf['ip'],
                    local_key=d_conf['key'], 
                    version=float(d_conf.get('version', 3.3)),
                    connection_timeout=2, 
                    dev_type='default' # Bypasses auto-detect which fails in docker
                )
                # Force socket persistence and disable auto-retry scan which fails in isolated docker
                d.set_socketPersistent(True) 
                
                self.devices.append(d)
                print(f"Connected to light: {d_conf.get('name', d_conf['id'])}", flush=True)
            except Exception as e:
                print(f"Failed to connect to light {d_conf.get('id')}: {e}", flush=True)

    def save_state(self):
        """Saves the current state of all devices if not already saved."""
        if not self.devices:
            logger.info("MOCK MODE: Saving light states")
            return

        if self.saved_states:
            logger.info("States already saved, skipping.")
            return

        logger.info(f"Saving state for {len(self.devices)} lights")
        for dev in self.devices:
            try:
                status = dev.status()
                if status and 'dps' in status:
                    self.saved_states[dev.id] = status['dps']
                    logger.info(f"Saved state for {dev.id}")
                else:
                    logger.warning(f"Could not get status for {dev.id}")
            except Exception as e:
                logger.error(f"Error saving state for device {dev.id}: {e}")

    def restore_state(self):
        """Restores the previously saved state of all devices."""
        if not self.devices:
            logger.info("MOCK MODE: Restoring light states")
            return

        if not self.saved_states:
            logger.info("No saved states to restore. Falling back to white.")
            self.set_white()
            return

        self.set_white()


        #logger.info(f"Restoring state for {len(self.saved_states)} lights")
        #for dev in self.devices:
        #    if dev.id in self.saved_states:
        #        try:
        #            state = self.saved_states[dev.id]
                    # Use set_status to apply all DPS at once (on/off, brightness, color, etc)
        #            dev.set_status(state)
        #            logger.info(f"Restored state for {dev.id}")
        #        except Exception as e:
        #            logger.error(f"Error restoring state for device {dev.id}: {e}")
        #    else:
        #        logger.warning(f"No saved state for device {dev.id}, resetting to white")
        #        dev.set_white()
        
        # Clear saved states after restoration
        self.saved_states = {}

    def set_color(self, r, g, b):
        """Sets the light color to the given RGB values for ALL connected lights."""
        # Save state before first color change in a session
        self.save_state()

        if not self.devices:
            logger.info(f"MOCK MODE: Setting lights to RGB({r}, {g}, {b})")
            return

        logger.info(f"Setting {len(self.devices)} lights to RGB({r}, {g}, {b})")
        for dev in self.devices:
            try:
                dev.set_colour(r, g, b)
            except Exception as e:
                logger.error(f"Error setting color for device {dev.id}: {e}")

    def set_white(self):
        """Resets all lights to white/normal mode."""
        if not self.devices:
            logger.info("MOCK MODE: Setting lights to White")
            return
        
        logger.info(f"Setting {len(self.devices)} lights to White")
        for dev in self.devices:
            try:
                dev.set_white()
            except Exception as e:
                logger.error(f"Error setting white for device {dev.id}: {e}")
