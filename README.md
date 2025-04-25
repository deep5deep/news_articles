# News Articles
newspaper extraction

Folder structure:
<date>/
├── Indian_Express_<date>.pdf
├── Indian_Express_UPSC_<date>.pdf
├── The_Hindu_<date>.pdf
├── Indian_Express_<date>.jpg
├── The_Hindu_<date>.jpg

The downloadable/uploaded artifact is now named after today's date (e.g., 25-04-2025)

Steps:

Run generate_session.py locally to get the string and put it in github secrets as TELEGRAM_SESSION_STRING

python3 -m venv .venv
source .venv/bin/activate
pip install telethon Pillow PyMuPDF python-docx poppler-utils pytesseract PyPDF2

python generate_session.py
enter phone number with country code without +
open telegram and copy code from the chat
paste the code here
save the string in github secrets as TELEGRAM_SESSION_STRING

To be run daily in github actions:
python telegram_downloader.py
