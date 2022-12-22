import pickle

class UserSystem:
    def __init__(self):
        self.users = {}
        try:
            self.load()
        except:
            pass

    def add_user(self, username, password, role):
        if username in self.users:
            print(f"Error: User {username} already exists.")
            return
        self.users[username] = User(username, password, role)
        print(f"User {username} added successfully.")

    def delete_user(self, username):
        if username not in self.users:
            print(f"Error: User {username} does not exist.")
            return
        del self.users[username]
        print(f"User {username} deleted successfully.")

    def update_user(self, username, password, role):
        if username not in self.users:
            print(f"Error: User {username} does not exist.")
            return
        self.users[username].password = password
        self.users[username].role = role
        print(f"User {username} updated successfully.")

    def login(self, username, password):
        if username not in self.users:
            print(f"Error: User {username} does not exist.")
            return False
        user = self.users[username]
        if user.password != password:
            print("Error: Incorrect password.")
            return False
        print(f"User {username} logged in successfully.")
        return True

    def save(self, filename="users.pkl"):
        with open(filename, "wb") as f:
            pickle.dump(self.users, f)

    def load(self, filename="users.pkl"):
        with open(filename, "rb") as f:
            self.users = pickle.load(f)

    def addwin(self, username):
        if username in self.users:
            self.users[username].win += 1

    def addloss(self, username):
        if username in self.users:
            self.users[username].loss += 1

class User:
    def __init__(self, username, password, role):
        self.username = username
        self.password = password
        self.role = role
        self.win = 0
        self.loss = 0