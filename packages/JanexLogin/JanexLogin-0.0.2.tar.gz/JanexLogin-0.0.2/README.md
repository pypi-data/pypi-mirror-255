<h1> Janex Login System </h1>

<h2> Overview </h2>

This Janex: Login System library provides a simple framework for developers to create their own login systems in Python applications. It includes functionality for adding accounts, logging in, and basic error handling.

<h2> Installation </h2>

You can install the library using pip:

```bash

pip install JanexLogin
```

<h2> Usage </h2>

Import the LoginSession class from the library:

```python

from JanexLogin import LoginSession
```

Initialize a LoginSession object with the path to the account JSON file:

```python

login_session = LoginSession("accounts.json")
```

Use the add_account method to add a new account:

```python

status_code = login_session.add_account("username", "email@example.com", "password123")
```

Possible status codes:

    200: New account created successfully.
    405: Username already exists.
    410: Email already exists.

Use the login_account method to log in to an existing account:

```python
status_code = login_session.login_account("email@example.com", "password123")
```

    Possible status codes:
        205: Password is correct.
        415: Incorrect password.

<h2>Contributing</h2>

Contributions are welcome! If you find any bugs or have suggestions for improvements, please open an issue or submit a pull request on GitHub.

<h2>License</h2>

This library is licensed under the Lily License 4.0. See the LICENSE file for details.
