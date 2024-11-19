from flask import Flask, request, render_template, redirect, url_for
import json

app = Flask(__name__)

# Load user data from JSON file
with open('users.json', 'r') as f:
    users_data = json.load(f)


# Add new users to the JSON File
def add_user(username, password):
    new_user = {"Username": username, "Password": password}
    users_data = load_users()
    
    # Appends the information
    users_data.append(new_user)
    
    # Updated data written into the JSON file
    with open('users.json', 'w') as f:
        json.dump(users_data, f, indent=4)
    
# Function to check credentials
def check_login(username, password):
    for user in users_data:
        if user['Username'] == username and user['Password'] == password:
            return True
    return False

# Route to display the sign-up page 
@app.route('/signup', methods=['GET'])
def signup_page():
    return render_template('SignUpPage.html')

# Route to handle sign-up form submission
@app.route('/signup', methods=['POST'])
def signup():
    username = request.form['euid']
    password = request.form['password']
    confirm_password = request.form['confirmPassword']
    
    #Checks if the passwords match
    if password != confirm_password:
        return "Passwords do not match."
    
    # Check if user already exists
    users_data = load_users()
    for user in users_data:
        if user['Username'] == username:
            return "User already exists!"

    # Add the new user
    add_user(username, password)
    return "Sign-Up successful! You can now log in."

    add_user(username, password)
    return redirect(url_for('profile_setup'))

# Route to display the profile setup page 
@app.route('/profilesetup', methods=['GET'])
def profile_setup():
    return render_template('ProfileSetUp.html')

if __name__ == '__main__':
    app.run(debug=True)


# Route to display the login page
@app.route('/')
def login_page():
    return render_template('LoginPage.html')  # Make sure LoginPage.html is in a folder named `templates`

# Route to handle login form submission
@app.route('/login', methods=['POST'])
def login():
    username = request.form['Username']
    password = request.form['Password']

    if check_login(username, password):
        return "Login successful!"
    else:
        return "Invalid username or password."

if __name__ == '__main__':
    app.run(debug=True)
