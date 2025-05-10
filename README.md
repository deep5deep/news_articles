# News Articles Telegram Downloader

Automated extraction and delivery of daily newspaper files from Telegram channels.

## Features

- Automated download of news articles from Telegram channels
- Organized file storage by date
- **Separate emails for each newspaper** - Indian Express and The Hindu sent as separate emails
- Email delivery with Dublin timezone timestamp
- Support for multiple email recipients
- **Smart date format handling** - Tries different date formats (with/without leading zeros) if the initial download fails
- Support for multiple newspaper editions (UPSC, Delhi) from the same channel
- **Google Drive integration** - Automatically uploads downloaded files to Google Drive

## Folder Structure

Each run creates a folder named after today's date (e.g., `25-04-2025`) containing the downloaded files:

```text
<date>/
├── Indian_Express_<date>.pdf
├── Indian_Express_UPSC_<date>.pdf
├── The_Hindu_UPSC_<date>.pdf
├── The_Hindu_Delhi_<date>.pdf
├── Indian_Express_<date>.jpg
├── The_Hindu_<date>.jpg
```

The downloadable/uploaded artifact is named after the date (e.g., `25-04-2025`).

## Email Structure

The system sends two separate emails:

1. **Indian Express Articles** - Contains all Indian Express files (both editions and image)
2. **The Hindu Articles** - Contains all The Hindu files (both editions and image)

This separation helps avoid email size limits and keeps content organized by publication.

## Supported File Formats

The downloader handles various file naming formats from different Telegram channels:

| Publication | Edition | Format in Telegram | Example |
|-------------|---------|-------------------|---------|
| Indian Express | Delhi | `INDIAN EXPRESS HD Delhi dd~mm~yyyy.pdf` | `INDIAN EXPRESS HD Delhi 04~05~2025.pdf` |
| Indian Express | UPSC | `INDIAN EXPRESS UPSC IAS EDITION HD dd~mm~yyyy.pdf` | `INDIAN EXPRESS UPSC IAS EDITION HD 04~05~2025.pdf` |
| The Hindu | UPSC | `THE HINDU UPSC IAS EDITION HD dd~mm~yyyy.pdf` | `THE HINDU UPSC IAS EDITION HD 04~05~2025.pdf` |
| The Hindu | Delhi | `TH Delhi dd--mm.pdf` | `TH Delhi 4--5.pdf` or `TH Delhi 04--05.pdf` |

The system handles variations with and without leading zeros in date formats.

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

4. **Add Google Drive Secrets (for file uploads):**

    - `GOOGLE_DRIVE_CREDENTIALS` – Your Google Service Account credentials JSON (see below)
    - `GOOGLE_DRIVE_FOLDER_ID` – (Optional) The ID of a parent folder in Google Drive (default: creates daily folders in root)

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

### Setting up Google Drive Service Account for `GOOGLE_DRIVE_CREDENTIALS`

To set up Google Drive uploads, you need to create a Service Account and get its credentials:

1. **Create a Google Cloud project:**

    - Go to the [Google Cloud Console](https://console.cloud.google.com/).
    - Create a new project or select an existing one.

2. **Enable the Google Drive API:**

    - In your project, navigate to "APIs & Services" > "Library".
    - Search for "Google Drive API" and enable it.

3. **Create a Service Account:**

    - Go to "APIs & Services" > "Credentials".
    - Click "Create credentials" > "Service account".
    - Enter a name and description for your service account.
    - Click "Create and continue".
    - In the "Grant this service account access to project" section, add the "Editor" role.
    - Click "Continue" and then "Done".

4. **Generate Service Account Key:**

    - In the Service Accounts list, find the one you just created.
    - Click on the service account to view its details.
    - Go to the "Keys" tab.
    - Click "Add Key" > "Create new key".
    - Choose "JSON" as the key type and click "Create".
    - The key file will be downloaded automatically.

5. **Share Drive Folder with Service Account:**

    - If you want to use a specific folder in Google Drive:
        - Create or select a folder in Google Drive.
        - Right-click on the folder and select "Share".
        - Share the folder with the email address of your service account (it ends with `@*.gserviceaccount.com`).
        - Copy the folder ID from the URL (it's the long alphanumeric string after `/folders/` in the URL).
        - Add this ID as the `GOOGLE_DRIVE_FOLDER_ID` GitHub secret.

6. **Add Service Account Credentials to GitHub Secrets:**

    - Open the downloaded JSON key file.
    - Copy all of its contents.
    - In your GitHub repository, create a new secret named `GOOGLE_DRIVE_CREDENTIALS`.
    - Paste the entire JSON content as the value for this secret.
    - In your repo's **Settings → Secrets → Actions**, set `EMAIL_PASSWORD` to the new 16-character App Password.

## Google Drive Service Credentials & Folder ID Setup

To enable Google Drive uploads, you must create a Google Service Account, enable the Drive API, and add the credentials and (optionally) a folder ID to your GitHub Actions secrets.

### 1. Create a Google Cloud Project

- Go to the [Google Cloud Console](https://console.cloud.google.com/).
- Create a new project or select an existing one.

### 2. Enable the Google Drive API

- In your project, go to "APIs & Services" > "Library".
- Search for "Google Drive API" and enable it.

### 3. Create a Service Account

- Go to "APIs & Services" > "Credentials".
- Click "Create Credentials" > "Service account".
- Enter a name and description, click "Create and Continue".
- Grant the "Editor" role, click "Continue" and then "Done".

### 4. Generate a Service Account Key

- In the Service Accounts list, click your new service account.
- Go to the "Keys" tab.
- Click "Add Key" > "Create new key" > select "JSON" > "Create".
- Download and save the JSON key file securely.

### 5. Share Your Google Drive Folder (Optional)

- In Google Drive, create/select a folder for uploads.
- Right-click > "Share" > add your service account email (from the JSON, ends with `@<project>.iam.gserviceaccount.com`).
- Set as "Editor".
- Copy the folder ID from the URL (the long string after `/folders/`).

### 6. Add Secrets to GitHub Actions

- Go to your repo: **Settings → Secrets and variables → Actions**.
- Click "New repository secret" for each:
  - `GOOGLE_DRIVE_CREDENTIALS`: Paste the entire JSON key file content.
  - `GOOGLE_DRIVE_FOLDER_ID`: (Optional) Paste the folder ID from step 5.

Once set, your workflow will be able to upload files to Google Drive, organized by date, inside the specified folder if provided.

## Dependencies

This project requires the following Python libraries:

- **telethon**: For downloading articles from Telegram channels
- **pytz**: For handling timezone information in email notifications

All dependencies are listed in the `requirements.txt` file.

## Running the Workflow

- The workflow runs automatically on the schedule above or can be triggered manually via GitHub Actions.
- Separate emails are sent for Indian Express and The Hindu articles, each with Dublin timezone timestamps.
- GitHub Actions logs will show notices when the email process starts and completes.

## To Do

- Remove additional email receivers

---
