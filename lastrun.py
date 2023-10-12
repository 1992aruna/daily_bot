from flask import Flask, request, jsonify
import os
import requests
from pymongo import MongoClient
from dotenv import load_dotenv
from messages import *



# Load environment variables
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")  # Replace with your MongoDB URI
MONGO_DB = 'sbi'  # Replace with your database name
STAFF_COLLECTION = 'staff'
ANSWERS_COLLECTION = 'answers'


API_URL = os.getenv("API_URL")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

app = Flask(__name__)

# Initialize Wati API endpoint
WATI_API_ENDPOINT = f"{API_URL}/api/v1/sendSessionMessage"



# Function to send image message
def send_image_message(phone_number,image, caption):
    url = f"{API_URL}/api/v1/sendSessionFile/{phone_number}?caption={caption}"

    payload = {}
    files=[
    ('file',('file',open(image,'rb'),'image/jpeg'))
    ]
    headers = {
    'Authorization': ACCESS_TOKEN
    }

    response = requests.post(url, headers=headers, json=payload, files=files)
    print(response)
    print(response.json())

# Function to send the 10 questions
def send_questions_to_contact(contact_number):
    questions = [
        "1. What is your favorite color?",
        "2. What is your role in the company?",
        "3. How satisfied are you with your current position?",
        "4. Are there any challenges you face in your work?",
        "5. What improvements would you suggest for our branch?",
        "6. Do you have any feedback on our recent projects?",
        "7. What are your career goals within the company?",
        "8. How can we provide better support for your role?",
        "9. Do you have any suggestions for team-building activities?",
        "10. How can we improve communication within the team?"
    ]

    for question in questions:
        send_message(contact_number, question)

        # Wait for and capture the user's response (you need to implement this part)
        user_response = "User's response goes here"

        # Save the user's response to the answers collection
        save_user_response(contact_number, question, user_response)

def save_user_response(contact_number, question, response):
    client = MongoClient(MONGO_URI)
    db = client[MONGO_DB]
    answers_collection = db[ANSWERS_COLLECTION]
    # Save the response to the answers collection
    answers_collection.insert_one({
        "contact_number": contact_number,
        "question": question,
        "response": response
    })



def send_branch_images():
    try:
        # Connect to MongoDB
        client = MongoClient(MONGO_URI)
        db = client[MONGO_DB]
        staff_collection = db[STAFF_COLLECTION]

        # Iterate over the orders
        for staff in staff_collection.find({"status": ""}):
            # Check if 'branch' and 'phone_number' fields exist in the document
            if 'branch' in staff and 'phone_number' in staff:
                branch = staff['branch']
                phone_number = staff['phone_number']

                # Check if an image exists for this branch with either .png or .jpg extension
                image_extensions = ['.png', '.jpg']
                image_found = False

                for ext in image_extensions:
                    image_path = f'D:\\New Project\\Python\\New_Bot\\Bot\\design_bot\\branch_images\\{branch}{ext}'

                    if os.path.isfile(image_path):
                        image_found = True
                        print("Image exists. Sending to", phone_number)
                        # Provide a caption for the image message
                        caption = f'Here is your image for branch {branch}'
                        send_image_message(phone_number, image_path, caption)
                        print(f"Image sent for branch {branch} with extension {ext}")
                        send_questions_to_contact(phone_number)
                        print(f"Questions sent for branch {branch} phone number {phone_number}")
                        staff_collection.update_one({"_id": staff["_id"]}, {"$set": {"status": "sent"}})


                if not image_found:
                    print(f"No image found for branch {branch}")
            else:
                print("Missing 'branch' or 'phone_number' field in the document.")

        # Close the MongoDB connection
        client.close()
    except Exception as e:
        print(f"An error occurred: {str(e)}")

allowed_extensions=["png", "jpg", "jpeg"]


@app.route('/')
def home():
  return "Ink Pen Bot Live 1.0"

@app.route("/webhook", methods=['GET'])
def connetwebhook():
    return "running whatsapp webhook"

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        # Trigger the send_order_images function when a POST request is received at /webhook
        send_branch_images()
        return jsonify({'message': 'Webhook executed successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    send_branch_images()
    app.run(debug=True)
    
# Test your send_order_images function locally
# if __name__ == "__main__":
#     send_branch_images()
