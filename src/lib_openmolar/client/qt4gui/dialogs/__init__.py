from bpe_dialogs import NewBpeDialog, ListBpeDialog  #BPE_ComboBox
from find_patient_dialog import FindPatientDialog
from new_patient_dialog import NewPatientDialog
from new_exam_dialog import NewExamDialog
from hyg_treatment_dialog import HygTreatmentDialog
from xray_treatment_dialog import XrayTreatmentDialog
from edit_patient_dialog import EditPatientDialog
from address_dialogs.address_dialog import AddressDialog
from save_discard_cancel_dialog import SaveDiscardCancelDialog
from treatment_item_finalise_dialog import TreatmentItemFinaliseDialog


__all__ = [ "NewBpeDialog",
            "ListBpeDialog",
            "FindPatientDialog",
            "NewPatientDialog",
            "NewExamDialog",
            "HygTreatmentDialog",
            "XrayTreatmentDialog",
            "EditPatientDialog",
            "AddressDialog",
            "SaveDiscardCancelDialog",
            "TreatmentItemFinaliseDialog"
        ]