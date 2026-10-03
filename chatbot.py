import mysql.connector
from flask import jsonify, session
import os

try:
    from dotenv import load_dotenv
    load_dotenv(override=True)
except ImportError:
    pass

# Configure Gemini AI gracefully
api_key = os.getenv("GEMINI_API_KEY")
model = None

try:
    import google.generativeai as genai
    print(f"DEBUG: Loaded API Key from env: {api_key}")
    if api_key and api_key != "YOUR_API_KEY_HERE":
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-3-flash-preview') 
        print("DEBUG: Gemini model successfully initialized! (gemini-3-flash-preview)")
    else:
        print("DEBUG: Condition failed! Either no api key or it's YOUR_API_KEY_HERE")
except Exception as e:
    print(f"DEBUG: Failed to initialize Google Generative AI: {e}")

def get_bot_response(user_message, db_config):
    message = user_message.strip()
    username = session.get("user", "Guest")

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        # FETCH ALL EVENTS AS CONTEXT
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
        
        # FETCH ALL COMPETITIONS
        cursor.execute("SELECT name, type, description, competition_date, venue FROM competitions")
        competitions = cursor.fetchall()

        # FETCH ALL TECH FESTS
        cursor.execute("SELECT name, department, description, fest_date, venue FROM tech_fests")
        tech_fests = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        # If API KEY is missing, fallback to a simple manual response so the app doesn't crash
        if model is None:
            return jsonify({
                "response": "⚠️ **System Notice**: The Chatbot is currently in minimal mode because the `GEMINI_API_KEY` is missing in the `.env` file! Please ask the administrator to configure it."
            })

        # BUILD SYSTEM PROMPT CONTEXT
        from datetime import datetime
        today = datetime.now()
        today_date = today.strftime('%Y-%m-%d')

        context_str = f"You are the official AI Assistant for 'Eventopia', a college event portal. Today's Date: {today_date}. You are talking to user: {username}.\n"
        context_str += "Here is the live database of tech fests, competitions, and events (classified as UPCOMING or CONCLUDED based on today's date):\n"
        
        if not events and not competitions and not tech_fests:
            context_str += "Currently, there are no events or competitions recorded in the system.\n"
        else:
            if tech_fests:
                context_str += "--- DEPARTMENT TECH FESTS ---\n"
                for t in tech_fests:
                    status = "[UPCOMING]"
                    try:
                        f_date = datetime.strptime(str(t['fest_date']), '%Y-%m-%d')
                        if f_date.date() < today.date(): status = "[CONCLUDED]"
                    except: pass
                    context_str += f"- {status} {t['name']} (Dept: {t['department']}): {t['description']} | Venue: {t['venue']} | Date: {t['fest_date']}\n"

            if events:
                context_str += "--- EVENTS & SUB-EVENTS ---\n"
                for e in events:
                    status = "[UPCOMING]"
                    try:
                        ev_date = datetime.strptime(str(e['event_date']), '%Y-%m-%d')
                        if ev_date.date() < today.date(): status = "[CONCLUDED]"
                    except: pass
                    
                    price_str = "Free" if e.get('price', 0) == 0 else f"₹{e.get('price', 0)}"
                    sub_cats = f" | Sub-Categories: {e['sub_categories']}" if e['sub_categories'] else ""
                    parent_fest = f" [Part of Tech Fest: {e['tech_fest_name']}]" if e.get('tech_fest_name') else ""
                    context_str += f"- {status} {e['name']}{parent_fest} ({e['category']} / {e['department']}): {e['description']} | Venue: {e['venue']} | Time: {e['event_date']} at {e['event_time']} | Price: {price_str}{sub_cats}\n"
            
            if competitions:
                context_str += "--- COMPETITIONS ---\n"
                for c in competitions:
                    status = "[UPCOMING]"
                    try:
                        c_date = datetime.strptime(str(c['competition_date']), '%Y-%m-%d')
                        if c_date.date() < today.date(): status = "[CONCLUDED]"
                    except: pass
                    context_str += f"- {status} {c['name']} (Type: {c['type']}): {c['description']} | Venue: {c['venue']} | Date: {c['competition_date']}\n"

        context_str += "\nInstructions: Answer the user's question clearly and conversationally. If they ask about events, tech fests, or competitions, reference the provided list. "
        context_str += "If they ask about sub-events, explicitly list the events marked as '[Part of Tech Fest: ...]', or mention the 'Sub-Categories'. "
        context_str += "If they explicitly ask to 'go to home page', 'navigate to home', or 'take me home', do NOT write any conversational text. Instead, respond EXACTLY with: [NAVIGATE_HOME] "
        context_str += "If they ask you to 'create a notification', 'send a notification', or 'announce something' to the notification panel, respond EXACTLY with the format: [CREATE_NOTIFICATION] Title | Message (replace Title and Message with a catchy title and message based on their request). Do not include any other text. "
        context_str += "If they ask a general knowledge question... answer it brilliantly but concisely. "
        context_str += "Always be polite and helpful. format your response in plain text (can use emojis). Do NOT hallucinate events that aren't in the list."

        prompt = f"{context_str}\n\nUser Question: {message}\nAssistant:"

        response = model.generate_content(prompt)
        ai_text = response.text.replace('\n', '<br>')
        
        return jsonify({"response": ai_text})

    except Exception as e:
        print("Chatbot Error:", e)
        return jsonify({
            "response": "Oops! I encountered an error connecting to my neural network. Please try again later."
        })