"""
Google Sheets API client for SWOT analysis and data visualization.
"""

import os
import json
from typing import Dict, Any, List, Optional
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from config.settings import get_settings


class GoogleSheetsClient:
    """Client for interacting with Google Sheets API."""
    
    def __init__(self):
        self.settings = get_settings()
        self.service = None
        self._initialize_service()
    
    def _initialize_service(self):
        """Initialize Google Sheets service with credentials."""
        try:
            # Load credentials from JSON file
            credentials_path = self.settings.google_sheets_credentials
            if os.path.exists(credentials_path):
                credentials = Credentials.from_service_account_file(
                    credentials_path,
                    scopes=['https://www.googleapis.com/auth/spreadsheets']
                )
                self.service = build('sheets', 'v4', credentials=credentials)
                print("✅ Google Sheets service initialized")
            else:
                print(f"⚠️ Google Sheets credentials not found at {credentials_path}")
                
        except Exception as e:
            print(f"❌ Failed to initialize Google Sheets service: {e}")
    
    async def create_swot_spreadsheet(
        self, 
        swot_data: Dict[str, Any], 
        title: str = "SWOT Analysis"
    ) -> Dict[str, Any]:
        """Create a new spreadsheet with SWOT analysis data."""
        
        if not self.service:
            return {
                "status": "error",
                "error_message": "Google Sheets service not available"
            }
        
        try:
            # Create new spreadsheet
            spreadsheet_body = {
                'properties': {
                    'title': title
                },
                'sheets': [
                    {
                        'properties': {
                            'title': 'SWOT Analysis',
                            'gridProperties': {
                                'rowCount': 50,
                                'columnCount': 10
                            }
                        }
                    }
                ]
            }
            
            spreadsheet = self.service.spreadsheets().create(
                body=spreadsheet_body
            ).execute()
            
            spreadsheet_id = spreadsheet['spreadsheetId']
            
            # Populate with SWOT data
            await self._populate_swot_data(spreadsheet_id, swot_data)
            
            return {
                "status": "success",
                "spreadsheet_id": spreadsheet_id,
                "spreadsheet_url": f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}",
                "title": title
            }
            
        except HttpError as e:
            return {
                "status": "error",
                "error_message": f"Google Sheets API error: {e}"
            }
        except Exception as e:
            return {
                "status": "error", 
                "error_message": f"Failed to create spreadsheet: {e}"
            }
    
    async def _populate_swot_data(self, spreadsheet_id: str, swot_data: Dict[str, Any]):
        """Populate spreadsheet with SWOT analysis data."""
        
        # Prepare SWOT matrix data
        values = [
            ["SWOT Analysis Matrix", "", "", ""],
            ["", "", "", ""],
            ["STRENGTHS", "", "OPPORTUNITIES", ""],
            ["", "", "", ""]
        ]
        
        # Add strengths
        strengths = swot_data.get("swot_matrix", {}).get("strengths", [])
        for i, strength in enumerate(strengths[:5]):  # Limit to 5 items
            if i + 4 < len(values):
                values[i + 4] = [strength.get("factor", ""), strength.get("description", ""), "", ""]
            else:
                values.append([strength.get("factor", ""), strength.get("description", ""), "", ""])
        
        # Add opportunities (same row as strengths)
        opportunities = swot_data.get("swot_matrix", {}).get("opportunities", [])
        for i, opportunity in enumerate(opportunities[:5]):
            row_index = i + 4
            if row_index < len(values):
                values[row_index][2] = opportunity.get("factor", "")
                values[row_index][3] = opportunity.get("description", "")
        
        # Add weaknesses and threats section
        values.extend([
            ["", "", "", ""],
            ["WEAKNESSES", "", "THREATS", ""],
            ["", "", "", ""]
        ])
        
        # Add weaknesses
        weaknesses = swot_data.get("swot_matrix", {}).get("weaknesses", [])
        for weakness in weaknesses[:5]:
            values.append([weakness.get("factor", ""), weakness.get("description", ""), "", ""])
        
        # Add threats (same rows as weaknesses)
        threats = swot_data.get("swot_matrix", {}).get("threats", [])
        weakness_start = len(values) - len(weaknesses)
        for i, threat in enumerate(threats[:5]):
            row_index = weakness_start + i
            if row_index < len(values):
                values[row_index][2] = threat.get("factor", "")
                values[row_index][3] = threat.get("description", "")
        
        # Update spreadsheet
        range_name = 'SWOT Analysis!A1'
        body = {
            'values': values
        }
        
        self.service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            valueInputOption='RAW',
            body=body
        ).execute()
        
        # Format the spreadsheet
        await self._format_swot_spreadsheet(spreadsheet_id)
    
    async def _format_swot_spreadsheet(self, spreadsheet_id: str):
        """Apply formatting to the SWOT spreadsheet."""
        
        requests = [
            # Header formatting
            {
                "repeatCell": {
                    "range": {
                        "sheetId": 0,
                        "startRowIndex": 0,
                        "endRowIndex": 1,
                        "startColumnIndex": 0,
                        "endColumnIndex": 4
                    },
                    "cell": {
                        "userEnteredFormat": {
                            "backgroundColor": {"red": 0.2, "green": 0.6, "blue": 0.9},
                            "textFormat": {"bold": True, "foregroundColor": {"red": 1, "green": 1, "blue": 1}}
                        }
                    },
                    "fields": "userEnteredFormat(backgroundColor,textFormat)"
                }
            },
            # SWOT section headers
            {
                "repeatCell": {
                    "range": {
                        "sheetId": 0,
                        "startRowIndex": 2,
                        "endRowIndex": 3,
                        "startColumnIndex": 0,
                        "endColumnIndex": 4
                    },
                    "cell": {
                        "userEnteredFormat": {
                            "backgroundColor": {"red": 0.9, "green": 0.9, "blue": 0.9},
                            "textFormat": {"bold": True}
                        }
                    },
                    "fields": "userEnteredFormat(backgroundColor,textFormat)"
                }
            }
        ]
        
        batch_update_request = {"requests": requests}
        
        self.service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body=batch_update_request
        ).execute()


def create_google_sheets_client() -> GoogleSheetsClient:
    """Factory function to create Google Sheets client."""
    return GoogleSheetsClient()