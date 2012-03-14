'''
make classes under lib_openmolar.admin.qt4.dialogs easily importable
'''
from populate_demo_dialog import PopulateDemoDialog
from plain_text_dialog import PlainTextDialog
from new_db_dialog import NewDatabaseDialog
from new_db_row_dialog import NewRowDialog
from manage_db_dialog import ManageDatabaseDialog
from import_progress_dialog import ImportProgressDialog

__all__ = ["PopulateDemoDialog",
            "PlainTextDialog",
            "NewDatabaseDialog",
            "NewRowDialog",
            "ManageDatabaseDialog",
            "ImportProgressDialog"]