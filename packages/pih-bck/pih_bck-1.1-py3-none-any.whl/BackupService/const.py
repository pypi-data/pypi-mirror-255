import ipih

from pih import A
from pih.tools import j
from pih.collections import RobocopyJobDescription
from pih.collections.service import ServiceDescription
from pih.consts.hosts import HOSTS

NAME: str = "Backup"

VERSION: str = "1.1"

class ROBOCOPY:
    
    NAME: str = "robocopy"
    JOB_PARAMETER_NAME: str = "/job:"

    JOB_MAP: dict[str, dict[str, list[RobocopyJobDescription]]] | None = None

    class JOB_NAMES:
        
        MOVE_1C_BACKUPS: str = "move_1c_backups"
        POLIBASE_DATA: str = "polibase_data"
        POLIBASE_DATA_LIVE: str = "polibase_data_live"
        POLIBASE_FILES: str = "polibase_files"
        OMS: str = "oms"
        SCAN: str = "scan"
        HOMES: str = "homes"
        SHARES: str = "shares"
        FACADE: str = "facade"
        USER_DESKTOP: str = "user_desktop"
        VALENTA: str = "valenta"

HOST = HOSTS.BACKUP_WORKER

class PATH:

    class ROBOCOPY_JOB_CONFIG:
        
        FILE_NAME: str = "job_config.json"
        DIRECTORY_NAME: str = "robocopy_config"
        DIRECTORY: str = A.PTH.join(
            A.PTH.FACADE.VALUE, j((NAME, A.CT_FACADE.SERVICE_FOLDER_SUFFIX)), DIRECTORY_NAME)
        
SD: ServiceDescription = ServiceDescription(
    name=NAME,
    description="Backup service",
    host=HOST.NAME,
    commands=[
        "robocopy_start_job",
        "robocopy_get_job_status_list"
    ],
    version=VERSION,
    standalone_name="bck"
    )