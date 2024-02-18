from enum import Enum
from typing import Optional


class PageType(Enum):
    ACTION: str = "action"
    REPORT: str = "report"
    RECORD: str = "recordType"
    INTERFACE: str = "interface"


class Page:
    """
    Class representing a single Page within a site
    """

    def __init__(self, page_name: str, page_type: PageType, group_name: Optional[str] = None) -> None:
        self.page_name = page_name
        self.page_type = page_type
        self.group_name = group_name

    def __str__(self) -> str:
        page_info = f"Page(name={self.page_name}, type={self.page_type}, group={self.group_name})"
        return page_info

    def __repr__(self) -> str:
        return self.__str__()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Page):
            return False
        if self.page_name != other.page_name:
            return False
        if self.page_type != other.page_type:
            return False
        if self.group_name != other.group_name:
            return False
        return True