"""Convertor class."""

from copy import deepcopy
from datetime import datetime
from typing import Dict, Iterator, Tuple, List, Union

from parser.models import ActionTypeEnum, WeekDaysEnum, ActionModel, DataModel


class Convertor:
    """Convert input data to human-readable format."""

    def __init__(self, data: DataModel):
        self.data = data.__root__

    @staticmethod
    def _seconds_to_time_string(seconds: int) -> str:
        time = datetime.utcfromtimestamp(seconds)
        if time.minute:
            return time.strftime('%-I.%M %p')

        return time.strftime('%-I %p')

    @staticmethod
    def _humanize_action_item(value: Union[str, List[Tuple[str, str]]]) -> str:
        if isinstance(value, str):
            return value

        return ', '.join(' - '.join(pair) for pair in value)

    def _get_normalized_data(self) -> Dict[WeekDaysEnum, List[ActionModel]]:
        data = deepcopy(self.data)
        for weekday, actions in data.items():
            if not actions:
                continue

            if actions[0].type == ActionTypeEnum.CLOSE:
                data[weekday.prev].append(actions.pop(0))
        return data

    def get_parsed_data(self) -> Iterator[Tuple[str, Union[str, List[Tuple[str, str]]]]]:
        """Return data in convenient format."""
        data = self._get_normalized_data()
        for weekday, actions in data.items():
            if actions:
                actions_pairs = zip(actions[::2], actions[1::2])
                yield weekday.capitalize(), [
                    (
                        self._seconds_to_time_string(open_action.value),
                        self._seconds_to_time_string(close_action.value),
                    ) for open_action, close_action in actions_pairs
                ]
            else:
                yield weekday.capitalize(), 'Closed'

    def get_humanized_data(self) -> Iterator[str]:
        """Return data in human-readable format."""
        for weekday, value in self.get_parsed_data():
            yield '{weekday}: {value}'.format(
                weekday=weekday,
                value=self._humanize_action_item(value),
            )
