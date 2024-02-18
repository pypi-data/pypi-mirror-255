import json
from pytz import utc
import azure.functions as func
from azure.storage.filedatalake import DataLakeServiceClient
from azure.storage.blob import BlobServiceClient
from apscheduler.schedulers.background import BackgroundScheduler
import subprocess
import os
from .commons.db_helper import (
    persist_value,
    get_table_values,
    delete_table_values
)
import shutil
from github import Github
import requests
import datetime
import os
from logging_increff.function import *
import configparser
from .commons.constants import *

python_config = configparser.ConfigParser()
python_config.read("config.ini")

scheduler = BackgroundScheduler()
scheduler.configure(timezone=utc)
scheduler.start()


def create_folder(name):
    if not os.path.exists(str(name)):
        os.makedirs(str(name))


def delete_folder(name, job_id):
    shutil.rmtree(str(name), ignore_errors=True)
    add_info_logs(job_id, f"folder {name} deleted successfully")


def change_job_to_processing_state(job):
    job["start_time"] = str(datetime.datetime.now())
    job["status"] = PROCESSING
    persist_value(JOBS_TABLE, job["id"], job)
    persist_value(INTERIM_JOBS, job["id"],{'id':job["id"]})


def change_job_to_success_state(job):
    job["status"] = SUCCESS
    job["end_time"] = str(datetime.datetime.now())
    persist_value(JOBS_TABLE, job["id"], job)
    delete_table_values(INTERIM_JOBS, job["id"])


def change_job_to_failure_state(job, reason):
    job["status"] = FAILED
    job["end_time"] = str(datetime.datetime.now())
    job["reason"] = str(reason)
    persist_value(JOBS_TABLE, job["id"], job)
    delete_table_values(INTERIM_JOBS, job["id"])


def update_job(job):
    persist_value(JOBS_TABLE, job["id"], job)


def send_success_callback(url, output, error_data, job):
    if error_data != {}:
        send_failure_callback(url, "Script Failed", output, error_data, job)
        return
    output["caas_job_id"] = job["id"]
    add_info_logs(job["id"], "Hitting Success Callback")
    body = {
        "StatusCode": "200",
        "Output": {"output_data": output, "error_data": error_data},
    }
    add_info_logs(job["id"], f"Success message -> {str(body)}")
    job["callback_status"] = "200"
    update_job(job)
    response = requests.post(url, data=json.dumps(body))


def send_failure_callback(url, error, output_data, error_data, job):
    add_info_logs(job["id"], "Hitting Failure Callback")
    output_data["caas_job_id"] = job["id"]
    body = {
        "Output": {"output_data": output_data, "error_data": error_data},
        "Error": {"ErrorCode": "400", "Message": str(error)},
        "StatusCode": "400",
    }
    add_info_logs(job["id"], f" failure message -> {str(body)}")
    job["callback_status"] = 400
    update_job(job)
    response = requests.post(url, data=json.dumps(body))


def read_json_file(file_path, job_id):
    add_info_logs(job_id, f"Reading JSON File {file_path}")
    if os.path.exists(file_path):
        if os.path.getsize(file_path) == 0:
            add_info_logs(job_id, f"File Read {file_path} Successfull")
            return {}

        with open(file_path, "r") as json_file:
            data = json.load(json_file)
        add_info_logs(job_id, f"File Read {file_path} Successfull")
        return data
    else:
        add_info_logs(job_id, f"File Read {file_path} Successfull")
        return {}


def run_with_timeout(cmd, timeout):
    timeout = int(timeout)
    process = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    try:
        outs, errs = process.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        process.kill()
        outs, errs = process.communicate()

        # Handle the timeout scenario here
        # handle_timeout(job, output_path)
        return subprocess.CompletedProcess(args=cmd, returncode=400, stdout=outs, stderr="Script execution timed out")

    return subprocess.CompletedProcess(args=cmd, returncode=process.returncode, stdout=outs, stderr=errs)

def trigger_script(job, algo_block, run_cmd, output_path):
    add_info_logs(job["id"], "Starting the Algo Run")
    run_cmd = run_cmd.split(" ")
    if "timeout" not in algo_block or algo_block["timeout"] == "-1":
        script_status = subprocess.run(
            run_cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE
        )
    else:
        script_status = run_with_timeout(run_cmd, algo_block["timeout"])
    if script_status.returncode == 0:
        add_info_logs(job["id"], f"Script run successfull for the job {job['id']}")
        change_job_to_success_state(job)
        if "callBackUri" in job["data"] and job["data"]["callBackUri"] != "":
            send_success_callback(
                job["data"]["callBackUri"],
                read_json_file(output_path + "/" + SCRIPT_OUTPUT_DATA, job["id"]),
                read_json_file(output_path + "/" + SCRIPT_ERROR_DATA, job["id"]),
                job,
            )
    else:
        add_info_logs(job["id"], f"Script run failed for the job {job['id']}")
        change_job_to_failure_state(job, script_status.stderr)
        if "callBackUri" in job["data"] and job["data"]["callBackUri"] != "":
            send_failure_callback(
                job["data"]["callBackUri"],
                script_status.stderr,
                read_json_file(output_path + "/" + SCRIPT_OUTPUT_DATA, job["id"]),
                read_json_file(output_path + "/" + SCRIPT_ERROR_DATA, job["id"]),
                job,
            )
    delete_folder(output_path, job["id"])


def parametrize_configs(file_path, params):
    with open(file_path, "r") as local_file:
        file_content = local_file.read()
        local_file.close()

    for param in params:
        file_content.replace("${" + param + "}", params[param])

    with open(file_path, "w") as local_file:
        local_file.write(file_content)
        local_file.close


def download_folder_from_github(
    username, repository, branch, folder_path, output_path, token, job_id
):
    try:
        g = Github(token)
        repo = g.get_repo(f"{username}/{repository}")
        contents = repo.get_contents(folder_path, ref=branch)
        output_folder = os.path.join(output_path + "/", os.path.basename(folder_path))
        os.makedirs(output_folder, exist_ok=True)

        download_contents(contents, output_folder, repo, branch, job_id)
        return SUCCESS
    except Exception as e:
        return e


def download_contents(contents, current_path, repo, branch, job_id):
    for content in contents:
        if content.type == "dir":
            new_path = os.path.join(current_path, content.name)
            os.makedirs(new_path, exist_ok=True)

            sub_contents = repo.get_contents(content.path, ref=branch)
            download_contents(sub_contents, new_path, repo, branch)
        else:
            file_content = repo.get_contents(content.path, ref=branch)
            with open(os.path.join(current_path, content.name), "wb") as f:
                add_info_logs(
                    job_id,
                    f"Downloaded {str(os.path.join(current_path, content.name))} successfully",
                )
                f.write(file_content.decoded_content)


def download_folder_from_datalake(
    account_name,
    file_system_name,
    storage_account_key,
    folder_path,
    local_output_path,
    job_id,
):
    try:
        service_client = DataLakeServiceClient(
            account_url=f"https://{account_name}.dfs.core.windows.net",
            credential=storage_account_key,
        )

        file_system_client = service_client.get_file_system_client(file_system_name)
        paths = file_system_client.get_paths(folder_path)
        for path in paths:
            pathss = local_output_path + "/"
            folders = path.name.split("/")[:-1]
            for folder in folders:
                pathss += folder
                if not os.path.exists(pathss):
                    os.makedirs(pathss)
                pathss += "/"
            if "." in path.name:
                file_client = file_system_client.get_file_client(path.name)
                download = file_client.download_file()
                downloaded_bytes = download.readall()
                with open(local_output_path + "/" + path.name, "wb") as local_file:
                    add_info_logs(
                        job_id,
                        f"Downloaded {local_output_path}/{path.name} successfully",
                    )
                    local_file.write(downloaded_bytes)
        return SUCCESS
    except Exception as e:
        return e


def download_folder_from_blob_storage(
    account_name, container_name, storage_account_key, local_output_path, job_id
):
    try:
        blob_service_client = BlobServiceClient(
            account_url=f"https://{account_name}.blob.core.windows.net",
            credential=storage_account_key,
        )
        container_client = blob_service_client.get_container_client(container_name)

        # List all blobs in the container
        blob_list = container_client.walk_blobs()

        # Download each blob and maintain folder structure
        for blob in blob_list:
            blob_path = blob.name
            local_path = os.path.join(local_output_path, blob_path)

            # Create local directories if they don't exist
            os.makedirs(os.path.dirname(local_path), exist_ok=True)

            # Download blob to a local file
            with open(local_path, "wb") as local_file:
                blob_data = container_client.download_blob(blob.name)
                local_file.write(blob_data.readall())
            add_info_logs(
                job_id, f"Blob {blob_path} downloaded to {local_path} successfully."
            )
        return SUCCESS

    except Exception as e:
        return str(e)


def add_script(job, algo_block, output_path, job_id, background_flag):
    global scheduler
    change_job_to_processing_state(job)
    if algo_block["repo_type"] == "github":
        add_info_logs(job_id, "Downloading the files from github")
        status = download_folder_from_github(
            algo_block["repo_creds"]["username"],
            algo_block["repo_creds"]["repository"],
            algo_block["repo_creds"]["branch"],
            algo_block["repo_creds"]["folder_path"],
            output_path,
            algo_block["repo_creds"]["access_token"],
            job_id,
        )
    elif algo_block["repo_type"] == "data_lake":
        add_info_logs(job_id, "Downloading the files from DataLake")
        status = download_folder_from_datalake(
            algo_block["repo_creds"]["account_name"],
            algo_block["repo_creds"]["file_system_name"],
            algo_block["repo_creds"]["storage_account_key"],
            algo_block["repo_creds"]["folder_path"],
            output_path,
            job_id,
        )
    elif algo_block["repo_type"] == "blob_storage":
        add_info_logs(job_id, "Downloading the files from BlobStorage")
        status = download_folder_from_blob_storage(
            algo_block["repo_creds"]["account_name"],
            algo_block["repo_creds"]["file_system_name"],
            algo_block["repo_creds"]["storage_account_key"],
            output_path,
            job_id,
        )
    else:
        status = FAILED

    run_command = (
        str(job["data"]["script_info"]["run_cmd"])
        .replace("${" + "root_dir" + "}", output_path)
        .replace("${" + "job_id" + "}", job_id)
    )
    add_info_logs(job_id, f"run command for the script is {run_command}")

    if status != SUCCESS:
        add_info_logs(job_id, "Failed to download the files from the repo")
        change_job_to_failure_state(job, str(status))
        if "callBackUri" in job["data"] and job["data"]["callBackUri"] != "":
            send_failure_callback(
                job["data"]["callBackUri"],
                status,
                read_json_file(output_path + "/" + SCRIPT_OUTPUT_DATA, job["id"]),
                read_json_file(output_path + "/" + SCRIPT_ERROR_DATA, job["id"]),
                job,
            )
        delete_folder(output_path, job_id)
        return

    if "config_path" in job["data"]["script_info"]:
        config_path = job["data"]["script_info"]["config_path"]
        if config_path not in [None, ""]:
            add_info_logs(job_id, f"Substituting Config File {config_path}")
            config_path = config_path.replace("${" + "root_dir" + "}", output_path)
            parametrize_configs(
                config_path, job["data"]["script_info"]["config_params"]
            )

    if "run_cmd_params" in job["data"]["script_info"]:
        with open(output_path + "/" + SCRIPT_INPUT_DATA, "w") as json_file:
            add_info_logs(job_id, f"created {output_path}/{SCRIPT_INPUT_DATA} file")
            json_file.write(json.dumps(job["data"]["script_info"]["run_cmd_params"]))

    if background_flag:
        scheduler.add_job(trigger_script, args=[job, algo_block, run_command, output_path])
    else:
        trigger_script(job, algo_block, run_command, output_path)


def increff_runner(job_id, background_flag=False):
    setup_logger(python_config["env"]["env"], job_id)
    add_info_logs(job_id, f"received a task to run")

    folder_name = "/tmp/caas_" + job_id

    create_folder(folder_name)
    job = get_table_values(JOBS_TABLE, job_id)
    algo_block = get_table_values(
        ALGO_BLOCK_TABLE,
        str(job["data"]["app_id"]) + "." + job["data"]["block_identifier"],
    )

    add_script(job, algo_block, folder_name, job_id, background_flag)

    return func.HttpResponse(json.dumps({"msg": "Run Trigger Successful!"}))