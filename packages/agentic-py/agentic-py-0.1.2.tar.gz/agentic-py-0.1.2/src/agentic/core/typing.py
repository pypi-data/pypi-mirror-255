from typing import ClassVar, Dict, Protocol


class IsDataclass(Protocol):
    # Apparently this is the most reliable way to check if something is a dataclass
    __dataclass_fields__: ClassVar[Dict]
