from pymongo import MongoClient
from decouple import config

MONGO_URL = config('MONGODB_URL')

def fetch_document_by_email(email):
    # Connect to the MongoDB server running on localhost:27017
    client = MongoClient(MONGO_URL, 27017)
    
    # Connect to the 'stress-ai-mongo' collection in the 'user-auth' database 
    collection = client['stress-ai-mongo']['user-auth']

    # Retrieve the document with the specified email address
    document = collection.find_one({"email": email})

    # Close the connection to MongoDB
    client.close()

    # return the retrieved document
    if document:
        return {
            "success": True,
            "document": document
        }
    else:
        return {
            "success": False,
            "message": "No document found with email: " + email
        }



def insert_document(email, name, password, models):
    # Connect to the MongoDB server running on localhost:27017
    client = MongoClient(MONGO_URL, 27017)
    
    # Connect to the 'stress-ai-mongo' collection in the 'user-auth' database 
    collection = client['stress-ai-mongo']['user-auth']

    # Retrieve the document with the specified email address
    document = collection.find_one({"email": email})
    if document:
        return {
            "success": False,
            "message": "Found existing user with email: " + email
        }

    # Create a document with the specified attributes
    document = {
        "email": email,
        "name": name,
        "password": password,
        "models": models
    }

    # Insert the document into the collection
    result = collection.insert_one(document)

    # Close the connection to MongoDB
    client.close()

    # Return the ID of the inserted document
    return {
        "success": True,
        "message": "Sucessfully created user account with: " + email
        # " ID: " + str(result.inserted_id)
    }



def update_document_by_email(email, new_name, new_password, new_models):
    # Connect to the MongoDB server running on localhost:27017
    client = MongoClient(MONGO_URL, 27017)
    
    # Connect to the 'stress-ai-mongo' collection in the 'user-auth' database 
    collection = client['stress-ai-mongo']['user-auth']

    # Prepare the update document
    update_fields = {}
    if new_name:
        update_fields["name"] = new_name
    if new_password:
        update_fields["password"] = new_password
    if new_models:
        update_fields["models"] = str(new_models)

    # Update the document with the specified email address
    result = collection.update_one({"email": email}, {"$set": update_fields})

    # Close the connection to MongoDB
    client.close()

    if 0 < result.modified_count < 2:
        return {
            "success": True,
            "message": "sucessfully updated user account: " + email
        }
    else: 
        return {
            "success": False,
            "message": "Failed to update user account: " + email
        }
