"""Tests for model validation."""

import pytest
from pydantic import error_wrappers

from parser.models import DataModel, WeekDaysEnum
from tests.utils import s_time


def test_validation_one_day_success():
    DataModel(__root__={
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


def test_validation_all_days_success():
    DataModel(__root__={
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


def test_validation_open_and_close_two_times_success():
    DataModel(__root__={
        'monday': [
            {
                'type': 'open',
                'value': s_time(9),
            },
            {
                'type': 'close',
                'value': s_time(11),
            },
            {
                'type': 'open',
                'value': s_time(16),
            },
            {
                'type': 'close',
                'value': s_time(23),
            },
        ],
    })


def test_validation_open_monday_close_tuesday_success():
    DataModel(__root__={
        'monday': [
            {
                'type': 'open',
                'value': s_time(9),
            },
        ],
        'tuesday': [
            {
                'type': 'close',
                'value': s_time(1),
            },
        ],
    })


def test_validation_open_saturday_close_sunday_success():
    DataModel(__root__={
        'saturday': [
            {
                'type': 'open',
                'value': s_time(9),
            },
        ],
        'sunday': [
            {
                'type': 'close',
                'value': s_time(1),
            },
        ],
    })


def test_validation_empty_day_success():
    DataModel(__root__={
        'monday': [],
    })


def test_validation_action_value_with_minutes_success():
    DataModel(__root__={
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


def test_validation_wrong_weekday_name_fails():
    with pytest.raises(error_wrappers.ValidationError) as exc:
        DataModel(__root__={
            'monday_s': [],
        })
    assert 'value is not a valid enumeration member' in str(exc.value)


def test_validation_actions_non_list_type_fails():
    with pytest.raises(error_wrappers.ValidationError) as exc:
        DataModel(__root__={
            'monday': 1,
        })
    assert 'value is not a valid list' in str(exc.value)


def test_validation_action_without_required_fields_fails():
    with pytest.raises(error_wrappers.ValidationError) as exc:
        DataModel(__root__={
            'monday': [
                {},
            ],
        })
    assert 'field required' in str(exc.value)


def test_validation_action_extra_field_fails():
    with pytest.raises(error_wrappers.ValidationError) as exc:
        DataModel(__root__={
            'monday': [
                {
                    'extra': None,
                },
            ],
        })
    assert 'extra fields not permitted' in str(exc.value)


def test_validation_action_type_wrong_value_fails():
    with pytest.raises(error_wrappers.ValidationError) as exc:
        DataModel(__root__={
            'monday': [
                {
                    'type': 'wrong',
                },
            ],
        })
    assert 'value is not a valid enumeration member' in str(exc.value)


def test_validation_action_value_non_int_fails():
    with pytest.raises(error_wrappers.ValidationError) as exc:
        DataModel(__root__={
            'monday': [
                {
                    'type': 'open',
                    'value': 'STRING',
                },
            ],
        })
    assert 'value is not a valid integer' in str(exc.value)


def test_validation_action_value_negative_number_fails():
    with pytest.raises(error_wrappers.ValidationError) as exc:
        DataModel(__root__={
            'monday': [
                {
                    'type': 'open',
                    'value': -1,
                },
            ],
        })
    assert 'ensure this value is greater than 0' in str(exc.value)


def test_validation_action_value_more_then_max_number_fails():
    with pytest.raises(error_wrappers.ValidationError) as exc:
        DataModel(__root__={
            'monday': [
                {
                    'type': 'open',
                    'value': s_time(24),
                },
            ],
        })
    assert 'Must be <= 86399' in str(exc.value)


def test_validation_two_actions_open_in_row_fails():
    with pytest.raises(error_wrappers.ValidationError) as exc:
        DataModel(__root__={
            'monday': [
                {
                    'type': 'open',
                    'value': s_time(8),
                },
                {
                    'type': 'open',
                    'value': s_time(9),
                },
            ],
        })
    assert (
               'Wrong actions for "monday", two actions '
               'in a row can\'t be of type "open"'
           ) in str(exc.value)


def test_validation_two_actions_close_in_row_fails():
    with pytest.raises(error_wrappers.ValidationError) as exc:
        DataModel(__root__={
            'monday': [
                {
                    'type': 'open',
                    'value': s_time(8),
                },
                {
                    'type': 'close',
                    'value': s_time(20),
                },
                {
                    'type': 'close',
                    'value': s_time(21),
                },
            ],
        })
    assert (
               'Wrong actions for "monday", two actions '
               'in a row can\'t be of type "close"'
           ) in str(exc.value)


def test_validation_actions_with_same_time_fails():
    with pytest.raises(error_wrappers.ValidationError) as exc:
        DataModel(__root__={
            'monday': [
                {
                    'type': 'open',
                    'value': s_time(8),
                },
                {
                    'type': 'close',
                    'value': s_time(8),
                },
            ],
        })
    assert (
               'Wrong actions for "monday", multiple items'
               ' have the same value "28800"') \
           in str(exc.value)


def test_validation_actions_with_wrong_time_order_fails():
    with pytest.raises(error_wrappers.ValidationError) as exc:
        DataModel(__root__={
            'monday': [
                {
                    'type': 'open',
                    'value': s_time(8),
                },
                {
                    'type': 'close',
                    'value': s_time(7),
                },
            ],
        })
    assert (
               'Wrong actions for "monday", the value "28800"'
               ' must be after "25200"') \
           in str(exc.value)


def test_validation_actions_open_without_close_no_next_day_fails():
    with pytest.raises(error_wrappers.ValidationError) as exc:
        DataModel(__root__={
            'monday': [
                {
                    'type': 'open',
                    'value': s_time(8),
                },
            ],
        })
    assert 'The next day after "monday" should start with a "close" action' in str(exc.value)


def test_validation_actions_open_without_close_empty_next_day_fails():
    with pytest.raises(error_wrappers.ValidationError) as exc:
        DataModel(__root__={
            'monday': [
                {
                    'type': 'open',
                    'value': s_time(8),
                },
            ],
            'tuesday': [],
        })
    assert 'The next day after "monday" should start with a "close" action' in str(exc.value)


def test_validation_actions_open_without_close_next_day_open_fails():
    with pytest.raises(error_wrappers.ValidationError) as exc:
        DataModel(__root__={
            'monday': [
                {
                    'type': 'open',
                    'value': s_time(8),
                },
            ],
            'tuesday': [
                {
                    'type': 'open',
                    'value': s_time(8),
                },
            ],
        })
    assert 'The next day after "monday" should start with a "close" action' in str(exc.value)


def test_validation_actions_starts_from_close_no_prev_day_fails():
    with pytest.raises(error_wrappers.ValidationError) as exc:
        DataModel(__root__={
            'tuesday': [
                {
                    'type': 'close',
                    'value': s_time(8),
                },
            ],
        })
    assert 'The previous day before "tuesday" must end with an "open" action' in str(exc.value)


def test_validation_actions_starts_from_close_empty_prev_day_fails():
    with pytest.raises(error_wrappers.ValidationError) as exc:
        DataModel(__root__={
            'monday': [],
            'tuesday': [
                {
                    'type': 'close',
                    'value': s_time(8),
                },
            ],
        })
    assert 'The previous day before "tuesday" must end with an "open" action' in str(exc.value)


def test_validation_actions_starts_from_close_empty_ends_by_close_fails():
    with pytest.raises(error_wrappers.ValidationError) as exc:
        DataModel(__root__={
            'monday': [
                {
                    'type': 'close',
                    'value': s_time(8),
                },
            ],
            'tuesday': [
                {
                    'type': 'close',
                    'value': s_time(8),
                },
            ],
        })
    assert 'The previous day before "monday" must end with an "open" action' in str(exc.value)
