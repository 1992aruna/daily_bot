from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
import os
import requests
from pymongo import MongoClient
from dotenv import load_dotenv
from messages import *
import logging



# Load environment variables
load_dotenv()

  # Replace with your MongoDB URI
# MONGO_DB = 'sbi'  # Replace with your database name
# STAFF_COLLECTION = 'staff'
# ANSWERS_COLLECTION = 'answers'

MONGO_URI = os.getenv("MONGO_URI")
API_URL = os.getenv("API_URL")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

app = Flask(__name__)

app.config["MONGO_URI"] = MONGO_URI
mongo = PyMongo(app)
db = mongo.db.staff
answers_db = mongo.db.answers
# fs = gridfs.GridFS(mongo.db, collection="files")

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

def send_questions_to_contact(contact_number):
    for question in questions:
        send_message(contact_number, question)
       
    
def send_branch_images():
    try:
        
        for staff in db.find({"status": ""}):
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
                        send_message(phone_number, f"Please send the answer with question number like this: 1. Your Answer")
                        print(f"Questions sent for branch {branch} phone number {phone_number}")
                        db.update_one({"_id": staff["_id"]}, {"$set": {"status": "sent"}})


                if not image_found:
                    print(f"No image found for branch {branch}")
            else:
                print("Missing 'branch' or 'phone_number' field in the document.")

        # Close the MongoDB connection
        # client.close()
    except Exception as e:
        print(f"An error occurred: {str(e)}")

def process_message(phone_number, message):
    print(f"Received message: {message} from phone_number: {phone_number}")
    
    question_number = extract_question_number(message)
    print(f"Extracted question number: {question_number}")
    
    # Get the corresponding question
    question = questions[question_number - 1]  # Subtract 1 because list indices start at 0

    # Extract only the response text from the message
    response_text = message.split('.', 1)[1].strip() if '.' in message else message

    # Check if a document for this phone number already exists
    user_responses = mongo.db.user_responses.find_one({'phone_number': phone_number})

    if user_responses:
        # If a document exists, update it with the new response
        mongo.db.user_responses.update_one(
            {'phone_number': phone_number},
            {'$set': {f'question_{question_number}': question, f'answer_{question_number}': response_text}}
        )
        print(f"Updated responses in database for phone number: {phone_number}")
    else:
        # If no document exists, create a new one
        user_responses = {
            'phone_number': phone_number,
            f'question_{question_number}': question,
            f'answer_{question_number}': response_text,
        }
        result = mongo.db.user_responses.insert_one(user_responses)
        print(f"Inserted responses into database, received ID: {result.inserted_id}")

def extract_question_number(message):
    # Split the message into words
    words = message.split()
    
    for word in words:
        # Remove any trailing period
        if word.endswith('.'):
            word = word[:-1]
        
        # Check if the word is a digit
        if word.isdigit():
            return int(word)
    
    return None  # Return None if no question number was found

# @app.route('/receive_message', methods=['POST'])
# def receive_message():
#     # Extract message details from request
#     print(f"Received POST request with JSON: {request.json}")
#     message = request.json.get('text')
#     phone_number = request.json.get('waId')
#     print(f"Received POST request with message: {message} and phone number: {phone_number}")

#     # Process the message and save the response
#     process_message(phone_number, message)

#     return jsonify({'message': 'Message received successfully'}), 200
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
        # Extract message details from request
        print(f"Received POST request with JSON: {request.json}")
        message = request.json.get('text')
        phone_number = request.json.get('waId')

        print(f"Received POST request with message: {message} and phone number: {phone_number}")

        # Process the message and save the response
        process_message(phone_number, message)

        return jsonify({'message': 'Webhook executed successfully'}), 200
    except Exception as e:
        logging.exception("An error occurred: %s", e)
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    send_branch_images()
    app.run(debug=True)
    
# Test your send_order_images function locally
# if __name__ == "__main__":
#     send_branch_images()
