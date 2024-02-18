# api_handler.py
import requests
import os
import logging
from .config_handler import load_config

# VIGIL_API_BASE_URL = "http://127.0.0.1:8000/api/v1"
# VIGIL_API_BASE_URL = "https://develop.vijil.ai/api/v1"
VIGIL_API_BASE_URL = "https://score.vijil.ai/api/v1"

# Set up logging
HIDDEN_DIR_NAME = ".vijil"
LOG_FILE_NAME = "vijil.log"
LOG_FILE_PATH = os.path.join(os.path.expanduser('~'), HIDDEN_DIR_NAME, LOG_FILE_NAME)
os.makedirs(os.path.dirname(LOG_FILE_PATH), exist_ok=True)
logging.basicConfig(level=logging.ERROR, filename=LOG_FILE_PATH, filemode='a',
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_headers():
    username, token = load_config()
    if not username or not token:
        raise ValueError("To proceed, please log in by using the 'login' command..")
    
    return {
        "username": username,
        "clitoken": token,
    }

def make_api_request(endpoint, method="get", params=None, data=None):
    url = f"{VIGIL_API_BASE_URL}/{endpoint}"
    headers = get_headers()
    
    try:
        if method.lower() == "get":
            response = requests.get(url, params=params, headers=headers)

        elif method.lower() == "post":
            response = requests.post(url, json=data, params=params, headers=headers)
        else:
            raise ValueError("Invalid HTTP method. Use 'get' or 'post'.")

        response.raise_for_status()
        return response.json()

    except requests.exceptions.HTTPError as http_err:
        error_detail = response.json()
        logger.error(f"{error_detail}")
        raise ValueError(f"{error_detail.get('detail')}")
    except requests.exceptions.RequestException as req_err:
        logger.error(f"Request error occurred: {req_err}")
        raise ValueError(f"Error during file download: {req_err}")
    except Exception as e:
        logger.error(f"Error during API request: {e}")
        raise ValueError(f"Something went wrong. Check the logs for details.")

def send_evaluation_request(model_type, model_name, probes, generations, job_name, deployment_type, token):
    endpoint = "evaluations/"
    data = {
        "model_type": model_type,
        "model_name": model_name,
        "probes": probes,
        "generations": generations,
        "job_name": job_name,
        "dType": deployment_type
    }
    if token != "":
        data["token"] = token
    return make_api_request(endpoint, method="post", data=data)

def job_status_request(id):
    endpoint = "evaluations/job_status"
    params = {"uid": id}
    return make_api_request(endpoint, params=params)

def stop_job_request(id):
    endpoint = "evaluations/stop"
    params = {"uid": id}
    return make_api_request(endpoint, method="post", params=params)

def stop_all_job_request():
    endpoint = "evaluations/stopall"
    return make_api_request(endpoint, method="post")

def delete_job_request(id):
    endpoint = "evaluations/remove"
    params = {"uid": id}
    return make_api_request(endpoint, method="post", params=params)

def download_report_request(file_id):
    try:
        download_url = f"{VIGIL_API_BASE_URL}/evaluations/download_file?file_id={file_id}"
        response = requests.get(download_url)
        response.raise_for_status()

        filename = response.headers.get('Content-Disposition', '').split('filename=')[1].strip('"')

        with open(filename, 'wb') as file:
            file.write(response.content)

        return f"File downloaded successfully: {filename}"

    except requests.exceptions.HTTPError as http_err:
        error_detail = response.json()
        logger.error(f"{error_detail}")
        raise ValueError(f"{error_detail.get('detail')}")
    except requests.exceptions.RequestException as req_err:
        logger.error(f"Request error occurred: {req_err}")
        raise ValueError(f"Error during file download: {req_err}")

def list_job_request():
    endpoint = "jobs/"
    return make_api_request(endpoint)

def get_job_detail_request(id):
    endpoint = "jobs/detail"
    params = {"job_id": id}
    return make_api_request(endpoint, params=params)

def model_token_request(source, name, token, isPrimary):
    endpoint = f"integrations/"
    data = {
        "token": token,
        "name": name,
        "type": source,
        "isPrimary": isPrimary
    }
    return make_api_request(endpoint, method="post", data=data)

def get_model_token_request():
    endpoint = "integrations/"
    return make_api_request(endpoint)

def check_jobs_progress(id):
    endpoint = "evaluations/job_progress"
    params = {"uid": id}
    return make_api_request(endpoint, method="get", params=params)
