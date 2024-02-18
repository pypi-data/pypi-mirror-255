import logging
import typing
import re

from dataclasses import dataclass, field


@dataclass
class STVariable:
    name: str
    dtype: str
    value: typing.Any
    default: typing.Any | None = field(default=None, repr=False)
    comment: str | None = field(default=None, repr=False)

    def __post_init__(self) -> None:
        self._check_name(self.name)
        self.default = self.value

    def __str__(self) -> str:
        dtype = self.dtype.lower()
        if self.value is None:
            return ''
        if (
            "char" in dtype or "string" in dtype and
            not str(self.value).startswith("'")
        ):
            return f"'{self.value}'"
        elif "time" in dtype and not str(self.value).startswith('T#'):
            return f'T#{self.value}'
        elif "bool" in dtype:
            if self.value is True:
                return "TRUE"
            else:
                return "FALSE"
        else:
            return str(self.value)

    @staticmethod
    def _check_name(name) -> None:
        if not isinstance(name, str):
            raise ValueError('Varname must be a string value.')
        if not name:
            raise ValueError('Varname cannot be an empty string.')
        if not name[0].isalpha():
            raise ValueError('Varname must start with a letter.')
        if any(not ch.isalnum() and ch != '_' for ch in name):
            raise ValueError(
                'Varname may only contain alphanumeric values and underscores.'
                )

    def to_py(self) -> typing.Any:
        dtype = self.dtype.lower()
        value = self.value
        # Array types
        if "array" in dtype:
            # array parsing is not supported at the moment
            return value
        # Custom structs as dictionaries
        elif "struct" in dtype:
            return {
                memb_name: self._convert_to_py(
                    memb_value["dtype"], memb_value["value"]
                    )
                for memb_name, memb_value in value.items()
                }
        # Primitive types
        return self._convert_to_py(dtype, value)

    def _convert_to_py(self, dtype: str, value: typing.Any) -> typing.Any:
        if value is None:
            return None
        try:
            dtype = dtype.lower()
            if "char" in dtype or "string" in dtype:
                return str(value)
            elif "int" in dtype:
                return int(value)
            elif "float" in dtype or "real" in dtype:
                return float(value)
            elif "bool" in dtype:
                return str(value).casefold() == 'true'
            elif "time" in dtype:
                time_pattern = r'^(T#)?(\d+d)?(\d+h)?(\d+m)?(\d+s)?(\d+ms)?$'
                match = re.match(time_pattern, value)
                if not match:
                    raise ValueError(f"Invalid TIME variable: {value}")
                if match.group(1):
                    return value
                if not value:
                    raise ValueError("TIME variable is an empty string")
                # add the T# prefix if not present
                return f"T#{value}"
            else:
                return value
        except Exception as exp:
            logging.warning(
                f'"{self.name}": cannot format value "{value}" to '
                f'data type "{dtype}" ({exp}). Default value '
                f'"{self.default}" will be used instead.'
                )
            return self._convert_to_py(dtype, self.default)
