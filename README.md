# AcademiaAI — AI-Powered Academic Assistant

AcademiaAI is a Flask-based learning application that uses a language-model API to help students explore topics, generate study material, visualize concepts, and keep a history of their learning sessions.

## Features

- **AI-assisted explanations:** Submit a topic or question and request a response in a selected learning mode.
- **Concept visualization:** Generate structured concept data and visual diagrams for a topic.
- **Study flashcards:** Request question-and-answer flashcards for revision.
- **Related learning videos:** Search YouTube for videos related to a topic.
- **Learning history:** Save, view, and delete previous question-and-answer sessions.
- **PDF export:** Export a learning response as a PDF.
- **User accounts:** Sign up, log in, and manage an individual learning history.
- **Automated tests:** A pytest test suite is included.

## Technology Stack

| Area | Technologies |
|---|---|
| Backend | Python, Flask |
| Database | MongoDB, Flask-PyMongo |
| AI integration | OpenAI-compatible chat completions API |
| Frontend | HTML, CSS, JavaScript |
| Visualization | Matplotlib |
| PDF generation | ReportLab |
| Authentication and security | Flask-Login, bcrypt, Flask-WTF |
| Testing | pytest, mongomock |

The application is configured to use OpenAI by default and can also be configured with a compatible provider such as Groq through environment variables.

## Project Structure

```text
AcademiaAI/
├── app.py
├── config.py
├── extensions.py
├── models/
├── routes/
├── services/
├── templates/
├── static/
├── tests/
├── utils/
├── requirements.txt
└── pytest.ini
```

## Getting Started

### Prerequisites

- Python 3.10 or later
- MongoDB running locally or a MongoDB connection string
- An API key for the selected supported language-model provider

### 1. Clone the repository

```bash
git clone https://github.com/KUMAR-N084/AcademiaAI.git
cd AcademiaAI
```

### 2. Create and activate a virtual environment

**Windows (PowerShell):**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**macOS / Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a local `.env` file in the project root. Do not commit this file.

For an OpenAI configuration:

```env
SECRET_KEY=replace-with-a-long-random-secret
MONGO_URI=mongodb://localhost:27017/academic_assistant
OPENAI_API_KEY=your-provider-api-key
OPENAI_MODEL=gpt-4o-mini
FLASK_ENV=development
```

For a Groq-compatible configuration, use `GROQ_API_KEY` instead of `OPENAI_API_KEY`. The application detects Groq keys and selects its configured Groq endpoint and default model. Do not publish real API keys or secret values.

### 5. Start the application

Make sure MongoDB is running, then execute:

```bash
python app.py
```

Open the local address shown by Flask in your browser (normally `http://127.0.0.1:5000`).

## Running Tests

With the virtual environment active:

```bash
pytest
```

The test configuration includes a MongoDB mock for tests. A passing test run should be confirmed in your own environment before treating the project as verified.

## Configuration Notes

- Keep `.env`, database files, virtual environments, and generated files out of version control.
- Use a unique, randomly generated `SECRET_KEY` outside local development.
- Keep API keys private and rotate any key that has been accidentally committed.
- API usage may incur charges or be subject to the provider's rate limits.

## Project Status

This repository contains the application source code and an automated test suite. Setup and provider configuration may need to be adjusted for your local environment. Contributions and suggestions are welcome.
