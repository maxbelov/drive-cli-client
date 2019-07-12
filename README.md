## Simple CLI client for Google Drive API
Main purpose of this client is to provide ability to view/upload/delete files in the Google drive via CLI.
Client authenticates as a service account and acts on behalf of it. Drive of service account is a separate Drive, which is accessible only via API. So, this client allows to view/upload/delete files and directories of Service account's drive. Also, you can manage files and folders that are shared with this service account from another drives.

### Operations reference:
List files in directory:

    python client.py -c <sa_json_file_path> list_dir # defaults to root of the Drive
    python client.py -c <sa_json_file_path> list_dir -id <drive_folder_id>
 
 Delete file or folder:
 
    python client.py -c <sa_json_file_path> delete -id <drive_id>

Upload file:

    python client.py -c <sa_json_file_path> upload -f <local_file_path> # defaults to root of the Drive
    python client.py -c <sa_json_file_path> upload -f <local_file_path> -id <drive_folder_id>
    
Delete all files in directory:

    python client.py -c <sa_json_file_path> clean_dir -id <drive_folder_id>
