# aiohttp-todo-client
A https://github.com/ricardodani/fastapi-simple-todo client written in Python 3 and aiohttp library

# Development instructions

- Install development packages with poetry using:

```
poetry install --dev
```

# Testing


Integration tests, please run FastAPI-Simple-Todo first at port 8000, then:

```
pytest todoclient/tests_integration.py
```


To unit tests, with a mocked server:

```
pytest todoclient/tests_unit.py
```

# Usage

```
>>> from todoclient.client import TodoAsyncClient
>>> client = TodoAsyncClient(base_url=optional_url)
>>> await client.register_user(first_name="User", last_name="Name", email="email@email.com", password="123")
>>> auth_client = AuthTodoClient(base_url=optional_url, user="email@email.com", password="123")
>>> response = await auth_client.add_list(list_name="My List")
```
