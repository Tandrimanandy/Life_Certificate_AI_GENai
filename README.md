# Life_Certificate_AI_GENai

# PensionAssist: AI Life Certificate Assistance System

[![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-Web%20App-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Pandas](https://img.shields.io/badge/Pandas-Data%20Handling-150458?logo=pandas&logoColor=white)](https://pandas.pydata.org/)
[![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![Google Gemini](https://img.shields.io/badge/Google%20Gemini-AI%20Guidance-8E75B2?logo=googlegemini&logoColor=white)](https://ai.google.dev/gemini-api/docs)
[![Google GenAI SDK](https://img.shields.io/badge/Google%20GenAI%20SDK-google--genai-4285F4?logo=google&logoColor=white)](https://github.com/googleapis/python-genai)
[![python-dotenv](https://img.shields.io/badge/python--dotenv-Configuration-ECD53F?logo=python&logoColor=black)](https://pypi.org/project/python-dotenv/)

A Streamlit-based educational demonstration of a pension Life Certificate workflow. It verifies submitted details against registered pensioner records, stores every submission in SQLite, and uses Google Gemini to explain rejections and answer general pension questions.

> **Disclaimer:** This is an educational software demonstration. It is not an official government or bank portal, and local verification results are not official pension approvals.

---

## Table of Contents

- [Screenshots](#screenshots)
- [Key Features](#key-features)
- [Technology Stack](#technology-stack)
- [How Verification Works](#how-verification-works)
- [Key Functions](#key-functions)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Usage](#usage)
- [Security and Privacy](#security-and-privacy)
- [Limitations](#limitations)
- [License](#license)

---

## Screenshots

| Dashboard | Submit / Resubmit Certificate |
|---|---|
<img width="1589" height="801" alt="Dashboard" src="https://github.com/user-attachments/assets/37cf3fb0-a5ec-4770-8cc2-ea5c6157ed19" />



<img width="1547" height="745" alt="Submit_Result" src="https://github.com/user-attachments/assets/c1e8f7d3-5d04-4bd3-b055-c88f36b731af" />


| Certificate History | Pensioner Records |
|---|---|

<img width="1556" height="741" alt="Certificate_history" src="https://github.com/user-attachments/assets/4eecd676-d6cc-4d4f-956e-5e82cc3c1b9c" />

<img width="1562" height="730" alt="Pensioner_records" src="https://github.com/user-attachments/assets/487afdd1-efbe-44f8-b28d-56c436fb47cd" />

| AI Pension Chatbot |
|---|
<img width="1582" height="732" alt="AI_pension_chatbot" src="https://github.com/user-attachments/assets/79bf7939-52c6-4c3a-9b75-07a545904898" />


---

## Key Features

- **Application dashboard:** Summary cards for registered pensioners, total submissions, approved demo certificates and rejected submissions, plus a table of recent submissions.
- **Life Certificate submission and resubmission:** Look up a registered pensioner by PPO number, then submit the PPO, bank account and IFSC details for verification.
- **Automated verification:** Each submission is checked field by field against the registered record, and every attempt is saved with its status and reason.
- **AI rejection explanation:** Gemini explains in plain English why a submission failed, what the mismatch means, and how to make a corrected resubmission.
- **AI pension chatbot:** Answers general questions about Life Certificates in simple language and directs users to their bank or pension authority for official confirmation.
- **Certificate history:** Search the full submission history for any PPO number.
- **Pensioner records:** View registered demo pensioners, with account numbers masked in the display.
- **Notifications:** For rejected submissions, generates WhatsApp-ready message text and can send a rejection email through Gmail SMTP on demand. Approved submissions display a demo success message.
- **Safety guardrails:** The AI assistant is instructed never to request OTPs, passwords, Aadhaar numbers or full bank credentials, and never to claim access to a bank or government portal.

---

## Technology Stack

| Layer | Technology | Purpose |
|---|---|---|
| User interface | [Streamlit](https://streamlit.io/) | Interactive multi-page web interface |
| Data handling | [Pandas](https://pandas.pydata.org/) | Tabular data display and processing |
| Database | [SQLite](https://www.sqlite.org/) | Pensioner records and certificate submission history |
| AI guidance | [Google Gemini](https://ai.google.dev/gemini-api/docs) | Rejection explanations and pension guidance |
| AI SDK | [Google GenAI SDK](https://github.com/googleapis/python-genai) (`google-genai`) | Client library for Gemini models |
| Configuration | [python-dotenv](https://pypi.org/project/python-dotenv/) | Loads API keys and settings from a `.env` file |
| Email | Python `smtplib` with Gmail SMTP | Sends rejection notification emails |

---

## How Verification Works

Each submitted certificate is compared with the registered pensioner record on three fields:

- **PPO number:** compared case-insensitively, ignoring leading and trailing spaces.
- **Bank account number:** compared exactly, after trimming spaces.
- **IFSC code:** compared case-insensitively.

If any field does not match, the submission is marked **REJECTED** and the mismatches are stored as the rejection reason. If all three match, it is marked **APPROVED** as a local demo result. Every attempt is recorded in the `life_certificates` table with a timestamp.

---

## Key Functions

The project separates the user interface (`app.py`) from the business logic, which lives in service modules. Each service handles one part of the workflow, so the code is easier to test, change and reuse.

The app stores the selected pensioner and the latest verification result in `st.session_state`. This lets the AI Rejection Explanation page use the result from the Submit page.

### Database Layer (`database.py`)

| Function | Purpose | Why it is used |
|---|---|---|
| `get_connection()` | Opens a SQLite connection to `database/pension.db`, creates the folder if needed, enables foreign keys and returns rows that behave like dictionaries. | Every service needs database access. Keeping the connection logic in one function keeps the database path and settings in one place. |
| `create_tables()` | Creates the `pensioners` and `life_certificates` tables if they do not already exist. | Makes setup repeatable. The app calls it at startup, so the database is ready without a manual step. |

### Demo Data (`seed_data.py`)

| Function | Purpose | Why it is used |
|---|---|---|
| `insert_dummy_records()` | Inserts three fictional demo pensioners. | Provides test data. `INSERT OR IGNORE` on the unique PPO number stops duplicate records when the app restarts. |

### Pensioner Lookup (`pensioner_service.py`)

| Function | Purpose | Why it is used |
|---|---|---|
| `get_pensioner_by_ppo(ppo_number)` | Finds one pensioner after trimming spaces and converting the PPO number to uppercase. | Used by the Submit and Certificate History pages. Normalising the input prevents false "not found" results caused by spacing or capitalisation. |
| `get_all_pensioners()` | Returns all pensioner records, ordered by ID. | Used by the Pensioner Records page. |
| `get_pensioner_by_id(pensioner_id)` | Finds one pensioner by internal ID. | Currently not called by `app.py`. Available for future features. |

### Verification (`verification_service.py`)

| Function | Purpose | Why it is used |
|---|---|---|
| `verify_certificate(pensioner, submitted_ppo, submitted_account, submitted_ifsc)` | Compares the three submitted fields with the registered record, sets the status to APPROVED or REJECTED, saves the attempt and returns the result. | This is the core business rule. It runs on every submission, records each attempt for history, and reports all mismatches together. |

### Certificate History (`certificate_service.py`)

| Function | Purpose | Why it is used |
|---|---|---|
| `get_certificate_history(pensioner_id)` | Returns all submissions for one pensioner, newest first. | Used by the Certificate History page. |
| `get_all_certificates()` | Returns all submissions joined with pensioner names. | Currently not called by `app.py`. Available for a future administrative report. |

### AI Guidance (`gemini_service.py`)

| Function | Purpose | Why it is used |
|---|---|---|
| `generate_ai_text(prompt)` | Checks that the API key exists, calls the Gemini model with a temperature of 0.3 and a 700-token limit, applies the system instruction and returns the text. | A single entry point for all Gemini calls. It enforces the safety instruction, keeps output settings consistent and raises clear errors for a missing key or an empty response. |
| `explain_rejection(pensioner_name, rejection_reason)` | Builds a prompt that explains a rejection and suggests corrective steps. | Used by the AI Rejection Explanation page. The prompt asks for plain language and forbids guaranteeing approval. |
| `generate_pension_guidance(question)` | Builds a prompt for a general pension question. | Used by the AI Pension Chatbot page. The prompt directs users to their bank or pension authority for official rules. |

A lower temperature makes the responses more consistent and less random, which suits factual guidance.

### Notifications (`notification_service.py` and `email_service.py`)

| Function | Purpose | Why it is used |
|---|---|---|
| `generate_whatsapp_message(name, certificate_id, reason)` | Formats a rejection message. | Shown as a preview on the Submit page. The application does not send WhatsApp messages. |
| `generate_success_message(name, certificate_id)` | Formats an approval message with a note that it is not official approval. | Shown when the demo checks pass. |
| `send_pension_email(receiver_email, pensioner_name, certificate_id, rejection_reason)` | Sends the rejection email through Gmail SMTP using STARTTLS and returns `(success, message)`. | Runs only when the user clicks "Send email notification" after a rejection. Returning a success flag and a message lets the interface show a clear result, even when email settings are missing or wrong. |

### Interface Helpers (`app.py`)

| Function | Purpose | Why it is used |
|---|---|---|
| `hero(title, subtitle)` | Renders the top banner with the logo. | Keeps the page header consistent. |
| `section(title)` | Renders a styled section heading. | Gives every page the same heading style. |
| `metric_card(label, value, variant)` | Renders one dashboard summary card. | Avoids repeating the same HTML for each dashboard metric. |
| `info_card(rows)` | Renders a panel of label and value rows. | Displays pensioner details and rejection reasons in one consistent format. |

## Project Structure

```text
pensionassist/
├── app.py                    # Streamlit application and page navigation
├── database.py               # SQLite connection and table creation
├── seed_data.py              # Inserts demo pensioner records
├── pensioner_service.py      # Pensioner lookup queries
├── certificate_service.py    # Certificate history queries
├── verification_service.py   # PPO, account and IFSC verification logic
├── gemini_service.py         # Gemini prompts and API calls
├── email_service.py          # Gmail SMTP notifications
├── notification_service.py   # WhatsApp and success message templates
├── config.toml               # Streamlit theme configuration
├── requirements.txt          # Python dependencies
├── .env                      # Local secrets (not committed)
├── database/
│   └── pension.db            # SQLite database (created at runtime)
└── docs/                     # Screenshots used in this README
```

---

## Getting Started

### Prerequisites

- Python 3.9 or later
- A Google Gemini API key from [Google AI Studio](https://aistudio.google.com/)
- A Gmail account with an [App Password](https://support.google.com/accounts/answer/185833) (optional, required only for email notifications)

### 1. Clone the repository

```bash
git clone https://github.com/<your-username>/pensionassist.git
cd pensionassist
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-3.6-flash
SENDER_EMAIL=your_email@gmail.com
SENDER_APP_PASSWORD=your_gmail_app_password
```

| Variable | Required | Description |
|---|---|---|
| `GEMINI_API_KEY` | Yes | Enables the AI rejection explanation and chatbot |
| `GEMINI_MODEL` | No | Gemini model name; defaults to `gemini-3.6-flash` |
| `SENDER_EMAIL` | No | Gmail address used to send notifications |
| `SENDER_APP_PASSWORD` | No | Gmail App Password for SMTP login |

### 5. Database setup (automatic)

The application creates the SQLite tables and loads the demo pensioners automatically the first time it starts. You can also run the scripts manually:

```bash
python database.py    # creates the tables
python seed_data.py   # loads the demo pensioners
```

### 6. Run the application

```bash
streamlit run app.py
```

Open the application at [http://localhost:8501](http://localhost:8501).

---

## Usage

1. **Dashboard:** Review pensioner and submission totals.
2. **Submit / Resubmit Certificate:** Enter a registered PPO number, confirm the pensioner, then submit the certificate details.
3. **AI Rejection Explanation:** Request a plain-language explanation of a rejected submission.
4. **AI Pension Chatbot:** Ask general questions about Life Certificates.
5. **Certificate History:** Enter a PPO number to view all its past submissions and their outcomes.
6. **Pensioner Records:** Browse the registered demo pensioners.

Demo PPO numbers loaded by `seed_data.py` can be used to test the workflow.

---

## Security and Privacy

- Never commit the `.env` file or share your API keys. Add `.env` and `database/` to `.gitignore`.
- The included seed data is fictional and for demonstration only. Do not replace it with real pensioner data.
- The AI features send prompts to the Google Gemini API. Do not enter OTPs, passwords, Aadhaar numbers or full bank credentials.
- Account numbers are masked in the Pensioner Records view.

---

## Limitations

- This is a demonstration. Verification uses simple field matching and does not connect to any bank, government or pension database.
- Approved results carry no official status.
- WhatsApp messages are generated as text only; the application does not send them.
- The AI responses are guidance only and may be incomplete or inaccurate. Users should confirm details with their bank or pension authority.

---

## License

Add your license here, for example MIT. Include a `LICENSE` file in the repository root.
