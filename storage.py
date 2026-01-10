import json
import os
import sys

def get_config_path():
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, "hawkeye_config.json")

CONFIG_FILE = get_config_path()

def save_config(x_range, y_range, sleep_mode, debug_mode):
    data = {
        "x_range": x_range,
        "y_range": y_range,
        "check_sleep": sleep_mode,
        "debug_mode": debug_mode
    }
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(data, f, indent=4)
    except Exception:
        pass

def load_config():
    if not os.path.exists(CONFIG_FILE):
        return None
    try:
        with open(CONFIG_FILE, 'r') as f:
            data = json.load(f)
            if "check_sleep" not in data: data["check_sleep"] = False
            if "debug_mode" not in data: data["debug_mode"] = False
            return data
    except Exception:
        return None