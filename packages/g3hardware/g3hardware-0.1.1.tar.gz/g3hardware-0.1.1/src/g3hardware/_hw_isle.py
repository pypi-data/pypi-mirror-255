import collections.abc
import itertools
import typing

from ._hw_module import HWModule, is_bm

if typing.TYPE_CHECKING:
    from .utils.xmltemplate import XMLElement


class HWIsle(collections.abc.Sequence[HWModule]):
    POWERLINK_CABLE_LENGTH = 10
    POWERLINK_CABLE_VERSION = "1.0.0.3"
    _NodeNumberCounter = itertools.count(2)

    def __init__(
        self,
        head: HWModule,
        *tail: HWModule
    ) -> None:
        if not self.is_isle_head(head.type):
            raise TypeError(f'Module "{head.type}" cannot form a HW isle.')
        self._modules: list[HWModule] = [head]
        for module in tail:
            self.connect(module)
        self.node_number = next(self._NodeNumberCounter)
        self._prev_isle: typing.Optional['HWIsle'] = None
        self._next_isle: typing.Optional['HWIsle'] = None

    def __str__(self) -> str:
        return self.to_xml_str()

    def __repr__(self) -> str:
        cls_name = self.__class__.__name__
        tail = ", ".join(repr(module) for module in self.tail)
        return f'{cls_name}(head={repr(self.head)}, tail=*[{tail}])'

    @typing.overload
    def __getitem__(self, i: int) -> 'HWModule':
        ...

    @typing.overload
    def __getitem__(self, s: slice) -> list['HWModule']:
        ...

    def __getitem__(self, index: typing.Union[int, slice]):
        return self._modules[index]

    def __len__(self) -> int:
        return len(self._modules)

    @staticmethod
    def is_cpu(module_type: str) -> bool:
        allowed = ['X20cCP1584']
        return module_type in allowed

    @staticmethod
    def is_isle_head(module_type: str) -> bool:
        allowed = ['X20cCP1584', 'X20cSL8101', 'X20cBC0083', 'X20cBC8083']
        return module_type in allowed

    @property
    def head(self):
        return self._modules[0]

    @property
    def tail(self):
        return self._modules[1:]

    @property
    def prev_isle(self) -> typing.Optional['HWIsle']:
        return self._prev_isle

    @prev_isle.setter
    def prev_isle(self, isle: 'HWIsle') -> None:
        isle._connect_isle(self)
        self._prev_isle = isle

    @property
    def next_isle(self) -> typing.Optional['HWIsle']:
        return self._next_isle

    @next_isle.setter
    def next_isle(self, isle: 'HWIsle') -> None:
        self._connect_isle(isle)
        isle._prev_isle = self

    @staticmethod
    def _get_module_bm(module: HWModule) -> HWModule:
        for dep in module.dependencies.values():
            if is_bm(dep):
                return dep
        raise ValueError(
            f'Module "{module.name}" of type "{module.type}" '
            f'does not have a Bus Module or Bus Base depencency.'
            )

    def _get_tail_connector(self) -> tuple[HWModule, str]:
        connect_to = self._modules[-1]
        match connect_to.type:
            case "X20cCP1584":
                return connect_to, "IF6"
            case "X20cSL8101":
                return connect_to, "IF1"
            case "X20cBC0083" | "X20cBC8083":
                return self._get_module_bm(connect_to), "IF1"
            case _:
                return self._get_module_bm(connect_to), "X2X2"

    def _connect_to_cp1584(self, to_connect: 'HWIsle') -> None:
        to_connect.head.add_connection_plk(
            connector="PLK1",
            target_module=self.head,
            target_connector="IF3",
            node_number=self.node_number,
            cable_length=self.POWERLINK_CABLE_LENGTH,
            cable_version=self.POWERLINK_CABLE_VERSION
            )

    def _connect_to_head(
        self, connector: str, target: 'HWIsle', target_connector: str
    ) -> None:
        self.head.add_connection_plk(
            connector=connector,
            target_module=target.head,
            target_connector=target_connector,
            node_number=self.node_number,
            cable_length=self.POWERLINK_CABLE_LENGTH,
            cable_version=self.POWERLINK_CABLE_VERSION
        )
        target.head.add_connection_plk(
            connector=target_connector,
            target_module=self.head,
            target_connector=connector,
            node_number=target.node_number,
            cable_length=self.POWERLINK_CABLE_LENGTH,
            cable_version=self.POWERLINK_CABLE_VERSION
        )

    def _connect_to_sl0101_bc0083(self, to_connect: 'HWIsle') -> None:
        self._connect_to_head("PLK2", to_connect, "PLK1")

    def _connect_to_bc8083(self, to_connect: 'HWIsle') -> None:

        def get_module_dep_hb2881(module: 'HWModule') -> 'HWModule' | None:
            for dep in module.dependencies.values():
                if dep.type == "X20cHB2881":
                    return dep
            return None

        if self.head.type != "X20cBC8083":
            self._connect_to_head("PLK2", to_connect, "PLK1")
        else:
            to_connect_hb2881 = get_module_dep_hb2881(to_connect.head)
            isle_head_hb2881 = get_module_dep_hb2881(self.head)
            if to_connect_hb2881 and isle_head_hb2881:
                isle_head_hb2881.add_connection_plk(
                    connector="ETH2",
                    target_module=to_connect_hb2881,
                    target_connector="ETH1",
                    cable_length=self.POWERLINK_CABLE_LENGTH,
                    cable_version=self.POWERLINK_CABLE_VERSION
                )
                to_connect_hb2881.add_connection_plk(
                    connector="ETH1",
                    target_module=isle_head_hb2881,
                    target_connector="ETH2",
                    cable_length=self.POWERLINK_CABLE_LENGTH,
                    cable_version=self.POWERLINK_CABLE_VERSION
                )
            else:
                self._connect_to_head("PLK2", to_connect, "PLK1")

    def _connect_isle(self, isle: 'HWIsle'):
        connectors = {
            'X20cCP1584': self._connect_to_cp1584,
            'X20cSL8101': self._connect_to_sl0101_bc0083,
            'X20cBC0083': self._connect_to_sl0101_bc0083,
            'X20cBC8083': self._connect_to_bc8083
        }
        connector = connectors[self.head.type]
        connector(isle)
        self._next_isle = isle

    def connect(self, module: typing.Union[HWModule, 'HWIsle']) -> None:
        if isinstance(module, HWIsle):
            self.next_isle = module
            return
        if self.is_isle_head(module.type):
            raise TypeError(
                f'Module "{module.name}" of type "{module.type}" '
                f'must be added as a hardware isle object.'
                )
        module_bm = self._get_module_bm(module)
        target_module, target_connector = self._get_tail_connector()
        module_bm.add_connection("X2X1", target_module, target_connector)
        self._modules.append(module)

    def to_xml_elements(
        self, with_connected_isles: bool = True
    ) -> list['XMLElement']:

        def get_xml_elements(isle: 'HWIsle') -> list['XMLElement']:
            elements = []
            for module in isle._modules:
                elements.extend(module.to_xml_elements())
            return elements

        xml_elements = get_xml_elements(self)
        if with_connected_isles is False:
            return xml_elements
        prev_isle = self.prev_isle
        while prev_isle:
            prev_xml_elements = get_xml_elements(prev_isle)
            xml_elements = prev_xml_elements + xml_elements
            prev_isle = prev_isle.prev_isle
        next_isle = self.next_isle
        while next_isle:
            next_xml_element = get_xml_elements(next_isle)
            xml_elements = xml_elements + next_xml_element
            next_isle = next_isle.next_isle
        return xml_elements

    def to_xml_str(self, with_connected_isles: bool = True) -> str:
        return "".join(
            module.to_str()
            for module in self.to_xml_elements(with_connected_isles)
            )
