import os
import sys
import json
import hashlib
import datetime
import platform
import subprocess
import requests

class SubscriptionManager:
    def __init__(self):
        self.config_file = "subscription_config.json"
        self.device_id = self.get_device_id()
        self.subscription_key = self.generate_subscription_key()

    def get_mac_address(self):
        try:
            if platform.system() == "Linux":
                result = subprocess.run(['ip', 'link', 'show'], capture_output=True, text=True)
                lines = result.stdout.split('\n')
                for line in lines:
                    if 'link/ether' in line and '00:00:00:00:00:00' not in line:
                        mac = line.split()[1]
                        return mac.replace(':', '')
            else:
                result = subprocess.run(['ipconfig', '/all'], capture_output=True, text=True)
                lines = result.stdout.split('\n')
                for line in lines:
                    if 'Physical Address' in line:
                        mac = line.split(':')[-1].strip()
                        return mac.replace('-', '')
        except:
            return "000000000000"

    def get_device_id(self):
        try:
            info = platform.uname()
            system_info = f"{info.system}-{info.machine}-{info.release}"
            mac = self.get_mac_address()
            combined = f"{system_info}:{mac}"
            return hashlib.md5(combined.encode()).hexdigest()[:16]
        except:
            return "DEVICE_ID_ERROR"

    def generate_subscription_key(self):
        key_base = hashlib.md5(self.device_id.encode()).hexdigest()[:12]
        return f"SUB-{key_base.upper()}"

    def load_config(self):
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {}

    def save_config(self, config):
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except:
            pass

    def check_online_subscription(self, key):
        try:
            url = f"https://clone-api-93fm.onrender.com/api/check_key?key={key}"
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                return data.get("approved", False)
            return False
        except Exception:
            return False

    def check_subscription(self):
        online = self.check_online_subscription(self.subscription_key)
        if online:
            return True
        config = self.load_config()
        if self.device_id in config:
            device_config = config[self.device_id]
            if device_config.get('subscription_key') == self.subscription_key:
                return device_config.get('approved', False)
        return False

    def create_subscription(self):
        config = self.load_config()
        config[self.device_id] = {
            'subscription_key': self.subscription_key,
            'approved': False,
            'created_at': str(datetime.datetime.now())
        }
        self.save_config(config)

    def display_subscription_info(self):
        print("\x1b[1;92m[~] WELCOME to Boostology BD 🚀✨\x1b[0m")
        print("\x1b[1;96m[~] CREATOR: Emam Hasan Bulbul\x1b[0m")
        print("\x1b[1;96m[~] OPERATOR: Yasin Ali Mondol\x1b[0m")
        print()
        print("\x1b[1;92m[~] YOUR KEY : \x1b[1;97m{}\x1b[0m".format(self.subscription_key))
        print("\x1b[1;93m    👉 Copy this key and send it to the operator for approval\x1b[0m")
        print("\x1b[1;92m[~] PLEASE CONTACT: Yasin Ali Mondol\x1b[0m")
        input("\x1b[1;92m[~] PRESS ENTER TO EXIT\x1b[0m")
        sys.exit()
