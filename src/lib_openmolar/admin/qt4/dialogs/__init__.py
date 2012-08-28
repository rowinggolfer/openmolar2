'''
make classes under lib_openmolar.admin.qt4.dialogs easily importable
'''
from populate_demo_dialog import PopulateDemoDialog
from plain_text_dialog import PlainTextDialog
from new_db_dialog import NewDatabaseDialog
from new_db_row_dialog import NewRowDialog
from manage_db_dialog import ManageDatabaseDialog
from configure_db_dialog import ConfigureDatabaseDialog
from manage_pg_users_dialog import ManagePGUsersDialog
from import_progress_dialog import ImportProgressDialog
from drop_pg_user_dialog import DropPGUserDialog

__all__ = ["PopulateDemoDialog",
            "PlainTextDialog",
            "NewDatabaseDialog",
            "NewRowDialog",
            "ManageDatabaseDialog",
            "ConfigureDatabaseDialog",
            "ManagePGUsersDialog",
            "ImportProgressDialog",
            "DropPGUserDialog",
            ]