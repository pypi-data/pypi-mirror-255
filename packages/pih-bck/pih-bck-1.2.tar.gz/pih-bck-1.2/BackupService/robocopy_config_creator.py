import ipih

from pih import A
from BackupService.const import *
import json


# \\pih\facade\WSService\pstools\psexec -nobanner -accepteula \\ws-255 -i -h -u fmv\Administrator -p Fortun@90 robocopy /job:\\pih\facade\BackupService\robocopy_config\dc1-dc2\shares
# \\pih\facade\WSService\pstools\psexec -nobanner -accepteula \\backup_worker -i -u fmv\Administrator -p Fortun@90 robocopy /job:\\pih\facade\BackupService\robocopy_config\1c-nas\move_1c_backups
# \\pih\facade\WSService\pstools\psexec -nobanner -accepteula \\ws-255 -i -h -u fmv\Administrator -p Fortun@90 robocopy /job:\\pih\facade\BackupService\robocopy_config\polibase-polibase_test\polibase_data

JOB_SETTINGS_DEFAULT: RobocopyJobDescription = RobocopyJobDescription(
    None, None, A.CT.HOST.WS255.NAME, False, True, False
)

JOB_NAMES = ROBOCOPY.JOB_NAMES

USER_DESKTOP_SETTINGS: dict[str, list[RobocopyJobDescription]] = {
    A.CT.HOST.DC1.ALIAS: [JOB_SETTINGS_DEFAULT.clone(JOB_NAMES.USER_DESKTOP)]
}

print(
    json.dumps(
        json.loads(
            A.D.rpc_represent(
                {
                    A.CT.HOST.DC1.ALIAS: {
                        A.CT.HOST.DC2.ALIAS: [
                            JOB_SETTINGS_DEFAULT.clone(JOB_NAMES.OMS),
                            JOB_SETTINGS_DEFAULT.clone(JOB_NAMES.SCAN),
                            JOB_SETTINGS_DEFAULT.clone(JOB_NAMES.SHARES),
                            JOB_SETTINGS_DEFAULT.clone(JOB_NAMES.HOMES),
                            JOB_SETTINGS_DEFAULT.clone(JOB_NAMES.FACADE),
                        ],
                        A.CT.HOST.BACKUP_WORKER.ALIAS: [
                            JOB_SETTINGS_DEFAULT.clone(JOB_NAMES.OMS),
                            JOB_SETTINGS_DEFAULT.clone(JOB_NAMES.SHARES),
                            JOB_SETTINGS_DEFAULT.clone(JOB_NAMES.HOMES),
                        ],
                    },
                    A.CT.HOST.POLIBASE.ALIAS: {
                        A.CT.HOST.BACKUP_WORKER.ALIAS: [
                            JOB_SETTINGS_DEFAULT.clone(JOB_NAMES.POLIBASE_DATA),
                            JOB_SETTINGS_DEFAULT.clone(
                                JOB_NAMES.POLIBASE_DATA_LIVE, live=True
                            ),
                            JOB_SETTINGS_DEFAULT.clone(JOB_NAMES.POLIBASE_FILES),
                        ],
                        A.CT.HOST.POLIBASE2.ALIAS: [
                            JOB_SETTINGS_DEFAULT.clone(JOB_NAMES.POLIBASE_DATA),
                            JOB_SETTINGS_DEFAULT.clone(
                                JOB_NAMES.POLIBASE_DATA_LIVE, live=True
                            ),
                            JOB_SETTINGS_DEFAULT.clone(JOB_NAMES.POLIBASE_FILES),
                        ],
                    },
                    A.CT.HOST._1C.ALIAS: {
                        A.CT.HOST.NAS.ALIAS: [
                            RobocopyJobDescription(JOB_NAMES.MOVE_1C_BACKUPS, "8:00")
                        ]
                    },
                    A.CT.HOST.WS816.NAME: {
                        A.CT.HOST.WS255.NAME: [
                            JOB_SETTINGS_DEFAULT.clone(JOB_NAMES.VALENTA)
                        ]
                    },
                    "gea": USER_DESKTOP_SETTINGS,
                    "ssa": USER_DESKTOP_SETTINGS,
                    "bar": USER_DESKTOP_SETTINGS,
                    "vns": USER_DESKTOP_SETTINGS,
                    "vvp": USER_DESKTOP_SETTINGS,
                    "gen": USER_DESKTOP_SETTINGS,
                    "rob": USER_DESKTOP_SETTINGS,
                    "ptyu": USER_DESKTOP_SETTINGS,
                }
            )
        ),
        indent=2,
    )
)
