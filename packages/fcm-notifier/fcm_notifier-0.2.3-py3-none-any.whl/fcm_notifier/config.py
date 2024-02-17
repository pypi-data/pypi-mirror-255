import configparser
from typing import (
    List,
    Optional,
    Tuple,
    Union,
)


class Config:
    """Обертка над парсером параметров конфигурации."""

    def __init__(self, filenames: Optional[Union[List[str], Tuple[str, ...]]] = None) -> None:
        self.parser = configparser.ConfigParser()
        if filenames:
            self.parser.read(filenames)

    def get(self, section, option, default: Optional[str] = None) -> Optional[str]:
        """Безопасно возвращает значение параметра option из раздела section."""
        value = self.parser.get(section, option, fallback=None) or default
        if value:
            return value.strip()

    def get_int(self, section, option, default: Optional[int] = None) -> Optional[int]:
        """Безопасно возвращает целое число из конфига."""
        value = self.get(section, option) or default
        try:
            value = int(value)
        except (ValueError, TypeError):
            value = None

        return value
