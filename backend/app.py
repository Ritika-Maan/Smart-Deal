from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENROUTER_API_KEY")  # Ensure your .env contains this
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

app = Flask(__name__)
CORS(app)

@app.route("/generate_contract", methods=["POST"])
def generate_contract():
    data = request.json
    user_input = data.get("prompt")

    prompt = f"""
The user wants a smart contract for the following situation:

\"{user_input}\"

1. First, explain the contract in simple bullet points.
2. Then write the smart contract in Solidity with inline comments.

Respond in this strict format:

EXPLANATION:
- Explanation 1
- Explanation 2

CONTRACT:
<Put Solidity code here>
"""

    payload = {
        "model": "openai/gpt-3.5-turbo",  # You can change this model if needed
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 1000
    }

    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=HEADERS, json=payload)
        response.raise_for_status()
        reply = response.json()["choices"][0]["message"]["content"]

        # Split explanation and contract
        explanation_part = ""
        contract_part = ""

        if "CONTRACT:" in reply:
            parts = reply.split("CONTRACT:")
            explanation_part = parts[0].replace("EXPLANATION:", "").strip()
            contract_part = parts[1].strip()
        else:
            explanation_part = "Could not extract explanation."
            contract_part = reply.strip()

        return jsonify({
            "explanation": explanation_part,
            "contractCode": contract_part
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
