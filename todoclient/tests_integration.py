import asyncio
import random
from todoclient.client import TodoAsyncClient, AuthTodoAsyncClient



def random_credentials():
    number = str(random.randint(0, 1000000))
    return number, f'bot{number}@emailfake.com', '123456'


async def test_integration():
    '''
    Makes a integration test using a real FastAPI Simple Todo server
    '''
    client = TodoAsyncClient()

    number, user, password = random_credentials()

    response = await client.register_user(
        email=user, first_name="Bot", last_name=number, password=password
    )

    auth_client = AuthTodoAsyncClient(user=user, password=password)

    assert (
        await auth_client.read_user()
    ).status_code == 200

    response = await auth_client.add_list(list_name=f"List from {number}")
    assert response.status_code == 200
    list_id = response.data['list_id']

    assert (
        await auth_client.view_list(list_id)
    ).data == []

    assert (
        await auth_client.add_item(list_id, todo_item_name="Item 1")
    ).status_code == 200

    list_response = (await auth_client.view_list(list_id)).data
    assert list_response[0]['todo_item_name'] == 'Item 1'

    item_id = list_response[0]['todo_item_id']

    assert(
        await auth_client.update_item(list_id, item_id, todo_item_name="Updated Item")
    ).status_code == 204

    assert(
        await auth_client.view_list(list_id)
    ).data[0]['todo_item_name'] == 'Updated Item'

    assert(
        await auth_client.delete_item(list_id, item_id)
    ).status_code == 204

    assert(
        await auth_client.view_list(list_id)
    ).data == []

    assert(
        await auth_client.delete_list(list_id)
    ).status_code == 204

    list_response = await auth_client.view_list(list_id)
    assert list_response.status_code == 404
    assert list_response.error_msg == 'List does not exists'



if __name__ == '__main__':
    asyncio.run(test_integration())
