import pandas as pd
import logging
import typing
import warnings

from ..utils.gdrive import get_table_data_from_gdrive


logger = logging.getLogger('g3tables.visualization_table')


DEVICE_TYPES = {
    "System": "System_G3",
    "SystemSafety": "SystemSafety_G3",
    "Zone": "Zone_G3",
    "Gate": "Gate_G3",
    "Route": "Route_G3",
    "Zone.Track": "Track",
    "Detector.TrackCircuit": "TC_G3",
    "Detector.Pantograph": "PD_G3",
    "PointMachine.PME": "PME_G3",
    "PointMachine.PMM": "PMM_G3",
    "Signal": "Signal_G3",
    "Signal.Symbol": "SignalSymbol_G3",
    "DoorDisplay7": "DoorDisplay7_G3",
    "Requestor.Digital": "RequestorDigital",
    "Requestor.RoutingTable": "RoutingTable_G3",
    "Requestor.Vecom": "VecomController_G3",
    "Requestor.Vecom.Loop": "VecomLoop_G3",
    "Requestor.DRR": "DRRController_G3",
    "Requestor.DRR.Transceiver": "DRRTransceiver_G3",
    "Requestor.SPIE": "SPIEController_G3",
    "Requestor.SPIE.Loop": "SPIELoop_G3",
    "Requestor.Vetra": "Vetra_G3",
    "Requestor.Digital.AWA": "AWA_G3",
    "Cabinet": "Cabinet_G3",
    "Cabinet.UPS": "CabinetUps_G3",
    "Cabinet.Fuse": "CabinetFuse_G3",
    "Cabinet.Convertor": "CabinetConvertor_G3",
    "Cabinet.MonitoringModule": "",
    "Heating": "Heating_G3",
    "Heating.Contactor": "HeatingContactor_G3",
    "Heating.Contactor.Rod": "HeatingRod_G3",
    "Matrix": "MPS_G3",
    "GPIO": "GPIO_G3"
}


class SHVVarDict(typing.TypedDict):
    name: str
    is_blacklisted: bool
    is_deleted: bool


class SHVProjectTypeDict(typing.TypedDict):
    type: str
    restricted_to: str | None
    vars: dict[str, SHVVarDict]


class VisualizationTable:
    NAME_PATTERN = 'project_visualization'
    EXCLUDED_SHEETS = [
        'Title', 'Identification', 'Worksheet explanation', 'Users'
        ]

    def __init__(self, params_sheet_data: pd.DataFrame) -> None:
        self._data = params_sheet_data

    @classmethod
    def is_name_valid(cls, name: str) -> bool:
        name_formatted = name.strip().replace(' ', '_').casefold()
        return cls.NAME_PATTERN in name_formatted

    @classmethod
    def from_local(cls, path: str) -> typing.Self:
        with warnings.catch_warnings():
            warnings.filterwarnings('ignore', category=UserWarning)
            params_sheet = pd.read_excel(
                path, header=2, sheet_name='Parameters'
                )
        formatter = VisualizationTableFormatter.format_params_sheet
        return cls(formatter(params_sheet))

    @classmethod
    def from_gdrive(cls, gdrive_table_name: str) -> typing.Self:
        sheets_all = get_table_data_from_gdrive(
            gdrive_table_name, header_row=3, exclude_sheets=cls.EXCLUDED_SHEETS
            )
        formatter = VisualizationTableFormatter.format_params_sheet
        return cls(formatter(sheets_all['Parameters']))

    @classmethod
    def load(cls, path: str) -> typing.Self:
        if path.endswith('.xlsx'):
            return cls.from_local(path)
        return cls.from_gdrive(path)

    @property
    def data(self) -> pd.DataFrame:
        return self._data

    @staticmethod
    def _new_shv_project_type_dict(
        module_type: str, restricted_to: str | None
    ) -> SHVProjectTypeDict:
        return {
            'type': module_type,
            'restricted_to': restricted_to,
            'vars': {}
            }

    @staticmethod
    def _new_shv_var_dict(
        shv_var_name: str, is_blacklisted: bool, is_deleted: bool
    ) -> SHVVarDict:
        return {
            'name': shv_var_name,
            'is_blacklisted': is_blacklisted,
            'is_deleted': is_deleted
            }

    @property
    def project_types(self) -> dict[str, SHVProjectTypeDict]:
        project_types: dict[str, SHVProjectTypeDict] = {}
        for _, row in self._data.iterrows():
            # create or fetch existing project_type_data dictionary
            project_type = row['Project type']
            project_subtype = row['Project subtype']
            if project_subtype:
                module_type, restricted_to = project_subtype, project_type
            else:
                module_type, restricted_to = project_type, None
            project_type_data = project_types.setdefault(
                module_type,
                self._new_shv_project_type_dict(module_type, restricted_to)
                )
            # create shv variable data dictionary
            if not (shv_var := row['SHV variable']):
                continue
            project_type_data['vars'][shv_var] = self._new_shv_var_dict(
                shv_var_name=shv_var,
                is_blacklisted=row['Available only in SHVspy'],
                is_deleted=row['x']
                )
        return project_types


class VisualizationTableFormatter:

    @staticmethod
    def fill_in_device_types(device):
        if device in DEVICE_TYPES:
            return DEVICE_TYPES[device]
        logging.warning(
            f'Could not retrieve SHV Device type for module "{device}".'
            )
        return ''

    @staticmethod
    def format_params_sheet(params_sheet: pd.DataFrame) -> pd.DataFrame:
        # drop rows where the 'Module (device)' column value is empty
        params_sheet = params_sheet.fillna('').astype(str, copy=True)
        params_sheet_mask = (params_sheet['Module (device)'] != '')
        params_sheet = params_sheet[params_sheet_mask]
        # create the 'Project type' column
        params_sheet['Project type'] = params_sheet['Module (device)'].apply(
            VisualizationTableFormatter.fill_in_device_types
            )
        # format the 'x' column to bool
        params_sheet.loc[:, 'x'] = params_sheet['x'].apply(
            lambda cell_val: bool(cell_val)
        )
        # format the 'Available only in SHVspy' column to bool
        col_name = 'Available only in SHVspy'
        params_sheet.loc[:, col_name] = params_sheet[col_name].apply(
            lambda cell_val: cell_val == 'TRUE'
        )
        return params_sheet
