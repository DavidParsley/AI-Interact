from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

app = FastAPI()

app.add_middleware(CORSMiddleware,allow_origins=['*'],allow_methods=['*'])

from routes import *
app.include_router(user.router)
app.include_router(query.router)

@app.get('/')
def index():
    return {"message": "Welcome to AI Interact"}

@app.get('/guide', response_class=HTMLResponse)
def guide():
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <title>AI Interact Developer Guide</title>
      <style>
        body {
          font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
          margin: 60px auto;
          max-width: 900px;
          line-height: 1.8;
          background-color: #fdfdfd;
          color: #2c3e50;
          transition: background-color 0.3s, color 0.3s;
        }

        body.dark-mode {
          background-color: #1e1e1e;
          color: #f5f5f5;
        }

        h1, h2, h3 {
          color: inherit;
        }

        h1 {
          text-align: center;
          font-size: 2.8em;
          margin-bottom: 30px;
        }

        body.dark-mode h3 {
        color: #fff; 
        }

        code {
          background: #f4f4f4;
          padding: 3px 6px;
          border-radius: 5px;
          font-size: 0.95em;
          color: #d63384;
        }

        body.dark-mode code {
          background: #2a2a2a;
          color: #ffb6c1;
        }

        pre {
          background: #f4f4f4;
          padding: 15px;
          border-left: 6px solid #007acc;
          overflow-x: auto;
          border-radius: 5px;
          font-size: 0.95em;
        }

        body.dark-mode pre {
          background: #2a2a2a;
          border-left: 6px solid #00bfff;
        }

        .section {
          margin-bottom: 50px;
        }

        .section h2 {
          border-bottom: 2px solid #ddd;
          padding-bottom: 8px;
          margin-bottom: 20px;
          font-size: 1.6em;
        }

        p {
          font-size: 1.05em;
        }

        .endpoint {
          margin-top: 20px;
        }

        .endpoint h3 {
          margin-bottom: 10px;
          color: #0c5460;
        }
        

        .note {
          font-size: 0.9em;
          color: #555;
        }

        body.dark-mode .note {
          color: #bbb;
        }

        .toggle-btn {
          position: fixed;
          top: 20px;
          right: 30px;
          background-color: #007acc;
          color: white;
          border: none;
          padding: 8px 14px;
          border-radius: 6px;
          font-size: 0.95em;
          cursor: pointer;
          transition: background-color 0.3s;
        }

        .toggle-btn:hover {
          background-color: #005fa3;
        }

        body.dark-mode .toggle-btn {
          background-color: #444;
        }

        body.dark-mode .toggle-btn:hover {
          background-color: #666;
        }
      </style>
    </head>
    <body>

      <button class="toggle-btn" onclick="toggleDarkMode()">🌗 Toggle Mode</button>

      <h1>📘 AI Interact Developer Guide</h1>
      <p><strong>Base URL:</strong> <code>http://localhost:8000</code></p>

      <div class="section">
        <h2>🔹 Root</h2>
        <div class="endpoint">
          <h3>GET /</h3>
          <p>Returns a welcome message.</p>
          <pre><code>{
  "message": "Welcome to AI Interact"
}</code></pre>
        </div>
      </div>

      <div class="section">
        <h2>👤 User Routes</h2>
        <div class="endpoint">
          <h3>POST /user/signup</h3>
          <p>Register a new user</p>
          <pre><code>{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "securepassword"
}</code></pre>
          <pre><code>{
  "message": "User created successfully",
  "user": {
    "access_token": "&lt;JWT Token&gt;"
  }
}</code></pre>
        </div>
        <div class="endpoint">
          <h3>POST /user/login</h3>
          <p>Authenticate user and return JWT token</p>
          <pre><code>{
  "email": "john@example.com",
  "password": "securepassword"
}</code></pre>
          <pre><code>{
  "access_token": "&lt;JWT Token&gt;"
}</code></pre>
        </div>
        <div class="endpoint">
          <h3>GET /user/current_user</h3>
          <p>Get current user info</p>
          <p class="note"><strong>Headers:</strong> <code>Authorization: Bearer &lt;JWT Token&gt;</code></p>
          <pre><code>{
  "id": 1,
  "name": "John Doe",
  "email": "john@example.com"
}</code></pre>
        </div>
        <div class="endpoint">
          <h3>PATCH /user/update</h3>
          <p>Update user's email or password</p>
          <p class="note"><strong>Headers:</strong> <code>Authorization: Bearer &lt;JWT Token&gt;</code></p>
          <pre><code>{
  "email": "newemail@example.com",
  "password": "newsecurepassword"
}</code></pre>
          <pre><code>{
  "message": "User updated successfully",
  "user": {
    "id": 1,
    "email": "newemail@example.com"
  }
}</code></pre>
        </div>
        <div class="endpoint">
          <h3>DELETE /user/logout</h3>
          <p>Logs out the user</p>
          <p class="note"><strong>Headers:</strong> <code>Authorization: Bearer &lt;JWT Token&gt;</code></p>
          <pre><code>{
  "message": "Successfully logged out"
}</code></pre>
        </div>
      </div>

      <div class="section">
        <h2>💬 LLM Interaction Routes</h2>
        <div class="endpoint">
          <h3>POST /query</h3>
          <p>Ask a question to the DeepSeek model</p>
          <p class="note"><strong>Headers:</strong> <code>Authorization: Bearer &lt;JWT Token&gt;</code></p>
          <pre><code>{
  "query_text": "What documents do I need to travel from Kenya to Ireland?"
}</code></pre>
          <pre><code>{
  "query": "What documents do I need to travel from Kenya to Ireland?",
  "response": "To travel from Kenya to Ireland, you will need..."
}</code></pre>
        </div>
        <div class="endpoint">
          <h3>POST /query/reset</h3>
          <p>Resets current conversation and starts a new one</p>
          <p class="note"><strong>Headers:</strong> <code>Authorization: Bearer &lt;JWT Token&gt;</code></p>
          <pre><code>[
  {
    "message": "Started a new conversation.",
    "conversation_id": "123abc456"
  }
]</code></pre>
        </div>
        <div class="endpoint">
          <h3>GET /query/history</h3>
          <p>Retrieve user's previous queries</p>
          <p class="note"><strong>Headers:</strong> <code>Authorization: Bearer &lt;JWT Token&gt;</code></p>
          <pre><code>[
  {
    "query_text": "What documents do I need to travel from Kenya to Ireland?",
    "response_text": "To travel from Kenya to Ireland, you will need...",
    "created_at": "2025-04-19T12:34:56.789Z"
  }
]</code></pre>
        </div>
      </div>

      <div class="section">
        <h2>🛠 Environment Variables</h2>
        <pre><code>
OPENROUTER_API_KEY=your_api_key_here
OPENROUTER_API_URL=https://openrouter.ai/api/v1/chat/completions
</code></pre>
      </div>

      <script>
        function toggleDarkMode() {
          document.body.classList.toggle('dark-mode');
        }
      </script>

    </body>
    </html>
    """
    return html_content
   