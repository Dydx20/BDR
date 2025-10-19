from flask import Flask, render_template, request, jsonify
import mysql.connector
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import os
from openai import OpenAI
import random

import whisper
from flask import request

model = whisper.load_model("base")

app = Flask(__name__)


client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


system_prompt = """
You are ScamDetectAI.
Your behavior has two modes:

1. Scam/Manipulation Detection Mode
   - ALWAYS first check if the user message contains scam, phishing, fraud, or psychological manipulation tactics.  
   - If detected → respond with:
     - Risk level (Safe, Moderate Risk, Suspicious).
     - A short explanation.
     - Categories (choose from the provided list).  

2. Chat Mode  
   - If the message does NOT contain scam/manipulation, respond as a helpful, friendly, and chatty assistant.  
   - You can greet, answer small talk, and help with general questions.  

Categories to detect (if relevant):  
Scam/Phishing, Urgency/Scarcity, Authority Pressure, Guilt/Obligation, Gaslighting, Scarcity/FOMO, Social proof/Consensus, Reciprocity, Commitment & consistency, Liking/Similarity, Urgency/Fear appeals, Flattery/Ingratiation, Mirroring/Familiarity & trust, Anchoring/Framing, Spearphishing/Whaling, Smishing, Quishing, Business Email Compromise (BEC)/CEO fraud, Pretexting (fake role/story), Quid pro quo ("service for info"), Baiting, Romance/Confidence scam, Tech-support scam, Safe.  

Rules:  
- If unrelated to scam AND not harmful, just chat normally. Example:  
  - User: "hihi" → "Hi there! 👋 How can I help you today?"  
  - User: "How’s the weather?" → "I can’t give weather updates, but happy to chat!"  
- Always remain friendly while prioritizing scam detection.
"""



try:
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="520120Dy@",
        database="htt_db"
    )
    cursor = conn.cursor()
    print("MySQL connected successfully!")
except mysql.connector.Error as err:
    print(f"MySQL connection failed: {err}")


# model
model_v1 = AutoModelForSequenceClassification.from_pretrained("./best_model")
tokenizer = AutoTokenizer.from_pretrained("./best_model")
model_v1.eval()

model_v2 = AutoModelForSequenceClassification.from_pretrained("./best_model_v2")
tokenizer_v2 = AutoTokenizer.from_pretrained("./best_model_v2")
model_v2.eval()

def predict_with_v1(message):

    high_risk_keywords = [
        "ssn", "dob", "password", "bank account", "credit card",
        "claim now", "urgent", "transfer", "wire", "crypto", "scan qr"
    ]
    message_lower = message.lower()

    if any(keyword in message_lower for keyword in high_risk_keywords):
        risk = 5
        label = "Suspicious"
        color = "red"
        return label, risk, color

    inputs = tokenizer(message, return_tensors="pt", truncation=True, padding=True, max_length=128)
    with torch.no_grad():
        outputs = model_v1(**inputs)
        probs = torch.softmax(outputs.logits, dim=1)
        spam_prob = probs[0][1].item()
        adjusted_prob = min(1.0, spam_prob * 1.5)
        if adjusted_prob < 0.1:
            risk = 1
        elif adjusted_prob < 0.3:
            risk = 2
        elif adjusted_prob < 0.5:
            risk = 3
        elif adjusted_prob < 0.7:
            risk = 4
        else:
            risk = 5
        
        if risk <= 2:
            label = "Safe"
            color = "green"
        elif risk <= 4:
            label = "Moderate Risk"
            color = "orange"
        else:
            label = "Suspicious"
            color = "red"

    return label, risk, color

def predict_with_v2(message):
    """Multi-class model → predicts directly risk 1–5"""
    inputs = tokenizer_v2(message, return_tensors="pt", truncation=True, padding=True, max_length=128)
    with torch.no_grad():
        outputs = model_v2(**inputs)
        preds = torch.argmax(outputs.logits, dim=1).item()

    # v2 labels are 0–4 → shift to 1–5
    risk = preds + 1

    if risk <= 2:
        return "Safe", risk, "green"
    elif risk <= 4:
        return "Moderate Risk", risk, "orange"
    else:
        return "Suspicious", risk, "red"

def predict_spam(message):
    label1, risk1, color1 = predict_with_v1(message)
    label2, risk2, color2 = predict_with_v2(message)

    # Take the higher risk as final decision
    final_risk = max(risk1, risk2)
    if final_risk <= 2:
        final_label, final_color = "Safe", "green"
    elif final_risk <= 4:
        final_label, final_color = "Moderate Risk", "orange"
    else:
        final_label, final_color = "Suspicious", "red"

    return {
        "v1": {"risk": risk1, "label": label1, "color": color1},
        "v2": {"risk": risk2, "label": label2, "color": color2},
        "final": {"risk": final_risk, "label": final_label, "color": final_color}
    }

#page
@app.route('/')
def home():
    return render_template('index.html')

@app.route("/menu")
def menu():
    return render_template('menu.html') 
@app.route("/call2")
def call2():
    return render_template('call2.html') 

@app.route("/call")
def call():
    return render_template('call.html') 

@app.route('/analyze_call', methods=['POST'])
def analyze_call():
    data = request.get_json()
    transcript = data.get("transcript", "")
    
    # Very simple fake detection logic for now
    scam_keywords = ["bank", "lottery", "customs", "pay", "account"]
    is_scam = any(word in transcript.lower() for word in scam_keywords)
    
    if is_scam:
        result = "Warning: This call is likely a scam!"
    else:
        result = "This call seems safe."
    
    return jsonify({"result": result})


@app.route("/AIChatbot", methods=["GET", "POST"])
def AIChatbot():
    if request.method == "POST":
        data = request.get_json()
        if not data or "message" not in data:
            return jsonify({"risk": "0/5", "reason": "No message provided"})

        message = data["message"]
        result = predict_spam(message)

        return jsonify({
            "risk": f"{result['final']['risk']}/5",
            "reason": result['final']['label'],
            "color": result['final']['color'],
            "details": {
                "best_model": f"{result['v1']['risk']}/5 ({result['v1']['label']})",
                "best_model_v2": f"{result['v2']['risk']}/5 ({result['v2']['label']})"
            }
        })

    # GET request → return chatbot page
    return render_template("AIChatbot.html")

@app.route("/InteractiveChatbot", methods=["POST"])
def interactive_chatbot():
    data = request.get_json()
    conversation = data.get("conversation", [])

    messages = [{"role": "system", "content": system_prompt}] + conversation

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # free/cheap
            messages=messages
        )
        reply = response.choices[0].message.content

        if not reply:
            reply="Sorry, I couldn't generate a proper response."

        return jsonify({"reply": reply})
    except Exception as e:
        return jsonify({"error": str(e)})



@app.route("/feedback", methods=["POST"])
def feedback():
    data = request.get_json()
    message = data.get("message")
    correct_label = data.get("correct_label")  # e.g., "Safe"

    try:
        cursor.execute(
            "INSERT INTO feedback (message, correct_label) VALUES (%s, %s)",
            (message, correct_label)
        )
        conn.commit()
        return jsonify({"status": "success"})
    except Exception as e:
        print("Feedback error:", e)
        return jsonify({"status": "error", "message": str(e)})

@app.route("/checkNumber", methods=['GET','POST'])
def checkNumber():
    if request.method == 'POST':
        contact = request.form['contact']

        sql = "SELECT * FROM reports WHERE contact = %s"
        cursor.execute(sql, (contact,))
        report = cursor.fetchone()

        if report:
            message = f"⚠️ This contact has been reported: {report[1]}"
        else:
            message = "✅ This contact is not reported."

        return jsonify({"message": message})

    return render_template('checkNumber.html')

@app.route("/HantarTipu", methods = ['GET', 'POST'])
def HantarTipu():
    if request.method == 'POST':
        description = request.form['description']
        contact = request.form['contact']
        category = request.form['category']

        sql = "INSERT INTO reports (description, contact, category) VALUES (%s, %s, %s)"
        cursor.execute(sql, (description, contact, category))
        conn.commit()
        return jsonify({"message": "✅ Report sent to PDRM CCID!"})

    return render_template('HantarTipu.html') 


# minigame (text)
with open("questions.txt", "r", encoding="utf-8") as f:
    questions = [line.strip() for line in f.readlines() if line.strip()]

@app.route("/minigame")
def minigame():
    question = random.choice(questions) 
    return render_template("minigame.html", question=question)

@app.route("/save_text_answer", methods=["POST"])
def save_text_answer():
    question = request.form["question"]
    user_answer = request.form["answer"]

    cursor.execute("INSERT INTO text_questions (question, user_answer) VALUES (%s, %s)",
                   (question, user_answer))
    conn.commit()

    return jsonify({"message": "Answer saved successfully!"})


if __name__ == "__main__":
    app.run(debug=True, port = 8000)
