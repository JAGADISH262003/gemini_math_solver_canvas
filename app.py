from flask import Flask, request, jsonify, send_from_directory
import google.generativeai as genai
from PIL import Image
import io
import os
import time
import threading
from datetime import datetime, timedelta

app = Flask(__name__)

# Configure Gemini API
API_KEY = "your gemini api key"
if not API_KEY:
    raise ValueError("GOOGLE_API_KEY environment variable not set.")
genai.configure(api_key=API_KEY)

# Gemini Model Configuration
generation_config = {
    "temperature": 1.0,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name="gemini-2.0-flash-exp", generation_config=generation_config
)

def generate_content(prompt, image_bytes):
    """Sends the prompt and image bytes to Gemini synchronously."""
    try:
        # Directly create PIL Image from Bytes
        img = Image.open(io.BytesIO(image_bytes))
        response = model.generate_content([prompt, img])
        return response.text
    except Exception as e:
        print(f"Error in Gemini interaction: {e}")
        raise


#this part of the code is for debuging. It will create a directory for the images and delete the images that are older than 10 seconds
# def create_image_directory():
#     """Creates the images directory if it does not exist"""
#     images_dir = os.path.join(os.path.dirname(__file__), 'images')
#     if not os.path.exists(images_dir):
#         os.makedirs(images_dir)
#     return images_dir

# def delete_old_images(images_dir):
#     """Deletes images that are older than 10 minutes"""
#     while True:
#         time.sleep(10) # Check every 10 seconds
#         now = datetime.now()
#         for filename in os.listdir(images_dir):
#             filepath = os.path.join(images_dir, filename)
#             if os.path.isfile(filepath):
#                 file_creation_time = datetime.fromtimestamp(os.path.getctime(filepath))
#                 if now - file_creation_time > timedelta(minutes=10):
#                     try:
#                         os.remove(filepath)
#                         print(f"Deleted old image: {filename}")
#                     except Exception as e:
#                         print(f"Error deleting file '{filename}': {e}")

# images_dir = create_image_directory()
# # Start the deletion thread
# delete_thread = threading.Thread(target=delete_old_images, args=(images_dir,), daemon=True)
# delete_thread.start()


@app.route("/")
def index():
    return send_from_directory('.', 'index.html')


@app.route("/solve", methods=["POST"])
def solve_equation():
    if "image" not in request.files:
        return jsonify({"error": "No image file uploaded"}), 400

    try:
         image_file = request.files["image"]
         image_bytes = image_file.read()
        #  # Save the image
        #  images_dir = os.path.join(os.path.dirname(__file__), 'images')
        #  timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
        #  filename = f"image_{timestamp}.png"
        #  image_path = os.path.join(images_dir, filename)
        #  with open(image_path, 'wb') as f:
        #      f.write(image_bytes)
        #  print(f"Saved image at: {image_path}")

         prompt = "Answer this math problem:"
         gemini_response = generate_content(prompt, image_bytes)

         if not gemini_response:
            return jsonify({"error": "No response from Gemini API"}), 500

         return jsonify({"response": gemini_response})

    except Exception as e:
        print(f"Error processing image: {e}")
        return jsonify({"error": f"Error processing image: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True)