"""Test TypeController"""
import json
import base64
import time
from collections import namedtuple
import pytest
from flask import Flask
import models.Type
import models.User
from app import initialize_app


app = Flask(__name__)
app = initialize_app(app)
client = app.test_client
generic_type = models.Type.Type(
        value='test',
        description='test')
generic_user = models.User.User(
        idType=1,
        email='test@test.com',
        username='test',
        password='password',
        salt='test',
        dateInsertion='03/02/2018',
        dateUpdate='10/02/2018')


def auth(generic_user=generic_user):
    """Method used to authenticate user"""
    creds = base64.b64encode(
        bytes(
            generic_user.username+":"+generic_user.password,
            'utf-8')).decode('utf-8')
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': 'Basic %s' % creds
    }
    resp = client().post(
        '/api/gyresources/token/',
        headers=headers,
        follow_redirects=True)
    resp = json.loads(resp.get_data(as_text=True))
    token = resp['response']
    generic_user.password = 'password'
    return (generic_user, token)


generic_user = models.User.User(
    id=generic_user.id,
    idType=generic_user.idType,
    email=generic_user.email,
    username=generic_user.username,
    password='password',
    salt=generic_user.salt,
    dateInsertion=generic_user.dateInsertion,
    dateUpdate=generic_user.dateUpdate)


@pytest.mark.order1
def test_search_by_unexistent_id():
    data = {
            "action": "searchByID",
            "id": "1000000",
            }
    resp = client().get(
            '/api/gyresources/types',
            content_type='application/json',
            headers={
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'dataType': 'json',
                'timeout': 240},
            query_string=data, follow_redirects=True)
    assert json.loads(resp.get_data(as_text=True))['status_code'] == 500


@pytest.mark.order2
def test_create(generic_type=generic_type, generic_user=generic_user):
    (generic_user, token) = auth(generic_user)
    data = generic_type.__dict__
    headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': 'Bearer %s' % token['token']
            }
    resp = client().post('/api/gyresources/types/', data=str(
        json.dumps(data)), headers=headers)
    type = json.loads(resp.get_data(as_text=True))['response']
    type = namedtuple("Type", type.keys())(*type.values())
    generic_type = type
    assert resp.status_code == 200
    assert "'id': 0" not in json.loads(resp.get_data(as_text=True))['response']


@pytest.mark.order3
def test_search_by_id():
    data = {
            "action": "searchByID",
            "id": "4",
            }
    resp = client().get(
            '/api/gyresources/types',
            content_type='application/json',
            headers={
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'dataType': 'json',
                'timeout': 240},
            query_string=data, follow_redirects=True)
    assert json.loads(resp.get_data(as_text=True))['status_code'] == 200
    assert 'test' in json.loads(
            resp.get_data(as_text=True))['response']['value']


@pytest.mark.order4
def test_search():
    data = {
                "action": "search",
                "value": "test",
                "description": "test",
                "pageSize": 10,
                "offset": 0
            }
    resp = client().get(
            '/api/gyresources/types',
            content_type='application/json',
            headers={
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'dataType': 'json'},
            query_string=data, follow_redirects=True)
    pagedResponse = json.loads(resp.get_data(as_text=True))
    assert pagedResponse['status_code'] == 200
    for response in pagedResponse['response']:
        assert 'test' in response['description']


@pytest.mark.order5
def test_update(generic_type=generic_type, generic_user=generic_user):
    (generic_user, token) = auth(generic_user)
    data = generic_type.__dict__
    data['action'] = 'search'
    resp = client().get(
            '/api/gyresources/types',
            content_type='application/json',
            headers={
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'dataType': 'json'},
            query_string=data, follow_redirects=True)
    pagedResponse = json.loads(resp.get_data(as_text=True))
    type = object()
    for response in pagedResponse['response']:
        type = namedtuple("Type", response.keys())(*response.values())

    type = {
                "id": type.id,
                "value": type.value,
                "description": 'update'
            }
    generic_type.description = 'update'
    headers = {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'Authorization': 'Bearer %s' % token['token']
              }
    resp = client().put('/api/gyresources/types/', data=str(
        json.dumps(type)), headers=headers)
    assert resp.status_code == 200
    type = json.loads(
                resp.get_data(as_text=True))
    type = namedtuple("Type", type.keys())(*type.values())
    assert "update" in type.response['description']


@pytest.mark.order6
def test_delete(generic_type=generic_type, generic_user=generic_user):
    (generic_user, token) = auth(generic_user)
    data = generic_type.__dict__
    data['action'] = 'search'
    resp = client().get(
            '/api/gyresources/types',
            content_type='application/json',
            headers={
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'dataType': 'json'},
            query_string=data, follow_redirects=True)
    pagedResponse = json.loads(resp.get_data(as_text=True))
    type = object()
    for response in pagedResponse['response']:
        type = namedtuple("Type", response.keys())(*response.values())

    type = {
                "id": type.id,
                "value": type.value,
                "description": type.description
            }

    headers = {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'Authorization': 'Bearer %s' % token['token']
              }
    resp = client().delete('/api/gyresources/types/', data=str(
        json.dumps(type)), headers=headers)
    assert resp.status_code == 200
    assert 204 == json.loads(
        resp.get_data(as_text=True))['status_code']


@pytest.mark.order7
def test_search_with_page_size_and_offset():
    data = {
                "action": "search",
                "value": "test",
                "description": "test",
                "pageSize": 10,
                "offset": 0
            }
    resp = client().get(
            '/api/gyresources/types',
            content_type='application/json',
            headers={
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'dataType': 'json'},
            query_string=data, follow_redirects=True)
    pagedResponse = json.loads(resp.get_data(as_text=True))
    assert pagedResponse['status_code'] == 200
    for response in pagedResponse['response']:
        assert 'large' in response['value']


@pytest.mark.order8
def test_create_empty(generic_type=generic_type, generic_user=generic_user):
    (generic_user, token) = auth(generic_user)
    type_aux = generic_type
    type_aux.value = ''
    type_aux.description = ''
    data = type_aux.__dict__
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': 'Bearer %s' % token['token']
        }
    resp = client().post('/api/gyresources/types/', data=str(
        json.dumps(data)), headers=headers)
    resp = json.loads(
        resp.get_data(as_text=True))
    assert resp['status_code'] == 500


@pytest.mark.order9
def test_update_wrong_id(
        generic_type=generic_type,
        generic_user=generic_user):
    (generic_user, token) = auth(generic_user)
    data = generic_type.__dict__
    data['action'] = 'search'
    resp = client().get(
        '/api/gyresources/types',
        content_type='application/json',
        headers={
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'dataType': 'json'},
        query_string=data, follow_redirects=True)
    pagedResponse = json.loads(resp.get_data(as_text=True))
    type_model = object()
    for response in pagedResponse['response']:
        type_model = namedtuple("Type", response.keys())(*response.values())

    type_model = {
        "id": 1000,
        "value": type_model.value,
        "description": 'update'
    }
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': 'Bearer %s' % token['token']
    }
    resp = client().put('/api/gyresources/types/', data=str(
        json.dumps(type_model)), headers=headers)
    resp = json.loads(
        resp.get_data(as_text=True))
    assert resp['status_code'] == 500
    assert 'Internal server error' in resp['message']


@pytest.mark.order10
def test_delete_non_existent(
        generic_type=generic_type,
        generic_user=generic_user):
    (generic_user, token) = auth(generic_user)
    data = generic_type.__dict__
    data['action'] = 'search'
    resp = client().get(
        '/api/gyresources/types',
        content_type='application/json',
        headers={
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'dataType': 'json'},
        query_string=data, follow_redirects=True)
    pagedResponse = json.loads(resp.get_data(as_text=True))
    type_model = object()
    for response in pagedResponse['response']:
        type_model = namedtuple("Type", response.keys())(*response.values())

    type_model = {
        "id": 1000,
        "value": type_model.value,
        "description": type_model.description
    }
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': 'Bearer %s' % token['token']
    }
    resp = client().delete('/api/gyresources/types/', data=str(
        json.dumps(type_model)), headers=headers)
    resp = json.loads(
        resp.get_data(as_text=True))
    assert resp['status_code'] == 500
    assert 'Internal server error' in resp['message']


@pytest.mark.order11
def test_expire_token(generic_type=generic_type, generic_user=generic_user):
    (generic_user, token) = auth(generic_user)
    time.sleep(241)
    type_aux = generic_type
    type_aux.value = ''
    type_aux.description = ''
    data = type_aux.__dict__
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': 'Bearer %s' % token['token']
        }
    resp = client().post('/api/gyresources/types/', data=str(
        json.dumps(data)), headers=headers)
    assert 'UNAUTHORIZED' in str(resp)
