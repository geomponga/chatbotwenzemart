from flask import Flask, request, jsonify, render_template
from fuzzywuzzy import fuzz
from faq_data import FAQS

app = Flask(__name__)

def find_answer(user_message):
    msg = user_message.lower()
    best_match = None
    best_score = 0
    best_category = None
    best_category_score = 0

    for item in FAQS:

        # 1. Exact keyword match
        for keyword in item["keywords"]:
            if keyword in msg:
                return item["answer"]

        # 2. Keyword count match
        match_count = sum(1 for keyword in item["keywords"] if keyword in msg)
        if match_count >= 2:
            return item["answer"]

        # Track category strength for fallback
        if match_count > best_category_score:
            best_category_score = match_count
            best_category = item

        # 3. Fuzzy matching
        for keyword in item["keywords"]:
            score = fuzz.partial_ratio(keyword, msg)
            if score > best_score:
                best_score = score
                best_match = item

    # 4. Category-based fallback (NEW: even 1 keyword triggers it)
    if best_category_score >= 1:
        return best_category["fallback"]

    # 5. Fuzzy fallback
    if best_score >= 70:
        return best_match["fallback"]

    # 6. Generic fallback
    return "I'm not sure about that. Try asking about shipping, returns, hours, or payments."

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "")

    if not user_message.strip():
        return jsonify({"response": "Please enter a valid question."})

    answer = find_answer(user_message)
    return jsonify({"response": answer})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
