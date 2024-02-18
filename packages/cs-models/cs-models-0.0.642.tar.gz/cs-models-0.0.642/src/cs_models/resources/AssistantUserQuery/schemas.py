from marshmallow import Schema, fields

from .models import AssistantUserQueryStatusEnum
from ..AssistantCommand.schemas import (
    AssistantCommandResourceSchema,
)


class AssistantUserQueryResourceSchema(Schema):
    id = fields.Integer(dump_only=True)
    session_id = fields.Integer(required=True)
    value = fields.String(required=True)
    type = fields.String(required=True)
    status = fields.Enum(AssistantUserQueryStatusEnum, required=True, by_value=True)
    commands = fields.Nested(
        AssistantCommandResourceSchema(exclude=("user_query_id",)),
        many=True,
        dump_only=True,
    )
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
