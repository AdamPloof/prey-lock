"""
Connect to Google Drive API for uploading training data
"""

from __future__ import print_function

import os.path
import json
from pathlib import Path

from google.oauth2 import service_account
from googleapiclient.http import MediaFileUpload
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class Drive:
    SCOPES = ['https://www.googleapis.com/auth/drive.file']
    ROOT = os.path.dirname(os.path.abspath(__file__))

    def __init__(self) -> None:
        with open('../env.json', 'r') as env_file:
            env = json.load(env_file)

        service_file = env['SERVICE_FILENAME']
        service = os.path.join(self.ROOT, 'auth', service_file)
        credentials = service_account.Credentials.from_service_account_file(service, scopes=self.SCOPES)
        self.drive = build('drive', 'v3', credentials=credentials)
        self.training_location_id = env['TRAINING_LOCATION_ID']

    def check_file_capacity(self):
        pass

    def upload_file(self, filepath):
        test_filepath = os.path.join(self.ROOT, 'test_upload.txt')
        metadata = {
            'name': 'test_upload.txt',
            'parents': [self.training_location_id]
        }
        media = MediaFileUpload(test_filepath, 'text/plain')

        try:
            file = self.drive.files().create(
                # uploadType='media',
                body=metadata,
                media_body=media,
                fields='id'
            ).execute()
            print(f'File ID: {file.get("id")}')
        except HttpError as e:
            print(f'An error occurred: {e}')
            file = None

        return file.get('id')

def main():
    drive_bot = Drive()
    drive_bot.upload_file('')

if __name__ == '__main__':
    main()
