import os
import argparse
import sys

from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from oauth2client.service_account import ServiceAccountCredentials


def get_service(api_name, api_version, scopes, key_file_location):
    """Get a service that communicates to a Google API.

    Args:
        api_name: The name of the api to connect to.
        api_version: The api version to connect to.
        scopes: A list auth scopes to authorize for the application.
        key_file_location: The path to a valid service account JSON key file.

    Returns:
        A service that is connected to the specified API.
    """

    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        key_file_location, scopes=scopes)

    # Build the service object.
    service = build(api_name, api_version, credentials=credentials)
    return service


def get_mime_type(service, drive_id):
    return service.files().get(fileId=drive_id,
                               fields='mimeType').execute().get('mimeType', None)


def exit_if_not_folder(service, drive_id):
    mime_type = get_mime_type(service, drive_id)
    if mime_type != 'application/vnd.google-apps.folder':
        print(f'Drive id should be a folder to perform this action! Actual type {mime_type}', file=sys.stderr)
        exit(1)


def list_dir(service, drive_folder_id):
    exit_if_not_folder(service, drive_folder_id)
    results = service.files().list(
        pageSize=10, fields="nextPageToken, files(id, name)",
        q=f"'{drive_folder_id}' in parents and trashed=false").execute()
    items = results.get('files', [])

    if not items:
        print('No files found.')
    else:
        print('Files:')
        for item in items:
            print(u'{0} ({1})'.format(item['name'], item['id']))


def delete_callback(request_id, response, exception):
    if exception:
        print(exception)


def clean_dir(service, drive_folder_id):
    exit_if_not_folder(service, drive_folder_id)

    file_ids = service.files().list(
        pageSize=10, fields="nextPageToken, files(id)",
        q=f"'{drive_folder_id}' in parents").execute().get('files', [])

    batch = service.new_batch_http_request(callback=delete_callback)

    for item in file_ids:
        print(item['id'])
        batch.add(service.files().delete(fileId=item['id']))

    batch.execute()


def upload_file(service, drive_folder_id, file_path):
    exit_if_not_folder(service, drive_folder_id)

    file_metadata = {'name': os.path.basename(file_path),
                     'parents': [drive_folder_id]}
    media = MediaFileUpload(file_path,
                            resumable=True)

    file = service.files().create(body=file_metadata,
                                  media_body=media,
                                  fields='id').execute()

    print(f"Successfully uploaded file '{file.get('id')}'")


def delete_file(service, drive_id):
    service.files().delete(fileId=drive_id).execute()


def main():
    actions = {
        'upload': lambda args: upload_file(service, args.drive_id, args.file),
        'list_dir': lambda args: list_dir(service, args.drive_id),
        'clean_dir': lambda args: clean_dir(service, args.drive_id),
        'delete': lambda args: delete_file(service, args.drive_id)
    }

    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=actions.keys(),
                        help="Google Drive action to perform: upload, list_dir, clean_dir")
    parser.add_argument('-c', '--credentials', required=True,
                        help='Path to the Google service account credential JSON file')
    parser.add_argument('-id', '--drive-id',  help='Drive file/folder id for operations', default='root')
    parser.add_argument('-f', '--file', help='Path to local file for upload')
    params = parser.parse_args()

    service = get_service(
        api_name='drive',
        api_version='v3',
        scopes=['https://www.googleapis.com/auth/drive'],
        key_file_location=params.credentials)

    actions[params.action](params)


if __name__ == '__main__':
    main()
