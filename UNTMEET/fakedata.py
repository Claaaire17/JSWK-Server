import json
from faker import Faker

#fake = Faker()

users_data = []

# Generate 100 fake users
for i in range(100):
    user = {
        "Username": fake.user_name(),
        "Password": fake.password()
    }
    users_data.append(user)

# Write the generated user data to a JSON file
with open('users.json', 'w') as fp:
    json.dump(users_data, fp, indent=4)

def main():
    number_of_users = 100 
    print("Database successfully generated")

main()



    