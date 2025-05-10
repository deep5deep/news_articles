from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import os
import json
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def setup_drive_service():
    """
    Set up and return Google Drive API service using service account credentials.
    
    Returns:
        Google Drive API service object
    """
    try:
        # Get credentials from GitHub secrets (stored as environment variable)
        credentials_json = os.environ.get('GOOGLE_DRIVE_CREDENTIALS')
        
        if not credentials_json:
            logger.error("Google Drive credentials not found in environment variables")
            print("ERROR: GOOGLE_DRIVE_CREDENTIALS environment variable is not set.")
            print("Please set this variable with your Google service account JSON.")
            return None
            
        # Parse credentials JSON from environment variable
        try:
            credentials_info = json.loads(credentials_json)
        except json.JSONDecodeError:
            logger.error("Invalid JSON format in GOOGLE_DRIVE_CREDENTIALS")
            print("ERROR: The GOOGLE_DRIVE_CREDENTIALS value is not valid JSON.")
            print("Make sure you've copied the entire JSON file contents correctly.")
            return None
            
        # Validate required fields in the credentials
        required_fields = ['client_email', 'private_key', 'type']
        missing_fields = [field for field in required_fields if field not in credentials_info]
        if missing_fields:
            logger.error(f"Missing required fields in credentials: {missing_fields}")
            print(f"ERROR: The service account JSON is missing required fields: {missing_fields}")
            return None
            
        # Create credentials object
        try:
            credentials = service_account.Credentials.from_service_account_info(
                credentials_info,
                scopes=['https://www.googleapis.com/auth/drive']
            )
        except Exception as e:
            logger.error(f"Error creating credentials object: {e}")
            print(f"ERROR: Failed to create credentials from service account JSON: {e}")
            return None
        
        # Build the Drive service
        service = build('drive', 'v3', credentials=credentials)
        logger.info("Google Drive service initialized successfully")
        return service
        
    except Exception as e:
        logger.error(f"Error setting up Google Drive service: {e}")
        return None

def upload_file_to_drive(service, file_path, parent_folder_id=None):
    """
    Upload a file to Google Drive.
    
    Args:
        service: Google Drive API service instance
        file_path: Path to the file to upload
        parent_folder_id: ID of the parent folder in Google Drive (optional)
        
    Returns:
        File ID if successful, None otherwise
    """
    try:
        file_name = os.path.basename(file_path)
        
        # File metadata
        file_metadata = {'name': file_name}
        
        # If parent folder specified, add to metadata
        if parent_folder_id:
            file_metadata['parents'] = [parent_folder_id]
        
        # Create media object
        media = MediaFileUpload(
            file_path,
            resumable=True
        )
        
        # Upload file
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()
        
        file_id = file.get('id')
        logger.info(f"Uploaded {file_name} to Google Drive with ID: {file_id}")
        return file_id
        
    except Exception as e:
        logger.error(f"Error uploading {os.path.basename(file_path)} to Google Drive: {e}")
        return None

def upload_file_as_gdoc(service, file_path, parent_folder_id=None):
    """
    Upload a file to Google Drive and request conversion to Google Docs format.
    Args:
        service: Google Drive API service instance
        file_path: Path to the file to upload
        parent_folder_id: ID of the parent folder in Google Drive (optional)
    Returns:
        File ID if successful, None otherwise
    """
    try:
        file_name = os.path.basename(file_path)
        ext = os.path.splitext(file_name)[1].lower()
        # Map extensions to Google Docs mimeTypes
        if ext in ['.txt', '.doc', '.docx', '.pdf', '.rtf', '.odt']:
            gdoc_mime = 'application/vnd.google-apps.document'
        elif ext in ['.jpg', '.jpeg', '.png']:
            gdoc_mime = 'application/vnd.google-apps.document'  # Google will OCR images
        else:
            return None  # Skip unsupported types for conversion
        file_metadata = {'name': file_name + '_gdoc', 'mimeType': gdoc_mime}
        if parent_folder_id:
            file_metadata['parents'] = [parent_folder_id]
        media = MediaFileUpload(file_path, resumable=True)
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()
        file_id = file.get('id')
        logger.info(f"Uploaded {file_name} as Google Doc to Drive with ID: {file_id}")
        return file_id
    except Exception as e:
        logger.error(f"Error uploading {os.path.basename(file_path)} as Google Doc: {e}")
        return None

def create_dated_folder(service, folder_name):
    """
    Create a folder in Google Drive with the specified name.
    
    Args:
        service: Google Drive API service instance
        folder_name: Name of the folder to create
        
    Returns:
        Folder ID if successful, None otherwise
    """
    try:
        folder_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        
        folder = service.files().create(
            body=folder_metadata,
            fields='id'
        ).execute()
        
        folder_id = folder.get('id')
        logger.info(f"Created dated folder '{folder_name}' in Google Drive with ID: {folder_id}")
        return folder_id
        
    except Exception as e:
        logger.error(f"Error creating folder {folder_name} in Google Drive: {e}")
        return None

def upload_files_to_drive(directory_path, parent_folder_id=None, file_filter=None):
    """
    Upload all files in a directory to Google Drive.
    
    Args:
        directory_path: Path to the directory containing files to upload
        parent_folder_id: ID of the parent folder in Google Drive (optional)
        file_filter: Filter function to determine which files to upload (optional)
                    The function should take a filename as input and return True/False
    
    Returns:
        Number of files successfully uploaded
    """
    # Initialize Drive service
    service = setup_drive_service()
    if not service:
        return 0
    
    # Create a dated folder
    today_str = datetime.now().strftime('%d-%m-%Y')
    
    # If parent_folder_id provided, create dated subfolder inside it
    # If not, create dated folder at root level
    dated_folder_id = create_dated_folder(service, today_str)
    if not dated_folder_id:
        return 0
    
    # If parent_folder_id exists, move the dated folder inside it
    if parent_folder_id:
        try:
            # Update the dated folder to be a child of the parent folder
            service.files().update(
                fileId=dated_folder_id,
                addParents=parent_folder_id,
                removeParents='root',
                fields='id, parents'
            ).execute()
            logger.info(f"Moved dated folder {today_str} into parent folder {parent_folder_id}")
        except Exception as e:
            logger.error(f"Error moving dated folder into parent: {e}")
            # Continue with upload even if move fails
    
    # Get list of files in directory
    files = [f for f in os.listdir(directory_path) if os.path.isfile(os.path.join(directory_path, f))]
    
    # Apply filter if specified
    if file_filter and callable(file_filter):
        files = [f for f in files if file_filter(f)]
    
    # Upload each file
    successful_uploads = 0
    gdoc_uploads = 0
    for file_name in files:
        file_path = os.path.join(directory_path, file_name)
        file_id = upload_file_to_drive(service, file_path, dated_folder_id)
        if file_id:
            successful_uploads += 1
        # Try uploading as Google Doc if supported
        gdoc_id = upload_file_as_gdoc(service, file_path, dated_folder_id)
        if gdoc_id:
            gdoc_uploads += 1
    
    logger.info(f"Uploaded {successful_uploads} original files and {gdoc_uploads} Google Docs to Google Drive in folder '{today_str}'")
    return successful_uploads + gdoc_uploads

# Example usage 
if __name__ == "__main__":
    today_str = datetime.now().strftime('%d-%m-%Y')
    directory_path = os.path.join(os.getenv('GITHUB_WORKSPACE', '.'), today_str)
    
    # Check if a specific parent folder ID is provided
    parent_folder_id = os.getenv('GOOGLE_DRIVE_FOLDER_ID')
    
    # Upload all files
    upload_files_to_drive(directory_path, parent_folder_id=parent_folder_id)
