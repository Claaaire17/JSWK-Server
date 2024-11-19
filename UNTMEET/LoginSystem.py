
import json

def check_login(username, password):
    # Open and load the JSON file
    with open('users.json', 'r') as f:
        users_data = json.load(f)  # Load entire file as list of users
    
    # Iterate through each user in the data
    for user in users_data:
        if user['Username'] == username and user['Password'] == password:
            return True  # Match found
    return False  # No match found

# Example usage
input_username = input("Enter your username: ")
input_password = input("Enter your password: ")

if check_login(input_username, input_password):
    print("Login successful!")
else:
    print("Invalid username or password.")
