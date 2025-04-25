# News Articles Telegram Downloader

Automated extraction and delivery of daily newspaper files from Telegram channels.

## Folder Structure
Each run creates a folder named after today's date (e.g., `25-04-2025`) containing the downloaded files:

```
<date>/
├── Indian_Express_<date>.pdf
├── Indian_Express_UPSC_<date>.pdf
├── The_Hindu_<date>.pdf
├── Indian_Express_<date>.jpg
├── The_Hindu_<date>.jpg
```

The downloadable/uploaded artifact is named after the date (e.g., `25-04-2025`).

## GitHub Actions Schedule
This workflow is automated to run daily at 5:30 AM UTC:

```yaml
on:
  schedule:
    - cron: '30 5 * * *'  # Runs daily at 5:30 AM UTC
  workflow_dispatch:
```

## Setup Instructions

1. **Clone the repository and set up your environment:**
    ```sh
    python3 -m venv .venv
    source .venv/bin/activate
    pip install telethon Pillow PyMuPDF python-docx poppler-utils pytesseract PyPDF2
    ```
2. **Generate a Telegram session string:**
    ```sh
    python generate_session.py
    ```
    - Enter your phone number (with country code, no `+`).
    - Copy the code sent to your Telegram app and paste it.
    - Save the generated session string in GitHub secrets as `TELEGRAM_SESSION_STRING`.

3. **Add Email Secrets (for automated delivery):**
    - `EMAIL_SENDER` – Sender's email address
    - `EMAIL_PASSWORD` – App password for the sender's email
    - `EMAIL_RECEIVER` – Recipient's email address

## Running the Workflow
- The workflow runs automatically on the schedule above or can be triggered manually via GitHub Actions.

---
