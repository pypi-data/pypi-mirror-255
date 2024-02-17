


import subprocess
from loguru import logger
from tornado.escape import json_decode
import paperless.constants as constants
from google.cloud.jupyter_config.config import gcp_project, gcp_region

def build_session_template(templateName=constants.DEFAULT_SESSION_TEMPLATE_NAME):
    project_id = gcp_project()
    region = gcp_region()
    return f"projects/{project_id}/regions/{region}/sessionTemplates/{templateName}"

def is_session_active_and_ready(sessionid):
    logger.debug("checking if session is active and ready")
    session = get_session(sessionid)
    if session and session["state"] == "ACTIVE":
        logger.debug("session is active and ready")
        return True
    else:
        logger.debug("session is not active and ready")
        return False

def get_session(sessionid):
    logger.debug("getting session")
    output, error =  subprocess.Popen(f"{constants.GCLOUD_SESSIONS_COMMAND} list --format json", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True).\
            communicate()
    if error and output is None:
        raise Exception("failed to list sessions:", error)

    sessions = json_decode(output)
    session = next((x for x in sessions if sessionid in x["name"]), None)
    if session:
        logger.debug("found session")
        return session
    else:
        logger.debug("session not found")
        return None

def create_session(sessionid,templateName):
    logger.debug("creating session")
    output, error = subprocess.Popen("gcloud beta dataproc sessions create spark "+sessionid+" --session_template "+templateName,\
                                        shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True).\
                                        communicate()
    if error and output is None:
        raise Exception("failed to create session:", error)
    logger.debug("created session:", output)

def delete_session(sessionid):
    logger.debug("deleting session")
    output, error = subprocess.Popen("gcloud beta dataproc sessions terminate "+sessionid + " --quiet --async", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True).\
                                        communicate()
    if error and output is None:
        raise Exception("failed to delete session:", error)
    logger.debug("deleted session")
