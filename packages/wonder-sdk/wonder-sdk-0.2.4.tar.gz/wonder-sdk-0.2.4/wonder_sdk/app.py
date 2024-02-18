import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud import storage, pubsub_v1, translate_v2

class App:
    def __init__(self) -> None:
        self.db_client = firestore.client()
        self.st_client = storage.Client()
        self.ps_client = pubsub_v1.SubscriberClient()
        self.tr_client = translate_v2.Client()

def initialize_app(project_id, app_credentials=None):
    firebase_cred = credentials.Certificate(app_credentials) if app_credentials else credentials.ApplicationDefault()
    firebase_admin.initialize_app(firebase_cred, {
        'projectId': project_id
    })

    return App()