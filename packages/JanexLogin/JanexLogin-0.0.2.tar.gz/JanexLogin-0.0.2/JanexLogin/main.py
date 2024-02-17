import json
import os

class LoginSession:
    def __init__(self, account_file):
        self.account_file = account_file
        if not os.path.exists(account_file):
            with open(account_file, "w") as new_file:
                json.dump({"accounts": []}, new_file)

    def load_json(self):
        with open(self.account_file, "r") as account_file:
            accounts = json.load(account_file)

        return accounts

    def edit_and_save_json(self, new_data):
        with open(self.account_file, "w") as account_file:
            json.dump(new_data, account_file, indent=4)

    def add_account(self, username, email, password):
        accounts = self.load_json()

        # Check if the username or email already exists
        for account in accounts["accounts"]:
            if username == account.get("username"):
                print("Username exists! Bad register.")
                return 405

            if email == account.get("email"):
                print("Email exists! Bad register.")
                return 410

        # Generate a unique ID for the new account
        new_account_id = len(accounts["accounts"]) + 1

        # Create a new account with ID
        new_account = {
            "id": new_account_id,
            "username": username,
            "email": email,
            "password": password
        }

        accounts["accounts"].append(new_account)

        # Save the updated accounts data
        self.edit_and_save_json(accounts)

        print("New account OK!")
        return 200

    def login_account(self, email, password):
        accounts = self.load_json()

        for account in accounts["accounts"]:
            if email == account.get("email"):
                if password == account.get("password"):
                    print("Password OK!")
                    return 205
                else:
                    print("Incorrect password!")
                    return 415
                    
        print("E-Mail not registered!")
        return 420

if __name__ == "__main__":
    Session = LoginSession("accounts.json")

    type = input("Test registration (1), login (2)")

    if type == "1":

        email = input("Email: ")
        username = input("Username: ")
        password = input("Password: ")

        Session.add_account(username, email, password)

    elif type == "2":

        email = input("Email: ")
        password = input("Password: ")

        Session.login_account(email, password)
