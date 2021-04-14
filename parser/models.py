"""Models of input data."""

from enum import Enum
from typing import List, Tuple, Dict

from pydantic import BaseModel, validator, root_validator, Extra, PositiveInt


class WeekDaysEnum(str, Enum):
    """Enumerator of weekdays."""
    SUNDAY = 'sunday'
    MONDAY = 'monday'
    TUESDAY = 'tuesday'
    WEDNESDAY = 'wednesday'
    THURSDAY = 'thursday'
    FRIDAY = 'friday'
    SATURDAY = 'saturday'

    def _get_shifted_day(self, shift: int) -> 'WeekDaysEnum':
        weekdays: Tuple = tuple(self.__class__)
        return weekdays[(weekdays.index(self) + shift) % 7]

    @property
    def prev(self) -> 'WeekDaysEnum':
        """Return previous weekday."""
        return self._get_shifted_day(-1)

    @property
    def next(self) -> 'WeekDaysEnum':
        """Return next weekday."""
        return self._get_shifted_day(1)


class ActionTypeEnum(str, Enum):
    """Enumerator of actions types."""
    OPEN = 'open'
    CLOSE = 'close'


class ActionModel(BaseModel, extra=Extra.forbid):
    """Action item model."""
    type: ActionTypeEnum
    value: PositiveInt

    @validator('value')
    @classmethod
    def validate_max_value(cls, value: int) -> int:
        """Validate maximum number of value."""
        if value > 86399:
            raise ValueError('Must be <= 86399')

        return value


class DataModel(BaseModel):
    """Input data model."""
    __root__: Dict[WeekDaysEnum, List[ActionModel]]

    @classmethod
    def _validate_actions_type_order(cls, weekday: WeekDaysEnum, action: ActionModel,
                                     prev_action: ActionModel):
        if action.type == prev_action.type:
            raise ValueError((
                f'Wrong actions for "{weekday}", two actions in a row '
                f'can\'t be of type "{action.type}"'
            ))

    @classmethod
    def _validate_actions_values_order(cls, weekday: WeekDaysEnum, action: ActionModel,
                                       prev_action: ActionModel):
        if prev_action.value == action.value:
            raise ValueError((
                f'Wrong actions for "{weekday}", multiple items have the '
                f'same value "{action.value}"'
            ))

        if prev_action.value >= action.value:
            raise ValueError((
                f'Wrong actions for "{weekday}", the value "{prev_action.value}" '
                f'must be after "{action.value}"'
            ))

    @classmethod
    def _validate_first_action(cls, weekday: WeekDaysEnum, action: ActionModel,
                               data: Dict[WeekDaysEnum, List[ActionModel]]):
        if action.type == ActionTypeEnum.CLOSE:
            prev_actions = data.get(weekday.prev, [])
            if not prev_actions or prev_actions[-1].type != ActionTypeEnum.OPEN:
                raise ValueError(
                    f'The previous day before "{weekday}" must end with an "open" action',
                )

    @classmethod
    def _validate_last_action(cls, weekday: WeekDaysEnum, action: ActionModel,
                              data: Dict[WeekDaysEnum, List[ActionModel]]):
        if action.type == ActionTypeEnum.OPEN:
            next_actions = data.get(weekday.next, [])
            if not next_actions or next_actions[0].type != ActionTypeEnum.CLOSE:
                raise ValueError(
                    f'The next day after "{weekday}" should start with a "close" action',
                )

    @root_validator
    @classmethod
    def check_consistency(cls, values: Dict) -> Dict:
        """Validate input data."""
        data = values.get('__root__')
        if not data:
            return {}

        for weekday, actions in data.items():
            prev_action = None
            for index, action in enumerate(actions):
                if prev_action:
                    cls._validate_actions_type_order(weekday, action, prev_action)
                    cls._validate_actions_values_order(weekday, action, prev_action)
                if index == 0:
                    cls._validate_first_action(weekday, action, data)
                if index == len(actions) - 1:
                    cls._validate_last_action(weekday, action, data)
                prev_action = action
        return values
