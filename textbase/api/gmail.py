import pickle
from pathlib import Path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def load_service():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    pickle_file = (Path.home() / 'dev' / 'libs' / 'libgmail' / 'token.pickle')
    if Path.exists(pickle_file):
        with open(pickle_file.as_posix(), 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                (Path.home() / 'dev' / 'libs' / 'libgmail' / 'credentials.json').as_posix(), SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(pickle_file.as_posix(), 'wb') as token:
            pickle.dump(creds, token)

    return build('gmail', 'v1', credentials=creds)


service = load_service()
results = service.users().labels().list(userId='me').execute()
results = service.users().drafts().list(userId='me').execute()
results = service.users().messages().list(userId='me').execute()

labels = results.get('labels', [])

if not labels:
    print('No labels found.')
else:
    print('Labels:')
    for label in labels:
        print(label['name'])
