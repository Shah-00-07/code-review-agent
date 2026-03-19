import os

def Get_Data_From_Database(user_id):
    # Intentional Flaw: Hardcoded Credential & SQL Injection risk
    connection_string = "admin:password123@localhost:5432/nirma_db"
    query = "SELECT * FROM users WHERE id = " + user_id 
    
    # Intentional Flaw: Broad Exception handling
    try:
        print(f"Connecting with {connection_string}")
        # Imagine DB logic here
        return "User Data"
    except:
        pass 

def process_list(my_list):
    # Intentional Flaw: O(n^2) complexity in a simple search
    for i in my_list:
        for j in my_list:
            if i == j:
                print("Match found")

# Triggering watcher