import copy
import itertools
import re
import typing

from ._hw_module_data import HWModuleData
from .utils.xmltemplate import XMLElement, create_xml_element_recursive


def create_module_settings(module_type: str) -> list[XMLElement]:
    return [
        create_xml_element_recursive(param_data)
        for param_data in HWModuleData.get_settings(module_type)
        ]


class HWModule:
    _SafeModuleIDCounter = itertools.count(2)  # 1 is reserved for SL8101

    def __init__(
        self,
        name: str,
        type: str,
        dependencies: typing.Optional[typing.Iterable['HWModule']] = None,
        cabinet: str | None = None
    ) -> None:
        version = HWModuleData.get_version(type)
        self._xml = XMLElement(
            tag='Module', text=None, Name=name, Type=type, Version=version
            )
        self._is_safety = HWModuleData.is_safety(type)
        settings = create_module_settings(type)
        if self._is_safety:
            for param in settings:
                if (
                    param.get('ID') == 'SafeModuleID' and
                    not param['Value'].isnumeric()
                ):
                    param['Value'] = next(self._SafeModuleIDCounter)
        for item in settings:
            self._xml.add_child(item)
        self.dependencies: dict[str, HWModule] = {}
        if dependencies is None:
            dependencies = []
        for dep in dependencies:
            self.add_dependency(dep)
        self.connections: dict[str, HWModule] = {}
        self.cabinet = cabinet

    def __str__(self) -> str:
        return self.to_xml_str()

    def __repr__(self) -> str:
        cls_name = self.__class__.__name__
        return f'{cls_name}(name="{self.name}", type="{self.type}")'

    @classmethod
    def new(cls, module_type: str, module_name_suffix: str) -> 'HWModule':
        return HWModuleCreator.create(module_type, module_name_suffix)

    @classmethod
    def reset_safemodule_id_counter(cls) -> None:
        cls._SafeModuleIDCounter = itertools.count(1)

    def to_xml_elements(self) -> list[XMLElement]:
        xml_elements = [copy.deepcopy(self._xml)]
        for dep in self.dependencies.values():
            xml_elements.append(copy.deepcopy(dep._xml))
        return xml_elements

    def to_xml_str(self) -> str:
        return "".join(elem.to_str() for elem in self.to_xml_elements())

    @property
    def name(self) -> str:
        return self._xml["Name"]

    @name.setter
    def name(self, name: str) -> None:
        self._xml["Name"] = name

    @property
    def type(self):
        return self._xml["Type"]

    @property
    def firmware_version(self):
        return self._xml["Version"]

    @firmware_version.setter
    def firmware_version(self, firmware_version: str) -> None:
        self._xml["Version"] = firmware_version

    @property
    def is_safety(self) -> bool:
        return self._is_safety

    def add_dependency(self, dependency_module: 'HWModule') -> None:
        if dependency_module.name in self.dependencies:
            raise ValueError(
                f'Module "{dependency_module.name}" is already registered '
                f'as a dependency of module "{self.name}".'
                )
        self.dependencies[dependency_module.name] = dependency_module

    def remove_dependency(self, dependency_module: 'HWModule') -> None:
        if dependency_module.name in self.dependencies:
            del self.dependencies[dependency_module.name]

    def add_connection(
        self, connector: str, target_module: 'HWModule', target_connector: str
    ) -> None:
        self.remove_connection(connector)
        connection = XMLElement(
            tag='Connection',
            Connector=connector,
            TargetModule=target_module.name,
            TargetConnector=target_connector
        )
        self._xml.add_child(connection)
        self.connections[connector] = target_module
        target_module.connections[target_connector] = self

    def add_connection_plk(
        self,
        connector: str,
        target_module: 'HWModule',
        target_connector: str,
        node_number: typing.Optional[int] = None,
        cable_length: float = 10.0,
        cable_version: str = "1.0.0.3",
    ) -> None:
        self.remove_connection(connector)
        connection = XMLElement(
            tag="Connection",
            text=None,
            Connector=connector,
            TargetModule=target_module.name,
            TargetConnector=target_connector,
            )
        if node_number is not None:
            connection['NodeNumber'] = str(node_number)
        cable = XMLElement(
            tag="Cable",
            text=None,
            Type="PowerlinkCable",
            Length=str(cable_length),
            Version=cable_version,
            )
        connection.add_child(cable)
        self._xml.add_child(connection)
        self.connections[connector] = target_module
        target_module.connections[target_connector] = self

    def remove_connection(self, connector: str) -> None:
        if connector in self.connections:
            connected_module = self.connections[connector]
            del self.connections[connector]
            for conn, module in connected_module.connections.items():
                if module == self:
                    del connected_module.connections[conn]
                    break


def is_tb(module: HWModule):
    return bool(re.match(r"^X20TB\d{2}$", module.type))


def is_bm(module: HWModule):
    return bool(re.match(r"^X20c?(BM|BB)\d{2}$", module.type))


class HWModuleCreator:

    def __init__(self):
        raise TypeError("HWModuleCreator class cannot be instantiated.")

    @classmethod
    def _create_module(
        cls,
        type_: str,
        name_suffix: str,
        dependencies: typing.Optional[typing.Iterable[HWModule]] = None
    ) -> 'HWModule':
        type_ = HWModuleData.format_module_type(type_)
        return HWModule(f"{type_}_{name_suffix}", type_, dependencies)

    @classmethod
    def _create_sl8101(cls, name_suffix: str) -> HWModule:
        assert (tb_name := HWModuleData.get_tb("X20cSL8101")) is not None
        tb = cls._create_module(tb_name, name_suffix)
        mk0213 = cls._create_module('X20cMK0213', name_suffix)
        sl8101 = cls._create_module(
            'X20cSL8101', name_suffix, [tb, mk0213]
            )
        sl8101.add_connection("SS1", tb, "SS")
        sl8101.add_connection("SS1", tb, "SS")
        mk0213.add_connection("SL", sl8101, "SL1")
        return sl8101

    @classmethod
    def _create_bc0083(cls, name_suffix: str) -> HWModule:
        assert (bb_name := HWModuleData.get_bm("X20cBC0083")) is not None
        bb = cls._create_module(bb_name, name_suffix)
        assert (tb_name := HWModuleData.get_tb("X20cBC0083")) is not None
        tb = cls._create_module(tb_name, name_suffix)
        ps9400 = cls._create_module('X20cPS9400', name_suffix)
        bc0083 = cls._create_module(
            'X20cBC0083', name_suffix, [ps9400, bb, tb]
            )
        bc0083.add_connection("SL", bb, "SL1")
        ps9400.add_connection("PS", bb, "PS1")
        ps9400.add_connection("SS1", tb, "SS")
        return bc0083

    @classmethod
    def _create_bc8083(cls, name_suffix: str) -> HWModule:
        assert (bb_name := HWModuleData.get_bm("X20cBC8083")) is not None
        bb = cls._create_module(bb_name, name_suffix)
        assert (tb_name := HWModuleData.get_tb("X20cBC8083")) is not None
        tb = cls._create_module(tb_name, name_suffix)
        hb2821 = cls._create_module('X20cHB2881', name_suffix)
        ps9400 = cls._create_module('X20cPS9400', name_suffix)
        bc8083 = cls._create_module(
            'X20cBC8083', name_suffix, [hb2821, ps9400, bb, tb]
            )
        bc8083.add_connection("SL", bb, "SL1")
        hb2821.add_connection("SS", bb, "SS1")
        ps9400.add_connection("PS", bb, "PS1")
        ps9400.add_connection("SS1", tb, "SS")
        return bc8083

    @classmethod
    def _create_si9100(cls, name_suffix: str) -> HWModule:
        assert (bm_name := HWModuleData.get_bm("X20cSI9100")) is not None
        bm = cls._create_module(bm_name, name_suffix)
        assert (tb_name := HWModuleData.get_tb("X20cSI9100")) is not None
        tb_1 = cls._create_module(tb_name, name_suffix)
        tb_2 = cls._create_module(tb_name, name_suffix)
        tb_1.name = f"{tb_1.name}_1"
        tb_2.name = f"{tb_2.name}_2"
        si9100 = cls._create_module(
            'X20cSI9100', name_suffix, [tb_1, tb_2, bm]
            )
        si9100.add_connection("SS1", tb_1, "SS")
        si9100.add_connection("SS2", tb_2, "SS")
        si9100.add_connection("SL", bm, "SL1")
        return si9100

    @classmethod
    def _create_default(cls, type_: str, name_suffix: str) -> HWModule:
        module = cls._create_module(type_, name_suffix)
        if (tb_name := HWModuleData.get_tb(type_)):
            tb = cls._create_module(tb_name, name_suffix)
            module.add_dependency(tb)
            module.add_connection("SS1", tb, "SS")
        if (bm_name := HWModuleData.get_bm(type_)):
            bm = cls._create_module(bm_name, name_suffix)
            module.add_dependency(bm)
            module.add_connection("SL", bm, "SL1")
        return module

    @classmethod
    def create(cls, module_type: str, module_name_suffix: str) -> HWModule:
        special_types = {
            "x20csl8101": cls._create_sl8101,
            "x20cbc0083": cls._create_bc0083,
            "x20cbc8083": cls._create_bc8083,
            "x20csi9100": cls._create_si9100,
        }
        if module_type.lower() in special_types:
            create_method = special_types[module_type.lower()]
            return create_method(module_name_suffix)
        return cls._create_default(module_type, module_name_suffix)
