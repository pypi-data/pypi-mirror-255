from dataclasses import dataclass, field
from typing import Optional, List

from .base import BaseModel
from .common import BaseApiResponse
from .mixins import DatetimeTimeMixin


@dataclass
class TranscriptSnippet(BaseModel, DatetimeTimeMixin):
    """
    A class representing the transcript snippet info.

    Refer: unknown
    """
    target_id: Optional[str] = field(default=None, repr=False)
    text: Optional[str] = field(default=None, repr=False)
    start_ms: Optional[str] = field(default=None, repr=False)
    end_ms: Optional[str] = field(default=None, repr=False)
    tracking_params: Optional[str] = field(default=None, repr=False)


@dataclass
class TranscriptResponse(BaseApiResponse):
    """
    A class representing the transcript's retrieve response info.

    Refer: unknown
    """

    items: Optional[List[TranscriptSnippet]] = field(default=None, repr=False)
