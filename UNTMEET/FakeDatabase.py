from faker import Faker
import json
import mysql.connector

fake = Faker()

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

# Load data from the JSON file for local checking
with open('users.json', 'r') as f:
    data = json.load(f)

# Function to check login credentials
def check_login(username, password):
    for user in data:
        if user['Username'] == username and user['Password'] == password:
            return True
    return False  # Placed outside the loop

# Connect to MySQL (Replace placeholders with your actual credentials)
connection = mysql.connector.connect(
    host='your_host',
    user='your_user',
    password='your_password',
    database='your_database'
)
cursor = connection.cursor()

# Optional: Use connection to interact with the database, e.g., insert user data
# Example to insert users from JSON to MySQL
# for user in users_data:
#     cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", 
#                    (user['Username'], user['Password']))
# connection.commit()
