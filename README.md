Economics-Chatbot

A small teaching chatbot and interactive frontend for basic economics concepts.

Files
- [backend/chatbot.py](backend/chatbot.py): Flask-based backend (NLP intent matching with NLTK).
- [frontend/index.html](frontend/index.html): Chat UI and interactive tools.
- [frontend/script.js](frontend/script.js): Client logic for chat and interactive charts.
- [frontend/styles.css](frontend/styles.css): Pink/feminine theme + responsive layout.
- [requirements.txt](requirements.txt): Python dependencies for the backend.

Usage
- Type questions in the chat or click a topic to get explanations and examples.
- Open the Tools panel to see the Supply & Demand demo, PPF simulator, and Price Control mini-game.
- Charts use Chart.js from a CDN; an internet connection is required for the CDN asset.