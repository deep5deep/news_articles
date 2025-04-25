# news
newspaper extraction

Folder structure:
Downloads/
├── To_read/
│   ├── Indian_Express_08-01-2025.docx
│   └── The_Hindu_08-01-2025.docx
├── Organized_text/
│   ├── Indian_Express_08-01-2025.txt
│   └── The_Hindu_08-01-2025.txt
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

python3 -m venv /Users/deepeshbathija/Library/CloudStorage/OneDrive-IBM/Documents/Scripts/news/.venv
source /Users/deepeshbathija/Library/CloudStorage/OneDrive-IBM/Documents/Scripts/news/.venv/bin/activate
pip install telethon Pillow PyMuPDF python-docx poppler-utils pytesseract PyPDF2
python3 -m pip install telethon Pillow PyMuPDF python-docx poppler-utils pytesseract PyPDF2

python telegram_downloader.py
python extract_text.py
python organize_text.py
python save_article.py
