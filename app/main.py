from flask import Flask, render_template, request, jsonify
import json
import os
from difflib import get_close_matches
from together import Together
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__, template_folder="templates", static_folder="static")
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default-secret-key')

# Initialize Together AI client with API key
Together.api_key = "bc705bf93d770e9b119cdce97e59ba2e047dffdf058d36b3a292e234e3b0868c"
together_client = Together()

# Define the correct file path
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
KNOWLEDGE_BASE_FILE = os.path.join(BASE_DIR, "..", "knowledge_base.json")

# Load knowledge base
def load_knowledge_base():
    try:
        with open(KNOWLEDGE_BASE_FILE, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"questions": [], "mood_responses": {}}

# Save knowledge base
def save_knowledge_base(data):
    with open(KNOWLEDGE_BASE_FILE, "w") as file:
        json.dump(data, file, indent=2)

knowledge_base = load_knowledge_base()

# Mood-based responses
MOOD_RESPONSES = {
    "great": [
        "That's wonderful to hear! What's making your day so great?",
        "I'm so happy for you! Would you like to share what's bringing you joy?",
        "Fantastic! Let's keep that positive energy flowing!"
    ],
    "good": [
        "I'm glad you're feeling good! What's contributing to your positive mood?",
        "That's great to hear! Would you like to talk about what's going well?",
        "Wonderful! Let's focus on maintaining this positive state."
    ],
    "okay": [
        "Sometimes okay is perfectly fine. Would you like to talk about anything?",
        "I'm here if you want to explore ways to lift your mood a bit.",
        "What could help make your day a little better?"
    ],
    "bad": [
        "I'm sorry you're not feeling your best. Would you like to talk about what's bothering you?",
        "Remember, it's okay to not be okay. How can I support you right now?",
        "Let's work through this together. What's on your mind?"
    ],
    "terrible": [
        "I'm here for you during this difficult time. Would you like to share what's troubling you?",
        "You're not alone in this. How can I help support you right now?",
        "Let's take this one step at a time. What's the biggest thing weighing on you?"
    ]
}

# Find best match for user question
def find_best_match(user_question, questions):
    matches = get_close_matches(user_question, questions, n=1, cutoff=0.6)
    return matches[0] if matches else None

# Get answer from knowledge base
def get_answer_for_question(question):
    for q in knowledge_base["questions"]:
        if q["question"].lower() == question.lower():
            return q["answer"]
    return None

# Generate contextual response
# Store conversation history
conversation_history = []
max_history_length = 5

def analyze_sentiment(message):
    # Simple sentiment analysis based on keywords
    positive_words = set(['happy', 'great', 'good', 'wonderful', 'love', 'excited', 'joy'])
    negative_words = set(['sad', 'bad', 'terrible', 'hate', 'angry', 'upset', 'worried'])
    
    words = message.lower().split()
    pos_count = sum(1 for word in words if word in positive_words)
    neg_count = sum(1 for word in words if word in negative_words)
    
    if pos_count > neg_count:
        return 'positive'
    elif neg_count > pos_count:
        return 'negative'
    return 'neutral'

def get_contextual_response(user_message, previous_messages):
    # Generate contextual responses based on conversation history
    if len(previous_messages) >= 2:
        last_bot_message = previous_messages[-1][1]
        last_user_message = previous_messages[-2][0]
        
        # Check if user is elaborating on previous topic
        if any(word in user_message.lower() for word in ['because', 'since', 'as', 'why']):
            return f"I understand that's affecting you. How long have you been feeling this way?"
        
        # Check if user is expressing agreement
        if any(word in user_message.lower() for word in ['yes', 'yeah', 'right', 'true']):
            return "I'm glad we're on the same page. Would you like to explore this further?"
        
        # Check if user is expressing disagreement
        if any(word in user_message.lower() for word in ['no', 'nope', 'not', 'disagree']):
            return "I appreciate you sharing a different perspective. Could you tell me more about your view?"
    
    return None

def generate_response(user_message, mood=None):
    global conversation_history
    
    # Add user message to history
    conversation_history.append((user_message, None))
    if len(conversation_history) > max_history_length * 2:
        conversation_history = conversation_history[-max_history_length * 2:]
    
    try:
        # Format conversation history for context
        chat_history = []
        for user_msg, bot_msg in conversation_history[-3:]:
            if bot_msg:
                chat_history.extend([
                    {"role": "user", "content": user_msg},
                    {"role": "assistant", "content": bot_msg}
                ])

        # Check for mood-specific responses first
        if mood and mood.lower() in MOOD_RESPONSES:
            import random
            response = random.choice(MOOD_RESPONSES[mood.lower()])
            conversation_history[-1] = (user_message, response)
            return response
    
        # Generate response using LLM
        sentiment = analyze_sentiment(user_message)
        system_prompt = """You are the Mindful General, an empathetic AI assistant focused on emotional support and mental well-being. 
        Your responses should be:
        1. Compassionate and understanding
        2. Non-judgmental and supportive
        3. Encouraging but realistic
        4. Professional while maintaining warmth
        5. Focused on the user's emotional state and needs
        
        If they express negative emotions, offer gentle understanding and support. If positive, celebrate with them while encouraging continued growth."""

        try:
            response = together_client.chat.completions.create(
                model="meta-llama/Llama-3.3-70B-Instruct-Turbo",
                messages=[
                    {"role": "system", "content": system_prompt}
                ] + chat_history + [
                    {"role": "user", "content": user_message}
                ],
                max_tokens=500,
                temperature=0.7,
                top_p=0.9,
                top_k=50,
                repetition_penalty=1.1
            )
            
            if hasattr(response, 'choices') and response.choices:
                llm_response = response.choices[0].message.content
                conversation_history[-1] = (user_message, llm_response)
                return llm_response
        except Exception as e:
            print(f"Error in LLM response generation: {str(e)}")
            
        # Fallback responses if LLM fails
        if any(greeting in user_message.lower() for greeting in ["hi", "hello", "hey"]):
            response = "Hello! How can I support you today? Feel free to share whatever is on your mind."
        elif "thank" in user_message.lower():
            response = "You're welcome! I'm here to help and support you on your journey."
        elif "bye" in user_message.lower():
            response = "Take care! Remember, I'm here whenever you need support, and every conversation is a step forward."
        else:
            if sentiment == 'positive':
                response = "I sense positivity in your words. Would you like to explore what's bringing you joy?"
            elif sentiment == 'negative':
                response = "I can hear that this is challenging for you. Would you like to talk more about what's troubling you?"
            else:
                response = "I'm here to listen and support you. Would you like to tell me more about what's on your mind?"
        
        conversation_history[-1] = (user_message, response)
        return response
            
    except Exception as e:
        print(f"Error in response generation: {str(e)}")
        return "I'm here to support you. Could you please share more about what's on your mind?"

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_message = data.get("message")
    mood = data.get("mood")
    
    if not user_message:
        return jsonify({"response": "Please share your thoughts with me."})

    response = generate_response(user_message, mood)
    return jsonify({"response": response})

if __name__ == "__main__":
    # Production settings
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

