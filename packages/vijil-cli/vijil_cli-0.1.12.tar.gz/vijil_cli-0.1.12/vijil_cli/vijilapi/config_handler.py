import os
import json
from datetime import datetime, timedelta

HIDDEN_DIR_NAME = ".vijil"
CONFIG_FILE_NAME = "vijil_config.json"
CONFIG_FILE_PATH = os.path.join(os.path.expanduser('~'), HIDDEN_DIR_NAME, CONFIG_FILE_NAME)

def save_config(username, token):
    config_data = {"username": username, "token": token, "timestamp": datetime.utcnow().isoformat()}
    os.makedirs(os.path.dirname(CONFIG_FILE_PATH), exist_ok=True)
    with open(CONFIG_FILE_PATH, 'w') as config_file:
        json.dump(config_data, config_file)

def load_config():
    try:
        with open(CONFIG_FILE_PATH, 'r') as config_file:
            config_data = json.load(config_file)
            timestamp = datetime.fromisoformat(config_data.get("timestamp"))
            expiration_time = timestamp + timedelta(days=2)
            if datetime.utcnow() <= expiration_time:
                return config_data.get("username"), config_data.get("token")
            else:
                remove_config()
                return None, None
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        return None, None

def remove_config():
    try:
        os.remove(CONFIG_FILE_PATH)
        return None
    except FileNotFoundError:
        pass
