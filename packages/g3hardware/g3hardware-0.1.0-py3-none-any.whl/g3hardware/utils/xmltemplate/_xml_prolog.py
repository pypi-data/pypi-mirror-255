import collections.abc
import typing

from .type_hinting import XMLPIData


class _XMLInstruction(collections.abc.MutableMapping):
    def __init__(self, target: str, **params: str) -> None:
        self._target = self._format_value(target)
        self._params = {
            param: self._format_value(value) for param, value in params.items()
            }

    def __str__(self) -> str:
        params = " ".join(
            f'{param}="{value}"' for param, value in self._params.items()
            )
        return f'<?{self._target} {params}?>'

    def __eq__(self, other: object) -> bool:
        if isinstance(other, type(self)):
            is_target_eq = self._target == other._target
            is_params_eq = self._params == other._params
            return is_target_eq and is_params_eq
        if isinstance(other, str):
            return str(self) == other
        return False

    def __getitem__(self, key: str) -> str:
        if key not in self._params:
            err_msg = f'{self.__class__.__name__} has no attribute "{key}"'
            raise AttributeError(err_msg)
        return self._params[key]

    def __setitem__(self, key, value) -> None:
        self._params[key] = self._format_value(value)

    def __delitem__(self, key) -> None:
        if key not in self._params:
            err_msg = f'{self.__class__.__name__} has no attribute "{key}"'
            raise AttributeError(err_msg)
        del self._params[key]

    def __iter__(self) -> typing.Iterator[str]:
        return iter(self._params.keys())

    def __len__(self) -> int:
        return len(self._params.keys())

    def _format_value(self, value: str) -> str:
        if isinstance(value, str):
            return value
        if isinstance(value, (str, int, float, bool)):
            return str(value)
        raise ValueError(
            f'An XML value must be set to a string, a number, or a Boolean '
            f'(got type "{value.__class__.__name__}").'
            )


class XMLDeclaration(_XMLInstruction):
    def __init__(self, **params: str) -> None:
        super().__init__(target='xml', **params)

    def __repr__(self) -> str:
        params = ", ".join(
            f'{name}="{value}"' for name, value in self._params.items()
            )
        return f'{self.__class__.__name__}({params})'

    @classmethod
    def from_dict(cls, params: dict[str, str]) -> typing.Self:
        return cls(**params)

    @property
    def target(self) -> str:
        return self._target


class XMLProcessingInstruction(_XMLInstruction):

    def __repr__(self) -> str:
        params = ", ".join(
            f'{param}="{value}"' for param, value in self._params.items()
            )
        return f'{self.__class__.__name__}(target="{self._target}", {params})'

    @classmethod
    def from_dict(cls, data: XMLPIData) -> typing.Self:
        return cls(target=data['target'], **data.get('params', {}))

    @property
    def target(self) -> str:
        return self._target

    @target.setter
    def target(self, value: str) -> None:
        self._target = self._format_value(value)
