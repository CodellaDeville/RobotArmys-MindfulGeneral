import os
from flask import Flask, render_template, request, jsonify
import requests
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

TOGETHER_API_KEY = os.getenv('705bf93d770e9b119cdce97e59ba2e047dffdf058d36b3a292e234e3b0868c')
TOGETHER_API_URL = "https://api.together.xyz/inference"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '')
    
    # Prepare the prompt for the Together API
    prompt = f"""You are MG (Mindful General), an empathetic AI companion designed to support veterans, military personnel, and first responders.
    Your responses should be compassionate, understanding, and focused on mental health and well-being.
    
    User: {user_message}
    MG:"""
    
    # Call Together API
    headers = {
        "Authorization": f"Bearer {TOGETHER_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "mistralai/Mixtral-8x7B-Instruct-v0.1",
        "prompt": prompt,
        "max_tokens": 400,
        "temperature": 0.7,
        "top_p": 0.7,
        "top_k": 50,
        "repetition_penalty": 1.1,
        "stop": ["User:", "\n\n"]
    }
    
    try:
        response = requests.post(TOGETHER_API_URL, json=payload, headers=headers)
        response.raise_for_status()
        
        # Extract the generated text from the response
        bot_response = response.json()['output']['choices'][0]['text'].strip()
        
        return jsonify({"response": bot_response})
        
    except Exception as e:
        print(f"Error calling Together API: {str(e)}")
        return jsonify({"response": "I apologize, but I'm having trouble processing your message right now. Please try again in a moment."}), 500

if __name__ == '__main__':
    app.run(debug=True) 