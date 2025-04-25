from PIL import Image
import pytesseract
import os
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_base_path():
    github_workspace = os.getenv('GITHUB_WORKSPACE')
    if github_workspace:
        return os.path.join(github_workspace, 'Downloads')
    return os.path.join(os.path.expanduser('~'), 'Library', 'CloudStorage', 'OneDrive-IBM', 'Documents', 'Scripts', 'news', 'Downloads')

def create_text_highlights_folder():
    base_path = os.path.join(get_base_path(), 'Highlights')
    new_folder_path = os.path.join(base_path, 'Text_highlights')
    
    os.makedirs(new_folder_path, exist_ok=True)
    logger.info(f"Text highlights folder: {new_folder_path}")
    
    return new_folder_path

def extract_newspaper_text(image_path, output_path):
    try:
        image = Image.open(image_path)
        image = image.convert('L')
        
        custom_config = r'--oem 3 --psm 1'
        text = pytesseract.image_to_string(image, config=custom_config)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(text)
        
        logger.info(f"Text extracted and saved to {output_path}")
    except Exception as e:
        logger.error(f"Error during extraction: {str(e)}")

def process_newspapers():
    highlights_folder = os.path.join(get_base_path(), 'Highlights')
    text_highlights_folder = create_text_highlights_folder()
    
    today = datetime.now().strftime("%d-%m-%Y")
    newspapers = ['Indian_Express', 'The_Hindu']
    
    for newspaper in newspapers:
        input_file = f"{newspaper}_{today}.jpg"
        output_file = f"{newspaper}_{today}.txt"
        
        input_path = os.path.join(highlights_folder, input_file)
        output_path = os.path.join(text_highlights_folder, output_file)
        
        if os.path.exists(input_path):
            extract_newspaper_text(input_path, output_path)
        else:
            logger.warning(f"Input file not found: {input_path}")

if __name__ == "__main__":
    process_newspapers()
