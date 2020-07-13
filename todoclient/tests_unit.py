import pytest
import aiohttp
import asyncio
from todoclient.client import TodoAsyncClient, AuthTodoAsyncClient

# Mocked Server API

routes = aiohttp.web.RouteTableDef()
user_input = {
    'first_name': 'First Name',
    'last_name': 'Last Name',
    'password': '123456',
    'email': 'email@email.com'
}
list_input = {"list_name": "List A"}
item_input = {"todo_item_name": "Item 1"}


@routes.post('/register')
async def mocked_register(request):
    return aiohttp.web.json_response(status=204)


@routes.get('/__user__')
async def mocked_read_current_user(request):
    return aiohttp.web.json_response(user_input, status=200)


@routes.post('/list')
async def mocked_create_list(request):
    return aiohttp.web.json_response(list_input, status=200)


@routes.get('/list/1')
async def mocked_view_list(request):
    return aiohttp.web.json_response([list_input], status=200)


@routes.post('/list/1')
async def mocked_add_item(request):
    return aiohttp.web.json_response(item_input, status=200)


@routes.put('/list/1/2')
async def mocked_update_item(request):
    return aiohttp.web.json_response(item_input, status=200)


@routes.delete('/list/1/2')
async def mocked_delete_item(request):
    return aiohttp.web.json_response(status=204)


@pytest.fixture
def mocked_server(loop, test_server):
    app = aiohttp.web.Application()
    app.add_routes(routes)
    server = loop.run_until_complete(test_server(app))
    server.url = f'http://localhost:{server.port}'
    return server


# Client tests

async def _register_user_test(client):
    user = await client.register_user(**user_input)
    assert user.status_code == 204
    assert user.method == 'post'


async def _get_user_test(auth_client):
    user = await auth_client.read_user()
    assert user.status_code == 200
    assert user.method == 'get'
    assert user.data == user_input


async def _post_list_test(auth_client):
    user = await auth_client.add_list(**list_input)
    assert user.status_code == 200
    assert user.method == 'post'


async def _get_list_test(auth_client):
    user = await auth_client.view_list(list_id=1)
    assert user.status_code == 200
    assert user.method == 'get'
    assert user.data == [list_input]


async def _post_item_test(auth_client):
    user = await auth_client.add_item(list_id=1, **item_input)
    assert user.status_code == 200
    assert user.method == 'post'


async def _put_item_test(auth_client):
    user = await auth_client.update_item(list_id=1, item_id=2, **item_input)
    assert user.status_code == 200
    assert user.method == 'put'


async def _delete_item_test(auth_client):
    user = await auth_client.delete_item(list_id=1, item_id=2)
    assert user.status_code == 204
    assert user.method == 'delete'



async def test_unit_tests(mocked_server):
    '''
    All unit tests
    '''
    client = TodoAsyncClient(base_url=mocked_server.url)
    auth_client = AuthTodoAsyncClient(base_url=mocked_server.url, user='user', password='password')

    await _register_user_test(client)
    await _get_user_test(auth_client)
    await _post_list_test(auth_client)
    await _get_list_test(auth_client)
    await _post_item_test(auth_client)
    await _put_item_test(auth_client)
    await _delete_item_test(auth_client)