import collections.abc
import typing

from lxml import etree

from .type_hinting import XMLElementData, XMLElementRecursiveData


class XMLElement(collections.abc.MutableMapping):
    def __init__(
        self,
        tag: str,
        text: typing.Optional[str] = None,
        **attributes: str
    ) -> None:
        attrs = {name: str(val) for name, val in attributes.items()}
        self._element = etree.Element(tag, attrs)
        self._element.text = text
        self._children: list['XMLElement'] = []
        self._parent: typing.Optional['XMLElement'] = None
        self._is_template: bool = False

    def __str__(self) -> str:
        return self.to_str()

    def __repr__(self) -> str:
        repr_str = f'{self.__class__.__name__}(tag={self.tag}'
        if self.text is not None:
            repr_str += f', text={self.text}'
        attrs = ", ".join(
            f'{str(name)}="{str(value)}"'
            for name, value in self._element.attrib.items()
            )
        if attrs:
            repr_str += f', {attrs})'
        else:
            repr_str += ')'
        return repr_str

    def __eq__(self, other: object) -> bool:
        if isinstance(other, XMLElement):
            return self._element == other._element
        if isinstance(other, str):
            return self._element == etree.fromstring(other)
        return False

    def __getitem__(self, key: str) -> str:
        if key not in self._element.attrib:
            err_msg = f'"{self.tag}" XML element has no attribute "{key}".'
            raise AttributeError(err_msg)
        return str(self._element.attrib[key])

    def __setitem__(self, key, value) -> None:
        self._element.attrib[key] = str(value)

    def __delitem__(self, key) -> None:
        if key not in self._element.attrib:
            err_msg = f'"{self.tag}" XML element has no attribute "{key}".'
            raise AttributeError(err_msg)
        del self._element.attrib[key]

    def __iter__(self) -> typing.Iterator:
        return iter(self._element.attrib.keys())

    def __len__(self) -> int:
        return len(self._element.attrib)

    @classmethod
    def from_dict(cls, data: XMLElementData) -> typing.Self:
        inst = cls(
            tag=data['tag'],
            text=data.get('text'),
            **data.get('attributes', {})
            )
        if data.get('isTemplate'):
            inst._is_template = True
        return inst

    @property
    def tag(self) -> str:
        return self._element.tag

    @property
    def text(self) -> str | None:
        return self._element.text

    @text.setter
    def text(self, value: str | None) -> None:
        if value is not None:
            value = str(value)
        self._element.text = value

    @property
    def attributes(self):
        return self._element.attrib

    @property
    def is_template(self) -> bool:
        return self._is_template

    def set_as_template(self) -> None:
        self._is_template = True
        if self._parent:
            self._parent._element.remove(self._element)

    @property
    def parent(self) -> typing.Optional['XMLElement']:
        return self._parent

    def add_child(self, child: 'XMLElement') -> None:
        child._parent = self
        self._children.append(child)
        if not child._is_template:
            self._element.append(child._element)

    def get_children(
        self, tag: typing.Optional[str] = None, **attributes: str
    ) -> list['XMLElement']:
        children = []
        for child in self._children:
            if child._is_template:
                continue
            if child.tag != tag and tag is not None:
                continue
            if any(
                child.get(name, "__ATTR_NOT_FOUND__") != value
                for name, value in attributes.items()
            ):
                continue
            children.append(child)
        return children

    def get_child(
        self, tag: typing.Optional[str] = None, **attributes: str
    ) -> 'XMLElement':
        children = self.get_children(tag, **attributes)
        if len(children) == 1:
            return children[0]
        attrs = ", ".join(
            f'{attr_name}="{attr_value}"'
            for attr_name, attr_value in attributes.items()
            )
        if len(children) > 1:
            raise AttributeError(
                f"Attributes '{attrs}' are ambiguous: "
                f"{len(children)} elements were found."
                )
        raise AttributeError(
            f"A child element with attributes '{attrs}' was not found."
            )

    def format(self, **kwargs) -> 'XMLElement':

        def copy_and_format(element: 'XMLElement') -> 'XMLElement':
            inst = XMLElement(element.tag, element.text, **element.attributes)
            if not element.is_template:
                return inst
            if inst.text:
                inst.text = inst.text.format(**kwargs)
            for attr in inst.attributes:
                inst[attr] = inst[attr].format(**kwargs)
            return inst

        self_copy = copy_and_format(self)
        for child in self._children:
            if child.is_template:
                self_copy.add_child(child)
            try:
                child_copy = child.format(**kwargs)
                child_copy._parent = self_copy
                self_copy.add_child(child_copy)
            except KeyError:
                pass

        return self_copy

    def to_str(self) -> str:
        return etree.tostring(
            self._element,
            pretty_print=True,
            with_tail=False,
            encoding="unicode",
            )

    def to_bytes(self) -> bytes:
        return etree.tostring(
            self._element,
            pretty_print=True,
            with_tail=False,
            encoding="utf-8",
            )


def create_xml_element_recursive(data: XMLElementRecursiveData) -> XMLElement:
    element = XMLElement.from_dict(data)
    nested_data = data.get('children')
    if not nested_data:
        return element
    if isinstance(nested_data, dict):
        element.add_child(create_xml_element_recursive(nested_data))
    elif isinstance(nested_data, list):
        for nested_item in nested_data:
            element.add_child(create_xml_element_recursive(nested_item))
    return element
