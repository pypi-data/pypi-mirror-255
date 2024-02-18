import typing
import json
import os

if typing.TYPE_CHECKING:
    from .utils.xmltemplate.type_hinting import XMLElementRecursiveData


class HWModuleCatalogData(typing.TypedDict):
    type: str
    is_safety: typing.NotRequired[bool]
    tb: typing.NotRequired[typing.Optional[str]]
    bm: typing.NotRequired[typing.Optional[str]]


MODULE_CATALOG: dict[str, HWModuleCatalogData] = {
    'x20cai4622': {
        'type': 'X20cAI4622',
        'is_safety': False,
        'tb': 'X20TB12',
        'bm': 'X20cBM11'
        },
    'x20cat4222': {
        'type': 'X20cAT4222',
        'is_safety': False,
        'tb': 'X20TB12',
        'bm': 'X20cBM11'
        },
    'x20cbb80': {'type': 'X20cBB80'},
    'x20cbb81': {'type': 'X20cBB81'},
    'x20cbb82': {'type': 'X20cBB82'},
    'x20cbc0083': {
        'type': 'X20cBC0083',
        'is_safety': False,
        'tb': 'X20TB12',
        'bm': 'X20cBB80'
        },
    'x20cbc8083': {
        'type': 'X20cBC8083',
        'is_safety': False,
        'tb': 'X20TB12',
        'bm': 'X20cBB82'
        },
    'x20cbm01': {'type': 'X20cBM01'},
    'x20cbm11': {'type': 'X20cBM11'},
    'x20cbm12': {'type': 'X20cBM12'},
    'x20cbm33': {'type': 'X20cBM33'},
    'x20ccp1584': {
        'type': 'X20cCP1584',
        'is_safety': False,
        'tb': None,
        'bm': None
        },
    'x20ccs1020': {
        'type': 'X20cCS1020',
        'is_safety': False,
        'tb': 'X20TB12',
        'bm': 'X20cBM11'
        },
    'x20ccs1030': {
        'type': 'X20cCS1030',
        'is_safety': False,
        'tb': 'X20TB12',
        'bm': 'X20cBM11'
        },
    'x20cdi9371': {
        'type': 'X20cDI9371',
        'is_safety': False,
        'tb': 'X20TB12',
        'bm': 'X20cBM11'
        },
    'x20cdi9372': {
        'type': 'X20cDI9372',
        'is_safety': False,
        'tb': 'X20TB12',
        'bm': 'X20cBM11'
        },
    'x20cdm9324': {
        'type': 'X20cDM9324',
        'is_safety': False,
        'tb': 'X20TB12',
        'bm': 'X20cBM11'
        },
    'x20cdo6639': {
        'type': 'X20cDO6639',
        'is_safety': False,
        'tb': 'X20TB32',
        'bm': 'X20cBM12'
        },
    'x20cdo9321': {
        'type': 'X20cDO9321',
        'is_safety': False,
        'tb': 'X20TB12',
        'bm': 'X20cBM11'
        },
    'x20cdo9322': {
        'type': 'X20cDO9322',
        'is_safety': False,
        'tb': 'X20TB12',
        'bm': 'X20cBM11'
        },
    'x20cmr111': {
        'type': 'X20CMR111',
        'is_safety': False,
        'tb': 'X20TB12',
        'bm': 'X20cBM11'
        },
    'x20cps3300': {
        'type': 'X20cPS3300',
        'is_safety': False,
        'tb': 'X20TB12',
        'bm': 'X20cBM01'
        },
    'x20cps9400': {
        'type': 'X20cPS9400',
        'is_safety': False,
        'tb': 'X20TB12',
        'bm': 'X20cBB80'
        },
    'x20csi4100': {
        'type': 'X20cSI4100',
        'is_safety': True,
        'tb': 'X20TB52',
        'bm': 'X20cBM33'
        },
    'x20csi9100': {
        'type': 'X20cSI9100',
        'is_safety': True,
        'tb': 'X20TB52',
        'bm': 'X20cBM33'
        },
    'x20csl8101': {
        'type': 'X20cSL8101',
        'is_safety': True,
        'tb': 'X20TB52',
        'bm': None
        },
    'x20cso2530': {
        'type': 'X20cSO2530',
        'is_safety': True,
        'tb': 'X20TB72',
        'bm': 'X20cBM33'
        },
    'x20cso4120': {
        'type': 'X20cSO4120',
        'is_safety': True,
        'tb': 'X20TB52',
        'bm': 'X20cBM33'
        },
    'x20tb12': {'type': 'X20TB12'},
    'x20tb32': {'type': 'X20TB32'},
    'x20tb52': {'type': 'X20TB52'},
    'x20tb72': {'type': 'X20TB72'},
    }


class SettingsData(typing.TypedDict):
    version: str
    settings: list['XMLElementRecursiveData']


def read_settings_data() -> dict[str, SettingsData]:
    file_dir = os.path.dirname(os.path.realpath(__file__))
    with open(os.path.join(file_dir, "settings.json"), 'r') as file:
        return json.load(file)


SETTINGS_DATA = read_settings_data()


def update_module_catalog_from_settings():
    for module in SETTINGS_DATA:
        if module.lower() not in MODULE_CATALOG:
            module_data = {'type': module}
            if any(
                attr['attributes']['ID'] == 'SafeModuleID'
                for attr in SETTINGS_DATA[module]['settings']
            ):
                module_data['is_safety'] = True
            MODULE_CATALOG[module.lower()] = module_data


update_module_catalog_from_settings()


class HWModuleData:

    def __init__(cls) -> None:
        raise TypeError('HWModuleData class cannot be instantiated.')

    @staticmethod
    def _get_from_module_catalog(
        module_type: str
    ) -> typing.Optional[HWModuleCatalogData]:
        return MODULE_CATALOG.get(module_type.lower())

    @classmethod
    def format_module_type(cls, module_type: str) -> str:
        data = cls._get_from_module_catalog(module_type)
        if (data is None) or not data.get('type'):
            return module_type
        return data['type']

    @classmethod
    def get_tb(cls, module_type: str) -> typing.Optional[str]:
        data = cls._get_from_module_catalog(module_type)
        if (data is None) or not data.get('tb'):
            return None  # add warning
        return data['tb']

    @classmethod
    def get_bm(cls, module_type: str) -> typing.Optional[str]:
        data = cls._get_from_module_catalog(module_type)
        if (data is None) or not data.get('bm'):
            return None  # add warning
        return data['bm']

    @classmethod
    def is_safety(cls, module_type: str) -> bool:
        data = cls._get_from_module_catalog(module_type)
        if (data is None) or not data.get('is_safety'):
            return False  # add warning
        return data['is_safety']

    @classmethod
    def _get_from_settings_data(cls, module_type: str) -> SettingsData:
        try:
            return SETTINGS_DATA[module_type]
        except KeyError:
            module_type = cls.format_module_type(module_type)
            data = SETTINGS_DATA.get(module_type)
            if data is None:
                return SETTINGS_DATA['default']
            return data

    @classmethod
    def get_version(cls, module_type: str) -> str:
        data = cls._get_from_settings_data(module_type)
        return data['version']

    @classmethod
    def get_settings(cls, module_type: str) -> list['XMLElementRecursiveData']:
        data = cls._get_from_settings_data(module_type)
        return data['settings']
