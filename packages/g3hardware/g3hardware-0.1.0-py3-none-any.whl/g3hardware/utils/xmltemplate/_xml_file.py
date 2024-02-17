import json
import typing

from ._xml_element import XMLElement, create_xml_element_recursive
from ._xml_prolog import XMLDeclaration, XMLProcessingInstruction
from .type_hinting import XMLFileData


class XMLFile:
    def __init__(
        self,
        root: XMLElement,
        declaration: typing.Optional[XMLDeclaration] = None,
        pis: typing.Optional[typing.Iterable[XMLProcessingInstruction]] = None
    ) -> None:
        self.root = root
        self.declaration = declaration
        if pis is None:
            pis = []
        self.pis = [pi for pi in pis]

    def __str__(self):
        return self.to_str()

    @classmethod
    def from_template_file(cls, file_path: str) -> typing.Self:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        return cls.from_dict(data)

    @classmethod
    def from_template(cls, template: str) -> typing.Self:
        data = json.loads(template)
        return cls.from_dict(data)

    @classmethod
    def from_dict(cls, data: XMLFileData) -> typing.Self:
        declaration_data = data.get('declaration')
        if declaration_data:
            declaration = XMLDeclaration.from_dict(declaration_data)
        else:
            declaration = None
        pis_data = data.get('processingInstructions')
        pis = []
        if isinstance(pis_data, dict):
            pis.append(XMLProcessingInstruction.from_dict(pis_data))
        elif isinstance(pis_data, (list, tuple, set)):
            for pi_data in pis_data:
                pis.append(XMLProcessingInstruction.from_dict(pi_data))
        root = create_xml_element_recursive(data['root'])
        return cls(root, declaration, pis)

    def to_str(self) -> str:
        """Generate a string representation of the XML file."""
        lines = []
        if self.declaration:
            lines.extend(str(self.declaration).splitlines())
        for pi in self.pis:
            lines.extend(str(pi).splitlines())
        if self.root:
            lines.extend(str(self.root).splitlines())
        return "\n".join(line for line in lines if line)
