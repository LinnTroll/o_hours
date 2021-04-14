"""Tests for workdays convertor."""

import pytest

from parser.convertor import Convertor
from parser.models import DataModel, WeekDaysEnum
from tests.utils import s_time


def test_convert_one_day():
    data = DataModel(__root__={
        'monday': [
            {
                'type': 'open',
                'value': s_time(10),
            },
            {
                'type': 'close',
                'value': s_time(18),
            },
        ],
    })
    convertor = Convertor(data)
    result = list(convertor.get_parsed_data())
    assert result == [
        ('Monday', [('10 AM', '6 PM')]),
    ]


def test_convert_one_day_closed():
    data = DataModel(__root__={
        'monday': [],
    })
    convertor = Convertor(data)
    result = list(convertor.get_parsed_data())
    assert result == [
        ('Monday', 'Closed'),
    ]


def test_convert_all_days():
    data = DataModel(__root__={
        weekday.value: [
            {
                'type': 'open',
                'value': s_time(10),
            },
            {
                'type': 'close',
                'value': s_time(18),
            },
        ]
        for weekday in list(WeekDaysEnum)
    })
    convertor = Convertor(data)
    result = list(convertor.get_parsed_data())
    assert result == [
        ('Sunday', [('10 AM', '6 PM')]),
        ('Monday', [('10 AM', '6 PM')]),
        ('Tuesday', [('10 AM', '6 PM')]),
        ('Wednesday', [('10 AM', '6 PM')]),
        ('Thursday', [('10 AM', '6 PM')]),
        ('Friday', [('10 AM', '6 PM')]),
        ('Saturday', [('10 AM', '6 PM')]),
    ]


def test_convert_multiple_openings_per_day():
    data = DataModel(__root__={
        'monday': [
            {
                'type': 'open',
                'value': s_time(10),
            },
            {
                'type': 'close',
                'value': s_time(14),
            },
            {
                'type': 'open',
                'value': s_time(15),
            },
            {
                'type': 'close',
                'value': s_time(21),
            },
        ],
    })
    convertor = Convertor(data)
    result = list(convertor.get_parsed_data())
    assert result == [
        ('Monday', [('10 AM', '2 PM'), ('3 PM', '9 PM')]),
    ]


def test_convert_close_next_day():
    data = DataModel(__root__={
        'monday': [
            {
                'type': 'open',
                'value': s_time(10),
            },
        ],
        'tuesday': [
            {
                'type': 'close',
                'value': s_time(1),
            },
        ],
    })
    convertor = Convertor(data)
    result = list(convertor.get_parsed_data())
    assert result == [
        ('Monday', [('10 AM', '1 AM')]),
        ('Tuesday', 'Closed'),
    ]


def test_convert_saturday_close_next_day():
    data = DataModel(__root__={
        'saturday': [
            {
                'type': 'open',
                'value': s_time(10),
            },
        ],
        'sunday': [
            {
                'type': 'close',
                'value': s_time(1),
            },
        ],
    })
    convertor = Convertor(data)
    result = list(convertor.get_parsed_data())
    assert result == [
        ('Saturday', [('10 AM', '1 AM')]),
        ('Sunday', 'Closed'),
    ]


def test_convert_with_minutes():
    data = DataModel(__root__={
        'monday': [
            {
                'type': 'open',
                'value': s_time(10, 10),
            },
            {
                'type': 'close',
                'value': s_time(18, 15),
            },
        ],
    })
    convertor = Convertor(data)
    result = list(convertor.get_parsed_data())
    assert result == [
        ('Monday', [('10.10 AM', '6.15 PM')]),
    ]


def test_convert_humanized_data():
    data = DataModel(__root__={
        'monday': [
            {
                'type': 'open',
                'value': s_time(10),
            },
            {
                'type': 'close',
                'value': s_time(14),
            },
            {
                'type': 'open',
                'value': s_time(15),
            },
            {
                'type': 'close',
                'value': s_time(21),
            },
        ],
        'tuesday': [],
    })
    convertor = Convertor(data)
    result = list(convertor.get_humanized_data())
    assert result == [
        'Monday: 10 AM - 2 PM, 3 PM - 9 PM',
        'Tuesday: Closed',
    ]


@pytest.mark.parametrize(
    'test_input,expected',
    [
        (0, '12 AM'),
        (3600, '1 AM'),
        (43200, '12 PM'),
        (46800, '1 PM'),
        (82800, '11 PM'),
        (3900, '1.05 AM'),
        (36300, '10.05 AM'),
        (36301, '10.05 AM'),
        (86399, '11.59 PM'),
    ]
)
def test_seconds_to_time_string_method(test_input, expected):
    assert Convertor._seconds_to_time_string(test_input) == expected


@pytest.mark.parametrize(
    'test_input,expected',
    [
        ('Closed', 'Closed'),
        ([('10 AM', '1 AM')], '10 AM - 1 AM'),
        ([('10 AM', '2 PM'), ('3 PM', '21 PM')], '10 AM - 2 PM, 3 PM - 21 PM'),
    ]
)
def test_humanize_action_item_method(test_input, expected):
    assert Convertor._humanize_action_item(test_input) == expected
