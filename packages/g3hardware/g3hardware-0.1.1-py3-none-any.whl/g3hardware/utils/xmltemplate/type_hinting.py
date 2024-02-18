import typing


class XMLElementData(typing.TypedDict):
    tag: str
    attributes: typing.NotRequired[dict[str, typing.Any]]
    text: typing.NotRequired[str]
    isTemplate: typing.NotRequired[bool]


class XMLElementRecursiveData(XMLElementData):
    children: typing.NotRequired[
        typing.Union[
            'XMLElementRecursiveData', list['XMLElementRecursiveData'], None
            ]
        ]


class XMLPIData(typing.TypedDict):
    target: str
    params: typing.NotRequired[dict[str, str]]


class XMLFileData(typing.TypedDict):
    declaration: typing.NotRequired[
        typing.Union[dict[str, str], None]
        ]
    processingInstructions: typing.NotRequired[
        typing.Union[XMLPIData, list[XMLPIData], None]
        ]
    root: XMLElementRecursiveData
