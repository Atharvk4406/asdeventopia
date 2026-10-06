import mysql.connector
from flask import jsonify, session
import os
import json
import random
from ml_chatbot import predict_intent

try:
    from dotenv import load_dotenv
    load_dotenv(override=True)
except ImportError:
    pass

# Load local intents for ML Fallback
local_intents = {}
try:
    with open("intents.json") as f:
        data = json.load(f)
        for item in data.get("intents", []):
            local_intents[item["tag"]] = item.get("responses", [])
except Exception as err:
    print("Warning: Could not load intents.json for fallback:", err)

# Configure Gemini AI gracefully
api_key = os.getenv("GEMINI_API_KEY")
model = None

if api_key and api_key != "YOUR_API_KEY_HERE":
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        
        # Try standard Gemini models in order of preference
        for model_name in ['gemini-2.5-flash', 'gemini-2.5-pro', 'gemini-flash-latest']:
            try:
                model = genai.GenerativeModel(model_name)
                print(f"DEBUG: Successfully initialized Gemini model: {model_name}")
                break
            except Exception:
                continue
    except Exception as e:
        print(f"DEBUG: Failed to initialize Google Generative AI: {e}")

def get_bot_response(user_message, db_config):
    message = user_message.strip()
    username = session.get("user", "Guest")

    events = []
    competitions = []
    tech_fests = []

    # Fetch DB Context if MySQL is available
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT e.id, e.name, e.description, e.category, e.department, e.event_date, e.event_time, e.venue, e.price,
                   t.name as tech_fest_name,
                   GROUP_CONCAT(c.category_name SEPARATOR ', ') as sub_categories
            FROM events e
            LEFT JOIN event_categories c ON e.id = c.event_id
            LEFT JOIN tech_fests t ON e.tech_fest_id = t.id
            GROUP BY e.id
        """)
        events = cursor.fetchall()
        
        cursor.execute("SELECT name, type, description, competition_date, venue FROM competitions")
        competitions = cursor.fetchall()

        cursor.execute("SELECT name, department, description, fest_date, venue FROM tech_fests")
        tech_fests = cursor.fetchall()
        
        cursor.close()
        conn.close()
    except Exception as db_err:
        print("Database connection notice for chatbot:", db_err)

    # 1. TRY GEMINI GENERATIVE AI
    if model is not None:
        try:
            from datetime import datetime
            today = datetime.now()
            today_date = today.strftime('%Y-%m-%d')

            context_str = f"You are the official AI Assistant for 'Eventopia', a college event portal. Today's Date: {today_date}. User: {username}.\n"
            context_str += "Here is the live database of tech fests, competitions, and events:\n"
            
            if tech_fests:
                context_str += "--- TECH FESTS ---\n"
                for t in tech_fests:
                    context_str += f"- {t.get('name')} ({t.get('department')}): {t.get('description')} | Date: {t.get('fest_date')}\n"

            if events:
                context_str += "--- EVENTS ---\n"
                for e in events:
                    context_str += f"- {e.get('name')} ({e.get('category')}): {e.get('description')} | Venue: {e.get('venue')} | Date: {e.get('event_date')}\n"

            if competitions:
                context_str += "--- COMPETITIONS ---\n"
                for c in competitions:
                    context_str += f"- {c.get('name')}: {c.get('description')} | Date: {c.get('competition_date')}\n"

            context_str += "\nAnswer politely, accurately, and concisely based on the events provided."

            prompt = f"{context_str}\n\nUser: {message}\nAssistant:"
            response = model.generate_content(prompt)
            if response and response.text:
                ai_text = response.text.replace('\n', '<br>')
                return jsonify({"response": ai_text})
        except Exception as ai_err:
            print("Gemini API call failed, falling back to ML Chatbot model:", ai_err)

    # 2. LOCAL ML RANDOMFOREST FALLBACK ENGINE
    try:
        tag, confidence = predict_intent(message)
        print(f"ML Intent prediction: tag='{tag}', confidence={confidence:.2f}")

        responses = local_intents.get(tag, [])
        if responses:
            chosen_response = random.choice(responses)
            if tag == "events_list" and events:
                event_names = ", ".join([e.get('name') for e in events[:5]])
                chosen_response += f"<br>Current Events: <b>{event_names}</b>"
            return jsonify({"response": chosen_response})
    except Exception as ml_err:
        print("ML Fallback error:", ml_err)

    # 3. GENERAL FRIENDLY FALLBACK
    return jsonify({
        "response": "Hello! I am your Eventopia Assistant. You can ask me about available events, registration processes, event fees, and competition schedules!"
    })