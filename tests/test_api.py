"""Test HTTP API."""

from http import HTTPStatus

from fastapi.testclient import TestClient

from main import app
from tests.utils import s_time

client = TestClient(app)


def test_api_convert_success():
    response = client.post('/convert', json={
        'monday': [
            {
                'type': 'open',
                'value': s_time(10),
            },
            {
                'type': 'close',
                'value': s_time(18),
            },
        ]
    })
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'output': ['Monday: 10 AM - 6 PM'],
    }


def test_api_convert_wrong_data_format_fails():
    response = client.post('/convert', json={
        'test': 'fail',
    })
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_api_convert_wrong_method_fails():
    response = client.get('/convert')
    assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED
