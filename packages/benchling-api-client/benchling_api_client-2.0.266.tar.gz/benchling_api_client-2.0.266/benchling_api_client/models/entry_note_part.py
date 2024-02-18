from typing import Union

from ..extensions import UnknownType
from ..models.assay_run_note_part import AssayRunNotePart
from ..models.box_creation_table_note_part import BoxCreationTableNotePart
from ..models.checkbox_note_part import CheckboxNotePart
from ..models.external_file_note_part import ExternalFileNotePart
from ..models.lookup_table_note_part import LookupTableNotePart
from ..models.mixture_prep_table_note_part import MixturePrepTableNotePart
from ..models.plate_creation_table_note_part import PlateCreationTableNotePart
from ..models.registration_table_note_part import RegistrationTableNotePart
from ..models.results_table_note_part import ResultsTableNotePart
from ..models.simple_note_part import SimpleNotePart
from ..models.table_note_part import TableNotePart
from ..models.text_box_note_part import TextBoxNotePart

EntryNotePart = Union[
    SimpleNotePart,
    TableNotePart,
    TextBoxNotePart,
    CheckboxNotePart,
    ExternalFileNotePart,
    AssayRunNotePart,
    LookupTableNotePart,
    ResultsTableNotePart,
    RegistrationTableNotePart,
    PlateCreationTableNotePart,
    BoxCreationTableNotePart,
    MixturePrepTableNotePart,
    UnknownType,
]
