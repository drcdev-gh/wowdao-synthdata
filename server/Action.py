import enum
from enum import Enum
import json
import uuid


class Action:
    def __init__(self, action_type, context, target_url):
        self.action_id   = uuid.uuid1()
        self.action_type = action_type
        self.context     = context
        self.target_url  = target_url
        self.step        = None

    def to_json(self):
        return json.dumps({
            'action_id': str(self.action_id),
            'action_type': str(self.action_type),
            'context': self.context,
        }, indent=4)

    def array_to_json(array):
        options = ""
        for action in array:
            options += action.to_json() + "\n"

        return options

    def __str__(self):
        return self.to_json()


class ActionType(Enum):
    QUERY_GOAL                = enum.auto()
    BACK_TO_SEARCH_RESULTS    = enum.auto()
    CLICK_SEARCH_RESULT       = enum.auto()
    CLICK_RECOMMENDED         = enum.auto()
    BUY_NOW                   = enum.auto()