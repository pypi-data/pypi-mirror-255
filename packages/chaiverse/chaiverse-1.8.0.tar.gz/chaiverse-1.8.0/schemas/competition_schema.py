from datetime import datetime
from enum import Enum
from typing import List, Literal, NamedTuple, Optional

from pydantic import BaseModel, Extra, Field, NonNegativeFloat, root_validator, PrivateAttr, validator

from chaiverse.schemas.date_range_schema import DateRange, BoundedDateRange


class CompetitionChatRouting(BaseModel):
    percentage: NonNegativeFloat = Field(default=100)

    @validator('percentage')
    def validate_percentage(cls, value):
        assert value <= 100, 'percentage more than 100'
        return value


class Competition(BaseModel, extra=Extra.allow):
    competition_id: str
    leaderboard_format: Optional[str]
    leaderboard_should_use_feedback: Optional[bool]
    submission_date_range: Optional[DateRange]
    evaluation_date_range: Optional[BoundedDateRange]
    chat_routing: CompetitionChatRouting = Field(default=CompetitionChatRouting())
    enrolled_submission_ids: Optional[List[str]]
    created_at: Optional[datetime]

    @root_validator
    def validate_date_ranges(cls, values):
        submission_date_range = values.get('submission_date_range')
        evaluation_date_range = values.get('evaluation_date_range')
        if evaluation_date_range:
            assert submission_date_range, 'missing submission_date_rage'
            assert evaluation_date_range.start_epoch_time >= submission_date_range.end_epoch_time, 'evaluation starts before submission completes'
        return values
