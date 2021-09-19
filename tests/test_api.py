"""
    Tests for API GET and POST.
"""
import time

import pytest

POST_URL = '/visited_links/'
GET_URL = '/visited_domains/'


def test_wrong_method(client):
    response = client.get(POST_URL)
    print(response)
    assert response.status_code == 404
    response = client.post(GET_URL)
    assert response.status_code == 404


@pytest.mark.parametrize('data', [None, b'{}', b'{link: "[[}', b'[]'])
def test_post_wrong_data(client, data):
    response = client.post(POST_URL, data, content_type='application/json')
    assert response.status_code == 400


def test_post_no_links(client):
    json_input = {'links': []}

    response = client.post(POST_URL, json_input, content_type='application/json')
    assert response.status_code == 400


def test_post_links(client):
    json_input = {
        'links': [
            'https://ya.ru',
            'https://ya.ru?q=123',
            'funbox.ru',
            'https://stackoverflow.com/questions/11828270/how-to-exit-the-vim-editor'
        ]
    }
    json_output = {'status': 'ok'}

    response = client.post(POST_URL, json_input, content_type='application/json')
    assert response.status_code == 201
    assert response.json() == json_output


def test_get_no_links(client):
    json_output = {'domains': [], 'status': 'ok'}

    response = client.get(f'{GET_URL}?from=0&to=1', content_type='application/json')
    assert response.status_code == 200
    assert response.json() == json_output


@pytest.mark.parametrize('start, end', [
    (None, None),
    ('from=100', None),
    (None, 'to=100'),
    ('from=', 'to='),
    ('from=100', 'to='),
    ('from=', 'to=100'),
    ('from=a', 'to=b'),
])
def test_get_wrong_parameters(client, start, end):
    response = client.get(f'{GET_URL}?{start}&{end}', content_type='application/json')
    assert response.status_code == 400


def test_post_and_get_with_time(client):
    json_input = {
        'links': [
            'https://ya.ru',
            'https://ya.ru?q=123',
            'funbox.ru',
            'https://stackoverflow.com/questions/11828270/how-to-exit-the-vim-editor'
        ]
    }
    current_time = round(time.time())

    # POST
    response = client.post(POST_URL, json_input, content_type='application/json')
    assert response.status_code == 201

    # GET
    response = client.get(f'{GET_URL}?from={current_time}&to={current_time + 100}', content_type='application/json')
    assert response.status_code == 200

    domains = response.json()['domains']
    assert 'ya.ru' in domains
    assert domains.count('ya.ru') == 1
    assert 'funbox.ru' in domains
    assert 'stackoverflow.com' in domains

    response = client.get(f'{GET_URL}?from={current_time + 200}&to={current_time + 300}',
                          content_type='application/json')
    assert response.status_code == 200
    domains = response.json()['domains']
    assert 'ya.ru' not in domains
    assert 'funbox.ru' not in domains
    assert 'stackoverflow.com' not in domains
