# News Articles Telegram Downloader

Automated extraction and delivery of daily newspaper files from Telegram channels.

## Features

- Automated download of news articles from Telegram channels
- Organized file storage by date
- Email delivery with Dublin timezone timestamp
- Support for multiple email recipients
- Smart retry system with 1-hour intervals between attempts
- Only sends email when all 3 newspapers are available or after maximum retry attempts

## Folder Structure

Each run creates a folder named after today's date (e.g., `25-04-2025`) containing the downloaded files:

```text
<date>/
├── Indian_Express_<date>.pdf
├── Indian_Express_UPSC_<date>.pdf
├── The_Hindu_<date>.pdf
├── Indian_Express_<date>.jpg
├── The_Hindu_<date>.jpg
├── download_status.json     # Tracks download progress and newspaper status
├── email_sent.txt           # Indicates if email has been sent for the day
```

The downloadable/uploaded artifact is named after the date (e.g., `25-04-2025`).

## Retry Logic

The system will attempt to download all three newspapers:
1. Indian Express
2. Indian Express UPSC Edition
3. The Hindu

If any newspapers are missing:
- The system will retry up to 3 times with 1-hour intervals between attempts
- Only sends email when either:
  - All 3 newspapers are successfully downloaded, or
  - After the 3rd attempt (with whatever newspapers are available)
- The email will indicate which newspapers were successfully downloaded
- Duplicate emails are prevented even if multiple workflow runs occur on the same day

## GitHub Actions Workflow

This workflow is automated to run daily at 5:30 AM UTC:

```yaml
on:
  schedule:
    - cron: '30 5 * * *'  # Runs daily at 5:30 AM UTC
  workflow_dispatch:
```

The system uses two complementary workflows:
1. `schedule.yml` - Main workflow that downloads newspapers and sends emails
2. `schedule_retry.yml` - Helper workflow that handles the 1-hour delay between retry attempts

## Setup Instructions

1. **Clone the repository and set up your environment:**

    ```sh
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
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
    - `EMAIL_RECEIVER` – Primary recipient's email address
    - `ADDITIONAL_EMAIL_RECEIVERS` – (Optional) Comma-separated list of additional email recipients (e.g., `person1@example.com`, `person2@example.com`)

### Setting up Gmail App Password for `EMAIL_PASSWORD`

To use a Gmail account for sending emails via GitHub Actions, you must use an App Password (not your regular Gmail password):

1. **Create an App Password**
    - Go to your [Google Account Security settings](https://myaccount.google.com/security).
    - Under "Signing in to Google," find **App passwords** (you may need to enable 2-Step Verification first).
    - Under "Select app," choose **Mail**.
    - Under "Select device," choose **Other (Custom name)**, and enter a name like `GitHub Actions News`.
    - Click **Generate**.
    - Copy the 16-character password provided.
2. **Update your GitHub secret**
    - In your repo's **Settings → Secrets → Actions**, set `EMAIL_PASSWORD` to the new 16-character App Password.

## Dependencies

This project requires the following Python libraries:
- **telethon**: For downloading articles from Telegram channels
- **pytz**: For handling timezone information in email notifications
- **json**: For tracking download status between retry attempts

All dependencies are listed in the `requirements.txt` file.

## Running the Workflow

- The workflow runs automatically on the schedule above or can be triggered manually via GitHub Actions.
- Emails are sent with a Dublin timezone timestamp in both the subject line and email body for accurate time reference.
- GitHub Actions logs will show notices when the email process starts and completes.
- If you want to trigger a manual run, use the GitHub Actions workflow dispatch feature.

## Troubleshooting

- If emails show fewer than 3 newspapers despite multiple retries, check the Telegram channels to ensure the files are available.
- If you need to force an email with whatever newspapers are currently available, you can manually trigger the workflow and set the `retry_attempt` input to `3`.
- Check the GitHub Actions logs and the `download_status.json` file in the date folder to diagnose any issues.

## To Do

- Change email sender and email password in GitHub secrets
- Upload it to Google Drive

---
