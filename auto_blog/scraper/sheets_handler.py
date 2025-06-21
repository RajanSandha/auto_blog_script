"""
Google Sheets handler module.
Provides functionality to interact with Google Sheets API for tracking processed URLs.
"""

from typing import List, Dict, Any
from google.oauth2.credentials import Credentials
from google.oauth2.service_account import Credentials as ServiceAccountCredentials
from googleapiclient.discovery import build
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GoogleSheetsHandler:
    def __init__(self, credentials_file: str, spreadsheet_id: str, sheet_name: str = "ProcessedURLs"):
        """
        Initialize the Google Sheets handler.
        
        Args:
            credentials_file (str): Path to the Google service account credentials file
            spreadsheet_id (str): ID of the Google Sheet to use
            sheet_name (str): Name of the sheet to track URLs (default: ProcessedURLs)
        """
        self.credentials_file = credentials_file
        self.spreadsheet_id = spreadsheet_id
        self.sheet_name = sheet_name
        self.creds = self._get_credentials()
        self.service = build('sheets', 'v4', credentials=self.creds)
        self.sheet = self.service.spreadsheets()
        self._ensure_headers()

    def _get_credentials(self) -> Credentials:
        """Get Google Sheets API credentials."""
        try:
            return ServiceAccountCredentials.from_service_account_file(
                self.credentials_file,
                scopes=['https://www.googleapis.com/auth/spreadsheets']
            )
        except Exception as e:
            raise Exception(f"Failed to get credentials: {str(e)}")

    def _ensure_headers(self):
        """Ensure the sheet has the required headers."""
        try:
            # Check if headers exist
            result = self.sheet.values().get(
                spreadsheetId=self.spreadsheet_id,
                range=f'{self.sheet_name}!A1:C1'
            ).execute()
            
            if not result.get('values'):
                # Set headers if sheet is empty
                headers = [['URL', 'Processed Date', 'Status']]
                self.sheet.values().update(
                    spreadsheetId=self.spreadsheet_id,
                    range=f'{self.sheet_name}!A1:C1',
                    valueInputOption='RAW',
                    body={'values': headers}
                ).execute()
                logger.info("Created headers in the sheet")
        except Exception as e:
            raise Exception(f"Failed to ensure headers: {str(e)}")

    def get_processed_urls(self) -> List[str]:
        """
        Get list of all processed URLs from the sheet.
        
        Returns:
            List[str]: List of processed URLs
        """
        try:
            result = self.sheet.values().get(
                spreadsheetId=self.spreadsheet_id,
                range=f'{self.sheet_name}!A2:A'
            ).execute()
            
            values = result.get('values', [])
            # Extract URLs from the first column, skip empty rows
            return [row[0] for row in values if row]
        except Exception as e:
            logger.error(f"Failed to get processed URLs: {str(e)}")
            return []

    def add_processed_url(self, url: str) -> bool:
        """
        Add a new processed URL to the sheet.
        
        Args:
            url: The URL that was processed
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Get next empty row
            result = self.sheet.values().get(
                spreadsheetId=self.spreadsheet_id,
                range=f'{self.sheet_name}!A:A'
            ).execute()
            next_row = len(result.get('values', [])) + 1
            
            # Add new row with URL, date, and success status
            row_data = [[
                url,
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'SUCCESS'
            ]]
            
            self.sheet.values().update(
                spreadsheetId=self.spreadsheet_id,
                range=f'{self.sheet_name}!A{next_row}:C{next_row}',
                valueInputOption='RAW',
                body={'values': row_data}
            ).execute()
            
            logger.info(f"Added processed URL to sheet: {url}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add processed URL: {str(e)}")
            return False
