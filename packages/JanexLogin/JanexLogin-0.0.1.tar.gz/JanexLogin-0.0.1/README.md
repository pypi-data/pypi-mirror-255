* Janex: Login System *

** Overview **

This Janex: Login System library provides a simple framework for developers to create their own login systems in Python applications. It includes functionality for adding accounts, logging in, and basic error handling.

Installation

You can install the library using pip:

```bash

pip install login-system-library```

*Usage*

Import the LoginSession class from the library:

```python

from login_system_library import LoginSession```

Initialize a LoginSession object with the path to the account JSON file:

```python

login_session = LoginSession("accounts.json")```

Use the add_account method to add a new account:

```python

status_code = login_session.add_account("username", "email@example.com", "password123")```

Possible status codes:

    200: New account created successfully.
    405: Username already exists.
    410: Email already exists.

Use the login_account method to log in to an existing account:

```python

    status_code = login_session.login_account("email@example.com", "password123")```

    Possible status codes:
        205: Password is correct.
        415: Incorrect password.

*Contributing*

Contributions are welcome! If you find any bugs or have suggestions for improvements, please open an issue or submit a pull request on GitHub.

*License*

This library is licensed under the Lily License 4.0. See the LICENSE file for details.
