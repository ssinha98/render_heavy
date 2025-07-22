from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# --- CORS CONFIGURATION (copied from your main app) ---
CORS(app, 
     resources={r"/*": {
         "origins": ["http://localhost:3000", "https://notebook-mvp.vercel.app"],
         "methods": ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
         "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"],
         "expose_headers": ["Content-Type", "Content-Disposition"],
         "supports_credentials": True,
         "max_age": 86400
     }})

def add_cors_headers(response):
    """Helper function to add CORS headers to any response"""
    origin = request.headers.get('Origin')
    if origin in ["http://localhost:3000", "https://notebook-mvp.vercel.app"]:
        response.headers['Access-Control-Allow-Origin'] = origin
    else:
        response.headers['Access-Control-Allow-Origin'] = origin or '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, PATCH, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    response.headers['Access-Control-Expose-Headers'] = 'Content-Type, Content-Disposition'
    response.headers['Access-Control-Max-Age'] = '86400'
    return response

@app.after_request
def after_request(response):
    """Add CORS headers to every response"""
    return add_cors_headers(response)

@app.before_request
def handle_preflight():
    """Global OPTIONS handler for all routes"""
    if request.method == "OPTIONS":
        response = make_response()
        return add_cors_headers(response), 204
    return None

# --- END CORS CONFIGURATION ---

# --- LLM Client Setup ---
client = OpenAI(
    api_key=os.getenv("PERPLEXITY_API_KEY"), 
    base_url="https://api.perplexity.ai"
)

@app.route("/deepresearch", methods=["POST", "OPTIONS"])
def deepresearch():
    if request.method == "OPTIONS":
        return add_cors_headers(make_response()), 204

    data = request.get_json()
    prompt = data.get("prompt")
    if not prompt:
        return add_cors_headers(jsonify({"error": "Missing prompt"})), 400

    response = client.chat.completions.create(
        model="sonar-deep-research",
        messages=[{"role": "user", "content": prompt}, 
        ], 
        # search_mode="web",  # Perplexity-specific
        # return_citations=True
    )
    return add_cors_headers(jsonify({"result": response.choices[0].message.content}))

if __name__ == "__main__":
    app.run(port=5000)