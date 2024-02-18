# commands.py
import click
import time
import random
import types
from datetime import datetime
from tabulate import tabulate
from vijil_cli.vijilapi.api_handler import (
    send_evaluation_request,
    job_status_request,
    stop_job_request,
    stop_all_job_request,
    delete_job_request,
    download_report_request,
    list_job_request,
    model_token_request,
    get_model_token_request,
    check_jobs_progress
)
from .options import *

def generate_default_job_name(job_list_data):
    words = ['dashing', 'devil', 'awesome', 'creative', 'innovative', 'wizard', 'spectacular']

    while True:
        selected_word = random.choice(words)
        random_two_digit_number = random.randint(0, 99)
        generated_job_name = f'{selected_word}{random_two_digit_number}'
        if not any(job['job_name'].lower() == generated_job_name.lower() for job in job_list_data):
            return generated_job_name

@click.command()
@click.option('--job-name', default='', prompt='Enter the job name or leave empty to generate a default name')
@click.option('--model-type', prompt='Choose the model type', type=click.Choice(MODEL_TYPE_CHOICES))
@click.option('--model-name', prompt='Enter the model name')
@click.option('--dimension', prompt='Choose the trust dimension', type=click.Choice(PROBES_CHOICES))
@click.option('--deployment-type', prompt='Choose the deployment type', type=click.Choice(DTYPE_CHOICES))
@click.option('--generations', default=1, prompt='Enter the number of generations', type=click.IntRange(1, 100))
@click.option('--token', default='', prompt='Enter a model token')
def run(job_name, model_type, model_name, dimension, deployment_type, generations, token):
    """Run the evaluation."""

    result = list_job_request()
    if job_name == '':
        job_name = generate_default_job_name(result)
    elif any(job['job_name'] == job_name for job in result):
        click.echo(f"Job name '{job_name}' is already in use. Please choose a different job name.")
        return
    if model_type != 'huggingface' and deployment_type == 'local':
        click.echo(f"Local deployment type is not allowed for model {model_type}.")
        return
    
    probes = PROBES_DIMENSIONS_MAPPING.get(dimension)
        

    click.echo(f"Running evaluation for model type: {model_type}, model name: {model_name}")

    try:
        result = send_evaluation_request(model_type, model_name, probes, generations, job_name, deployment_type, token)
        if result.get("task_id"):
            click.echo(f"Successfully Create Evaluation, Check Job Status by ID: {result.get('task_id')}")    
        else:
            click.echo(f"Response: {result}")

    except ValueError as e:
        click.echo(f"Error: {e}")


@click.command()
@click.option('--id', prompt='Enter ID that you received while creating evaluation', type=str)
def status(id):
    """Check Job Status By it's ID."""

    click.echo(f"Getting Job status for ID: {id}")

    try:
        result = job_status_request(id)
        if "job_result" in result:
            click.echo(f"Job Status: {result.get('status')}") 
            click.echo(f"Job Result: {result.get('job_result')}")
        elif "status" in result:
            click.echo(f"Job Status: {result.get('status')}") 
        elif isinstance(result, type([])) and len(result) > 0:
            click.echo("-" * 60)
            for job in result:
                click.echo(f"Job ID: {job.get('job_id', '')}")
                click.echo(f"Model Type: {job.get('model_type', '')}")
                click.echo(f"Model Name: {job.get('model_name', '')}")
                click.echo(f"Probe Group: {job.get('probe_group', '')}")
                click.echo("Probes:")
                for probe in job.get('probe', []):
                    click.echo(f"  - {probe}")

                click.echo("Detectors:")
                for detector in job.get('detector', []):
                    click.echo(f"  - {detector}")
                click.echo(f"Start Time: {format_datetime(job.get('start_time', ''))}")
                click.echo(f"Report: {job.get('report', '')}")
                click.echo(f"Hitlog: {job.get('hitlog', '')}")
                click.echo("-" * 60)
        else:
            click.echo("No Data Found.")

    except ValueError as e:
        click.echo(f"Error: {e}")

@click.command()
@click.option('--id', default='', help='Enter ID that you received while creating evaluation')
@click.option('-a', '--all', is_flag=True, help='Stop all running evaluations.')
def stop(id, all):
    """Stop Evaluation by it's Id or stop all evaluations."""

    if all:
        click.echo(f"Stopping all running evaluations.")
        try:
            result = stop_all_job_request()
            if result.get("status"):
                click.echo(f"Job Status: {result.get('status')}") 
        except ValueError as e:
            click.echo(f"Error: {e}")
    else:
        if not id:
            click.echo("Please provide the ID for stopping a specific job.")
            return
        click.echo(f"Stopping Evaluation of ID: {id}")
        try:
            result = stop_job_request(id)
            if result.get("status"):
                click.echo(f"Job Status: {result.get('status')}") 
        except ValueError as e:
            click.echo(f"Error: {e}")

@click.command()
@click.option('--id', prompt='Enter ID that you received while creating evaluation', type=str)
def delete(id):
    """Delete Evaluation by it's Id."""

    click.echo(f"Deleting evaluation of ID: {id}")

    try:
        result = delete_job_request(id)
        if result:
            click.echo(f"{result.get('message')}") 

    except ValueError as e:
        click.echo(f"Error: {e}")

@click.command()
@click.option('--file-id', prompt='Enter the Report/Hitlog ID')
def download(file_id):
    """Download a Report/Hitlog file by on its ID."""
    
    try:
        result = download_report_request(file_id)
        if result:
            click.echo(f"{result}") 

    except ValueError as e:
        click.echo(f"Error: {e}")

def format_datetime(datetime_str):
    """Format datetime from API response."""
    if datetime_str:
        try:
            dt = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
            return dt.strftime("%Y/%m/%d %H:%M")
        except ValueError:
            return datetime_str
    else:
        return datetime_str
    
def format_value(value, all_option):
    return value if all_option else (value[:10] + '...' if (value and len(value) > 10) else value)

@click.command()
@click.option('-a', '--all', is_flag=True, help='Show full values')
def list(all):
    """List all jobs."""

    try:
        result = list_job_request()
        if len(result) > 0:
            table_data = []
            for job in result:
                table_data.append([
                    job.get('id', ''),
                    format_value(job.get('model_type', ''), all),
                    format_value(job.get('model_name', ''), all),
                    format_value(job.get('probe_group', ''), all),
                    format_value(job.get('job_id', ''), all),
                    (job.get('status', '')),
                    format_value(job.get('job_result', ''), all),
                    (format_datetime(job.get('start_time', ''))),
                    (format_datetime(job.get('end_time', '')))
                ])

            headers = ["ID", "Model Type", "Model Name", "Probe Group", "Job ID", "Status", "Result", "Start Time", "End Time"]

            # colalign = 'center' if all else ['left'] * len(headers)
            colalign = ['left'] * len(headers)

            # tablefmt = "plain" if all else "pretty"
            tablefmt = "pretty"

            table = tabulate(table_data, headers=headers, tablefmt=tablefmt, colalign=colalign)
            click.echo(table)
        else:
            click.echo("No Jobs found.")

    except ValueError as e:
        click.echo(f"Error: {e}")

@click.command()
@click.option('--source', prompt='Choose source of token', type=click.Choice(MODEL_TYPE_CHOICES))
@click.option('--name', prompt='Enter the name of token')
@click.option('--token', prompt='Enter the token')
@click.option('--is-primary', prompt='Do you want to make this token as Default?', type=click.Choice(['yes', 'no']))
def integrations(source, name, token, is_primary):
    """Set Integration Token to Vijil."""
    isPrimary = "true" if is_primary == 'yes' else "false"
    try:
        result = model_token_request(MODEL_TYPE_MAPPING.get(source), name, token, isPrimary)
        if result:
            click.echo(f"SuccessFully Saved Integration Token.") 

    except ValueError as e:
        click.echo(f"Error: {e}")

@click.command()
def tokens():
    """Get Integration Tokens."""
    try:
        result = get_model_token_request()
        if len(result) > 0:
            table_data = []
            for token in result:
                table_data.append([
                    token.get('name', ''),
                    token.get('type', ''),
                    token.get('token', ''),
                    token.get('isPrimary', '')
                ])

            headers = ["Name", "Type", "Token", "isPrimary"]
            colalign = ['left'] * len(headers)
            tablefmt = "pretty"

            table = tabulate(table_data, headers=headers, tablefmt=tablefmt, colalign=colalign)
            click.echo(table)
        else:
            click.echo("No Tokens found.")

    except ValueError as e:
        click.echo(f"Error: {e}")

def find_job_by_task_id(job_list, target_task_id):
    for job in job_list:
        if job.get('id') == target_task_id:
            return job
    return None

@click.command()
@click.option('--id', prompt='Enter ID that you received while creating evaluation', type=str)
@click.option('--trail', is_flag=True, help='Print live logs for in-progress jobs')
def logs(id, trail):
    """Check logs for running jobs."""
    printed_lines = set()
    try:
        joblist = list_job_request()
        matched_job = find_job_by_task_id(joblist, id)
        if matched_job:
            if matched_job.get('status') == 'In Progress':
                if trail:
                    while True:
                        live_logs = check_jobs_progress(id)
                        for log in live_logs.get('progress'):
                            if log not in printed_lines:
                                print(log)
                                printed_lines.add(log)
                        time.sleep(5)
                else:
                    print("Job is still in progress. Use --trail to get live logs.")
            else:
                result = [matched_job.get('job_result')] if matched_job.get('status') == "Stopped" else matched_job.get('output')
                for item in result:
                    print(item)
        else:
            print("No matching job found.")

    except ValueError as e:
        error_detail = str(e)
        if error_detail == "400: Job is already completed.":
            joblist = list_job_request()
            matched_job = find_job_by_task_id(joblist, id)
            result = [matched_job.job_result] if matched_job.get('status') == "Stopped" else matched_job.get('output')
            for item in result:
                if item not in printed_lines:
                    print(log)
                    printed_lines.add(log)
        else:
            click.echo(f"Error: {error_detail}")