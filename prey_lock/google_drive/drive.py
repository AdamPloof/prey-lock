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
    DRIVE_CAPACITY = 2000 # Max number of files allowed to be stored in the drive

    def __init__(self) -> None:
        with open('../env.json', 'r') as env_file:
            env = json.load(env_file)

        self.training_location_id = env['TRAINING_LOCATION_ID']
        service_file = env['SERVICE_FILENAME']

        service = os.path.join(self.ROOT, 'auth', service_file)
        credentials = service_account.Credentials.from_service_account_file(service, scopes=self.SCOPES)
        self.drive = build('drive', 'v3', credentials=credentials)

    def over_capacity(self):
        files = self.drive.files()
        request = files.list(
            corpora='user',
            supportsAllDrives=True,
            # driveId=self.training_location_id,
            q='trashed = false',
            includeItemsFromAllDrives=True
        )
        file_cnt = 0
        while request is not None:
            res = request.execute()
            file_cnt += len(res['files'])
            request = files.list_next(request, res)

        return file_cnt <= self.DRIVE_CAPACITY


    def upload_file(self, filepath):
        if self.over_capacity():
            raise Exception('There is no room to store additional images in the selected location.')

        metadata = {
            'name': filepath,
            'parents': [self.training_location_id]
        }
        media = MediaFileUpload(filepath, 'image/jpeg')

        try:
            file = self.drive.files().create(
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
