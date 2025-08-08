import random
import json

# List of first names
first_names = [
    "Ananya", "Priya", "Sanya", "Sneha", "Isha", "Aditi", "Riya", "Aisha",
    "Neha", "Pooja", "Swati", "Kavya", "Anjali", "Megha", "Divya", "Lakshmi",
    "Shreya", "Anika", "Radhika", "Tanya", "Mira", "Sonal", "Vidya", "Nidhi",
    "Priti", "Sunita", "Kamala", "Malini", "Tarini", "Charu", "Gauri", "Leena",
    "Nandini", "Bhavana", "Deepa", "Ekta", "Farah", "Geeta", "Harini", "Indira",
    "Jaya", "Kiran", "Lalita", "Manisha", "Nisha", "Ojasvi", "Parvati", "Rekha",
    "Sakshi", "Tanvi"
]

# List of last names
last_names = [
    "Singh", "Kumar", "Sharma", "Patel", "Gupta", "Mehta", "Joshi", "Desai",
    "Reddy", "Chopra", "Malhotra", "Kapoor", "Bhat", "Naidu", "Varma", "Roy",
    "Das", "Nair", "Iyer", "Rao"
]

def generate_username():
    """Generate a username in the format firstname_lastname_randomnumber"""
    # Select random first name and last name
    first_name = random.choice(first_names)
    last_name = random.choice(last_names)
    
    # Generate random number between 01 and 99 (formatted with leading zero if needed)
    random_number = random.randint(1, 99)
    
    # Create username in lowercase with proper formatting
    username = f"{first_name.lower()}_{last_name.lower()}_{random_number:02d}"
    
    return username

def save_username_to_json(username, filename="username.json"):
    """Save the generated username to a JSON file"""
    data = {
        "username": username
    }
    
    with open(filename, 'w') as json_file:
        json.dump(data, json_file, indent=2)
    
    print(f"Username '{username}' saved to {filename}")

def main():
    # Generate username
    username = generate_username()
    
    # Save to JSON file
    save_username_to_json(username)
    
    # Display the generated username
    print(f"Generated username: {username}")

if __name__ == "__main__":
    main()