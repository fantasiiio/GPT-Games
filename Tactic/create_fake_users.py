import json
from faker import Faker

# Initialize faker
fake = Faker()

# Create a list to store user data
user_list = []

# Generate 5 sets of email, username, and password
for _ in range(20):
    user_data = {}
    user_data["email"] = fake.email()
    user_data["username"] = fake.user_name()
    user_data["password"] = fake.password(length=12, special_chars=True, digits=True, upper_case=True, lower_case=True)
    user_list.append(user_data)

# Write the user data to a JSON file
with open("data\\fake_users.json", "w") as f:
    json.dump(user_list, f, indent=4)

print("User data has been written to users.json")
