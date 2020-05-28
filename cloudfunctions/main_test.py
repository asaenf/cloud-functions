from unittest import mock

import flask
import main
import pytest
from mockfirestore import MockFirestore


@pytest.fixture(scope="module")
def app():
    return flask.Flask(__name__)


@mock.patch('main.get_database_client')
def test_get(get_database_client, app):
    mock_db = MockFirestore()
    get_database_client.return_value = mock_db
    mock_db.collection('items').document('test').set({'quantity': 1})

    expected = {'quantity': 1}
    with app.test_request_context(query_string={'item': 'test'}):
        res = main.get(flask.request)
        assert res.status_code == 200
        assert expected == res.get_json()


@mock.patch('main.get_database_client')
def test_get_all(get_database_client, app):
    mock_db = MockFirestore()
    get_database_client.return_value = mock_db
    mock_db.collection('items').document('test').set({'quantity': 1})
    mock_db.collection('items').document('test2').set({'quantity': 2})

    expected = [{"test": {'quantity': 1}}, {"test2": {'quantity': 2}}]
    with app.test_request_context():
        res = main.get(flask.request)
        assert res.status_code == 200
        assert expected == res.get_json()


@mock.patch('main.get_database_client')
def test_get_not_found(get_database_client, app):
    mock_db = MockFirestore()
    get_database_client.return_value = mock_db

    with app.test_request_context(query_string={'item': 'test'}):
        res = main.get(flask.request)
        assert res.status_code == 404


@mock.patch('main.get_database_client')
def test_incorrect_content_type(get_database_client, app):
    mock_db = MockFirestore()
    get_database_client.return_value = mock_db

    with app.test_request_context(json={'item': 'test'},
                                  content_type='application/x-www-form-urlencoded'):
        res = main.post(flask.request)
        assert res.status_code == 400


@mock.patch('main.get_database_client')
def test_put_creates_if_doesnt_exist(get_database_client, app):
    mock_db = MockFirestore()
    get_database_client.return_value = mock_db

    expected = {'quantity': 1}
    with app.test_request_context(json={"item": "item1", "quantity": 1},
                                  content_type="application/json",
                                  method='PUT'
                                  ):
        res = main.put(flask.request)
        assert res.status_code == 201
        assert expected == res.get_json()
        doc = mock_db.collection('items').document('item1').get()
        assert doc.to_dict() == expected


@mock.patch('main.get_database_client')
def test_put_if_already_exist(get_database_client, app):
    mock_db = MockFirestore()
    get_database_client.return_value = mock_db

    mock_db.collection('items').document('item1').set({'quantity': 1})
    with app.test_request_context(json={"item": "item1", "quantity": 1},
                                  content_type="application/json",
                                  method='PUT'
                                  ):
        res = main.put(flask.request)
        assert res.status_code == 409


@mock.patch('main.get_database_client')
def test_incorrect_payload(get_database_client, app):
    mock_db = MockFirestore()
    get_database_client.return_value = mock_db

    # missing quantity
    with app.test_request_context(json={"item": "item1"},
                                  content_type="application/json",
                                  method='PUT'):
        res = main.put(flask.request)
        assert res.status_code == 400


@mock.patch('main.get_database_client')
def test_post_updates(get_database_client, app):
    mock_db = MockFirestore()
    get_database_client.return_value = mock_db

    mock_db.collection('items').document('item1').set({'quantity': 1})
    expected = {'quantity': 4}
    with app.test_request_context(json={"item": "item1", "quantity": 4},
                                  content_type="application/json",
                                  method='POST'
                                  ):
        res = main.post(flask.request)
        assert res.status_code == 200
        assert expected == res.get_json()
        doc = mock_db.collection('items').document('item1').get()
        assert doc.to_dict() == expected


@mock.patch('main.get_database_client')
def test_post_not_existing(get_database_client, app):
    mock_db = MockFirestore()
    get_database_client.return_value = mock_db

    with app.test_request_context(json={"item": "item1", "quantity": 4},
                                  content_type="application/json",
                                  method='POST'
                                  ):
        res = main.post(flask.request)
        assert res.status_code == 404
