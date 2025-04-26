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
    - `EMAIL_PASSWORD` – App password for the sender's email (see below)
    - `EMAIL_RECEIVER` – Recipient's email address

### Setting up Gmail App Password for `EMAIL_PASSWORD`

To use a Gmail account for sending emails via GitHub Actions, you must use an App Password (not your regular Gmail password):

1. **Create an App Password**
    - Go to your [Google Account Security settings](https://myaccount.google.com/security).
    - Under "Signing in to Google," find **App passwords** (you may need to enable 2-Step Verification first).
    - Under “Select app,” choose **Mail**.
    - Under “Select device,” choose **Other (Custom name)**, and enter a name like `GitHub Actions News`.
    - Click **Generate**.
    - Copy the 16-character password provided.
2. **Update your GitHub secret**
    - In your repo’s **Settings → Secrets → Actions**, set `EMAIL_PASSWORD` to the new 16-character App Password.

## Running the Workflow
- The workflow runs automatically on the schedule above or can be triggered manually via GitHub Actions.

## To Do:

* Change email sender and email password in GitHub secrets
* Upload it to Google Drive
---
