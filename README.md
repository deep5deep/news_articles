# News Articles
newspaper extraction

Folder structure:
Downloads/
├── Newspapers/
│   ├── Indian_Express_08-01-2025.pdf
│   └── The_Hindu_08-01-2025.pdf
└── Highlights/
    ├── Indian_Express_08-01-2025.jpg
    ├── The_Hindu_08-01-2025.jpg
    └── Text_highlights/
        ├── Indian_Express_08-01-2025.txt
        └── The_Hindu_08-01-2025.txt

Steps:

Run generate_session.py locally to get the string and put it in github secrets

python3 -m venv .venv
source .venv/bin/activate
pip install telethon Pillow PyMuPDF python-docx poppler-utils pytesseract PyPDF2

python generate_session.py

To be run daily in github actions:
python telegram_downloader.py
