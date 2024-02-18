from .app import initialize_app
from .config import WonderSdkConfig
from .health import start_health_check
from .logger import setup_logger
from .threading import initialize_threading
from .firestore import get_data, set_data, update_data
from .translation import translate
from .storage import upload_to_bucket, download_from_bucket, upload_results_and_update_db_async
from .pubsub import subscribe_to_pubsub

class WonderSdk:
    def __init__(self, config: WonderSdkConfig, app_credentials=None):
        self._config = config

        start_health_check()
        self.logger = setup_logger()
        initialize_threading(self.logger)
        self.app = initialize_app(config.project_id, app_credentials)


    # ENVIRONMENT VARIABLE GETTERS
    def get_process_count(self):
        """
        Returns:
            int: The configured number of processes to be used by the SDK.
        """
        return self._config.process_count

    def get_subscription_name(self):
        """
        Returns:
            str: The subscription name from the SDK configuration.
        """
        return self._config.subscription_name

    def get_environment(self):
        """
        Returns:
            str: The current deployment environment (staging, production) from the SDK configuration.
        """
        return self._config.environment

    def get_collection_name(self):
        """
        Returns:
            str: The data collection name (e.g., database table) from the SDK configuration, specifying where data should be stored or retrieved.
        """
        return self._config.collection_name

    def get_project_id(self):
        """
        Returns:
            str: The project ID from the SDK configuration.
        """
        return self._config.project_id


    # FIRESTORE
    def get_firestore_client(self):
        """
        Returns:
            firestor.client: The Firestore database client from the app configuration.
        """
        return self.app.db_client

    def get_firestore_data(self, document_name, collection_name=None):
        """
        Retrieves a document from a Firestore collection.

        Args:
            document_name (str): The name of the document to retrieve.
            collection_name (str, optional): The name of the collection. Defaults to SDK's configured collection name.

        Returns:
            dict: A dictionary containing the data from the Firestore document.

        Raises:
            ValueError: If any of the input parameters are invalid.
            Exception: If the specified document does not exist in the collection.
        """
        collection_name = collection_name if collection_name else self.get_collection_name()
        return get_data(client=self.app.db_client, collection_name=collection_name, document_name=document_name, logger=self.logger)

    def set_firestore_data(self, data, document_name=None, collection_name=None, on_thread=False):
        """
        Sets data in a Firestore document, optionally using a separate thread. If the document name is not provided, a new document is created, and its ID is returned.

        Args:
            data (dict): Data to set in the document.
            document_name (str, optional): The name of the document to set data for. If None, a new document is created.
            collection_name (str, optional): The name of the collection. Defaults to SDK's configured collection name.
            on_thread (bool, optional): Whether to perform the operation on a separate thread. Defaults to False.

        Returns:
            Thread or str: The Thread object if `on_thread` is True, the document ID if a new document is created.

        Raises:
            ValueError: If any of the input parameters are invalid.
        """
        collection_name = collection_name if collection_name else self.get_collection_name()
        return set_data(client=self.app.db_client, data=data, collection_name=collection_name, logger=self.logger, document_name=document_name, on_thread=on_thread)

    def update_firestore_data(self, document_name, data, collection_name=None, on_thread=False):
        """
        Updates data in a Firestore document, optionally using a separate thread.

        This function updates the data for a specified document in a Firestore collection. If the
        document does not exist, it raises an exception. This operation can run either synchronously
        or in a new thread. When run in a new thread, it starts the thread and returns the Thread object.

        Args:
            document_name (str): The name of the document to update.
            data (dict): Data to update in the document.
            collection_name (str, optional): The name of the collection. Defaults to SDK's configured collection name.
            on_thread (bool, optional): Whether to perform the operation on a separate thread.

        Returns:
            Thread or None: The Thread object if `on_thread` is True; otherwise, None.

        Raises:
            Exception: If the specified document does not exist in the collection.
        """
        collection_name = collection_name if collection_name else self.get_collection_name()
        return update_data(client=self.app.db_client, document_name=document_name, data=data, collection_name=collection_name, logger=self.logger, on_thread=on_thread)


    # PUB/SUB
    def subscribe_to_pubsub(self, callback, max_messages=None, timeout=None):
        """
        Subscribes to a Pub/Sub topic with a specified callback function.

        This function sets up a subscriber client to listen to messages on a specified subscription
        within a Google Cloud Pub/Sub project. It applies flow control settings based on the maximum
        number of messages and optionally applies a timeout for the subscription to listen.

        Args:
            callback (Callable): The callback function to execute when a message is received.
            max_messages (int, optional): The maximum number of messages to process. Defaults to SDK's configured process count.
            timeout (int, optional): The timeout for the subscription in seconds.

        Note:
            This method does not return a value but configures the subscription.

        Raises:
            ValueError: If any of the input parameters are invalid.
            Exception: For errors during the subscription process.
        """
        max_messages = max_messages if max_messages else self.get_process_count()
        subscribe_to_pubsub(client=self.app.ps_client, logger=self.logger, project_id=self.get_project_id(), subscription_name=self.get_subscription_name(),
                            callback=callback, max_messages=max_messages, timeout=timeout)


    # TRANSLATION
    def get_translation_client(self):
        """
        Returns:
            translate_v2.client: The translation client from the app configuration.
        """
        return self.app.tr_client

    def translate_text(self, text, target_language='en'):
        """
        Translates text into the specified language.

        Args:
            text (str): The text to translate.
            target_language (str, optional): The target language code. Defaults to 'en'.

        Returns:
            str: The translated text.

        Raises:
            ValueError: If any of the input parameters are invalid.
            Exception: If the translation process fails.
        """
        return translate(client=self.app.tr_client, text=text, target_language=target_language, logger=self.logger)


    # STORAGE
    def get_storage_client(self):
        """
        Returns:
            storage.client: The storage client from the app configuration.
        """
        return self.app.st_client

    def upload_to_bucket(self, bucket_name, destination_blob_name, source_file_path=None, source_file=None, source_string=None, on_thread=False):
        """
        Uploads a file, file object, or string to a Google Cloud Storage bucket, optionally using a separate thread.

        Args:
            bucket_name (str): The name of the bucket to upload to.
            destination_blob_name (str): The destination blob name in the bucket.
            source_file_path (str, optional): Path to the source file to upload.
            source_file (File, optional): Source file object to upload.
            source_string (str, optional): String content to upload.
            on_thread (bool, optional): Whether to perform the operation on a separate thread.

        Returns:
            Thread or None: The Thread object if `on_thread` is True, otherwise None.

        Raises:
            ValueError: If any of the input parameters are invalid.
            Exception: If the upload process fails.
        """
        return upload_to_bucket(client=self.app.st_client, logger=self.logger, bucket_name=bucket_name, destination_blob_name=destination_blob_name,
                                source_file_path=source_file_path, source_file=source_file, source_string=source_string, on_thread=on_thread)

    def download_from_bucket(self, bucket_name, source_blob_name,
                             destination_file_path=None,
                             download_as_file_to_filename=False,
                             download_as_text=False,
                             download_as_bytes=False,
                             download_as_string=False,
                             on_thread=False):
        """
       Downloads a blob from Google Cloud Storage to a specified destination, optionally using a seperate thread.

        Args:
            bucket_name (str): The name of the bucket to download from.
            source_blob_name (str): The name of the source blob in the bucket.
            destination_file_path (str, optional): Path to save the downloaded file.
            download_as_file_to_filename (bool, optional): Whether to download directly to a file specified by filename.
            download_as_text (bool, optional): Whether to download the data as text.
            download_as_bytes (bool, optional): Whether to download the data as bytes.
            download_as_string (bool, optional): Whether to download the data as a string.
            on_thread (bool, optional): Whether to perform the operation on a separate thread.

        Returns:
            Thread, str, or bytes: Depending on the download type and threading option.
            - If the download type is file, the function returns a Thread object if `on_thread` is True; otherwise, str (destination file name).
            - If the download type is text, bytes, or string, the function returns a Thread object if `on_thread` is True; otherwise, str, bytes, or str, respectively.

        Raises:
            ValueError: For invalid inputs.
            Exception: For errors during the download process.
        """
        return download_from_bucket(client=self.app.st_client, logger=self.logger, bucket_name=bucket_name, source_blob_name=source_blob_name,
                                    destination_file_path=destination_file_path,
                                    download_as_file_to_filename=download_as_file_to_filename,
                                    download_as_text=download_as_text,
                                    download_as_bytes=download_as_bytes,
                                    download_as_string=download_as_string,
                                    on_thread=on_thread)


    # TASK UTILS, NOT GENERIC
    def upload_results_and_update_db(self, bucket_name, destinations, images, document_name, data, collection_name=None):
        """
        Uploads images to a specified Google Cloud Storage bucket and updates a document in a Firestore collection.
        This operation is performed in a separate thread.

        Args:
            bucket_name (str): The name of the bucket where images will be uploaded.
            destinations ([str]): A list of destination blob names in the bucket for each image.
            images ([Image]): A list of image objects to be uploaded.
            document_name (str): The name of the document to update in the Firestore collection.
            data (dict): The data to update in the document.
            collection_name (str): The name of the Firestore collection containing the document.

        Returns:
            Thread: The Thread object for the operation.

        Raises:
            ValueError: If any input parameters are invalid.
        """
        collection_name = collection_name if collection_name else self.get_collection_name()
        return upload_results_and_update_db_async(st_client=self.app.st_client, db_client=self.app.db_client, logger=self.logger,
            bucket_name=bucket_name, destinations=destinations, images=images,
            document_name=document_name, data=data, collection_name=collection_name)