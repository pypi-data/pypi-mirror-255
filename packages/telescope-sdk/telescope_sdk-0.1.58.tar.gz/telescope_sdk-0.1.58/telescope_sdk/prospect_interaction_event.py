from enum import Enum
from typing import Optional

from telescope_sdk.common import UserFacingDataType


class ProspectInteractionEventType(str, Enum):
    PROSPECT_REPLIED_POSITIVE = 'PROSPECT_REPLIED_POSITIVE'
    PROSPECT_REPLIED_NEGATIVE = 'PROSPECT_REPLIED_NEGATIVE'
    PROSPECT_REPLIED_UNKNOWN_SENTIMENT = 'PROSPECT_REPLIED_UNKNOWN_SENTIMENT'
    PROSPECT_BOUNCE_NOTIFICATION = 'PROSPECT_BOUNCE_NOTIFICATION'
    PROSPECT_OOO_NOTIFICATION = 'PROSPECT_OOO_NOTIFICATION'


class ProspectInteractionEvent(UserFacingDataType):
    campaign_id: str
    prospect_id: str
    type: ProspectInteractionEventType
    thread_id: Optional[str] = None
    sent_at: Optional[str] = None
    subject: Optional[str] = None
    text_reply: Optional[str] = None
    is_auto_reply: Optional[bool] = None
