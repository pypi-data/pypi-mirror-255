# api_handler.py
import requests
import logging

from .config_handler import load_config

VIGIL_API_BASE_URL = "http://127.0.0.1:8000/api/v1"
# VIGIL_API_BASE_URL = "http://dockder-test-alb-2018306447.us-west-2.elb.amazonaws.com/api/v1"

# Set up logging
logging.basicConfig(level=logging.ERROR, filename='vijil.log', filemode='w',
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)



def custom_headers():
    """Customize headers for display."""
    return {
        "job_id": "Job ID",
        "task_id": "ID",
        "model_type": "Model Type",
        "model_name": "Model Name",
        "probe_group": "Probe Group",
        "status": "Status",
        "job_result": "Result",
        "start_time": "Start Time",
        "end_time": "End Time",
    }

def send_evaluation_request(model_type, model_name, probes, generations):
    url = f"{VIGIL_API_BASE_URL}/evaluations/"
    username, token = load_config()

    if not username or not token:
        raise ValueError("Username or token not found in configuration.")

    headers = {
        # "Authorization": f"Bearer {token}",
        "username": username,
        "clitoken": token,
    }

    data = {
        "model_type": model_type,
        "model_name": model_name,
        "probes": probes,
        "generations": generations,
    }

    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        return response.json()

    except Exception as e:
        logger.error(f"Error during API request: {e}")
        raise ValueError("An error occurred during the API request. Check the logs for details.")


def job_status_request(id):
    url = f"{VIGIL_API_BASE_URL}/evaluations/job_status"
    username, token = load_config()

    if not username or not token:
        raise ValueError("Username or token not found in configuration.")

    headers = {
        "username": username,
        "clitoken": token,
    }
    params = {"task_id": id}
    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        return response.json()

    except Exception as e:
        logger.error(f"Error during API request: {e}")
        raise ValueError("An error occurred during the API request. Check the logs for details.")
    
def stop_job_request(id):
    url = f"{VIGIL_API_BASE_URL}/evaluations/stop"
    username, token = load_config()

    if not username or not token:
        raise ValueError("Username or token not found in configuration.")

    headers = {
        "username": username,
        "clitoken": token,
    }
    params = {"task_id": id}
    try:
        response = requests.post(url, params=params, headers=headers)
        response.raise_for_status()
        return response.json()

    except Exception as e:
        logger.error(f"Error during API request: {e}")
        raise ValueError("An error occurred during the API request. Check the logs for details.")
    
def stop_all_job_request():
    url = f"{VIGIL_API_BASE_URL}/evaluations/stopall"
    username, token = load_config()

    if not username or not token:
        raise ValueError("Username or token not found in configuration.")

    headers = {
        "username": username,
        "clitoken": token,
    }

    try:
        response = requests.post(url, headers=headers)
        response.raise_for_status()
        return response.json()

    except Exception as e:
        logger.error(f"Error during API request: {e}")
        raise ValueError("An error occurred during the API request. Check the logs for details.")
    
def delete_job_request(id):
    url = f"{VIGIL_API_BASE_URL}/evaluations/remove"
    username, token = load_config()

    if not username or not token:
        raise ValueError("Username or token not found in configuration.")

    headers = {
        "username": username,
        "clitoken": token,
    }
    params = {"task_id": id}
    try:
        response = requests.post(url, params=params, headers=headers)
        response.raise_for_status()
        return response.json()

    except Exception as e:
        logger.error(f"Error during API request: {e.detail}")
        raise ValueError("An error occurred during the API request. Check the logs for details.")
    
def download_report_request(file_id):

    try:
        download_url = f"{VIGIL_API_BASE_URL}/evaluations/download_file?file_id={file_id}"
        response = requests.get(download_url)
        response.raise_for_status()

        filename = response.headers.get('Content-Disposition', '').split('filename=')[1].strip('"')

        with open(filename, 'wb') as file:
            file.write(response.content)

        return f"File downloaded successfully: {filename}"

    except requests.exceptions.RequestException as e:
        raise ValueError(f"Error during file download: {e}")
    
def list_job_request():

    jobs_url = f"{VIGIL_API_BASE_URL}/jobs/"
    try:
        username, token = load_config()

        if not username or not token:
            raise ValueError("Username or token not found in configuration.")

        headers = {
            "username": username,
            "clitoken": token,
        }

        response = requests.get(jobs_url, headers=headers)
        response.raise_for_status()
        jobs_data = response.json()

        if not jobs_data:
            return {
                "message": "No jobs found."
            }

        return {
            "table_data":jobs_data
        }
    
    except requests.exceptions.RequestException as e:
        raise ValueError(f"Error fetching jobs: {e}")
    
def get_job_detail_request(id):
    url = f"{VIGIL_API_BASE_URL}/jobs/detail"
    username, token = load_config()

    if not username or not token:
        raise ValueError("Username or token not found in configuration.")

    headers = {
        "username": username,
        "clitoken": token,
    }
    params = {"job_id": id}
    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        return response.json()

    except Exception as e:
        logger.error(f"Error during API request: {e}")
        raise ValueError("An error occurred during the API request. Check the logs for details.")