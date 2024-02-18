import io
from logging import Logger
from threading import Thread
from google.cloud import storage, firestore
from PIL import Image

# UPLOAD OPERATION
def _upload(client: storage.Client, logger: Logger, bucket_name: str, destination_blob_name: str, source_file_path=None, source_file=None, source_string=None):
    logger.info(f"Uploading file to '{destination_blob_name}' in bucket '{bucket_name}'.")
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    if source_file_path:
        blob.upload_from_filename(source_file_path)
    elif source_file:
        blob.upload_from_file(source_file)
    elif source_string:
        blob.upload_from_string(source_string)
    else:
        raise ValueError("No source provided for upload.")
    logger.info(f"File uploaded to '{destination_blob_name}' in bucket '{bucket_name}'.")

def upload_to_bucket(client, logger, bucket_name, destination_blob_name, source_file_path=None, source_file=None, source_string=None, on_thread=False) -> Thread or None:
    if not isinstance(logger, Logger):
        raise ValueError("Logger must be a Logger object.")
    if not isinstance(client, storage.Client):
        logger.error("Invalid storage client type provided.")
        raise ValueError("Client must be a Google Cloud Storage Client.")
    if not isinstance(bucket_name, str) or not bucket_name:
        logger.error("Invalid bucket name provided.")
        raise ValueError("Bucket name must be a non-empty string.")
    if not isinstance(destination_blob_name, str) or not destination_blob_name:
        logger.error("Invalid destination blob name provided.")
        raise ValueError("Destination blob name must be a non-empty string.")
    if not isinstance(on_thread, bool):
        logger.error("Invalid on_thread value provided.")
        raise ValueError("on_thread must be a boolean.")

    if on_thread:
        logger.info("Upload operation is starting on a separate thread.")
        t = Thread(target=_upload, args=[client, logger, bucket_name, destination_blob_name, source_file_path, source_file, source_string])
        t.start()
        return t
    else:
        _upload(client, logger, bucket_name, destination_blob_name, source_file_path, source_file, source_string)
        return None

# DOWNLOAD OPERATION
def _download(client: storage.Client, logger: Logger, bucket_name: str, source_blob_name: str,
              filename=None, to_filename=False, as_bytes=False, as_text=False, on_thread=False):
    logger.info(f"Downloading blob '{source_blob_name}' from bucket '{bucket_name}'.")
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)

    filename = filename or source_blob_name

    if to_filename:
        logger.info(f"Downloading to filename '{filename}'. Seperate thread: {on_thread}")
        blob.download_to_filename(filename)
        return filename

    if as_bytes:
        if on_thread:
            logger.info(f"Downloading as bytes on a separate thread. The content will be saved to {filename}.")
            content = blob.download_as_bytes()
            with open(filename, 'wb') as file:
                file.write(content)
                return
        else:
            logger.info("Downloading as bytes.")
            content = blob.download_as_bytes()
            return content

    if as_text:
        if on_thread:
            logger.info(f"Downloading as text on a separate thread. The content will be saved to {filename}.")
            content = blob.download_as_text()
            with open(filename, 'w') as file:
                file.write(content)
                return
        else:
            logger.info("Downloading as text.")
            content = blob.download_as_text()
            return content

def download_from_bucket(client, logger, bucket_name, source_blob_name, destination_file_path=None,
                         download_to_filename=False, download_as_text=False, download_as_bytes=False, on_thread=False) -> Thread or str or bytes:
    if not isinstance(logger, Logger):
        raise ValueError("Logger must be a Logger object.")
    if not isinstance(client, storage.Client):
        logger.error("Invalid storage client type provided.")
        raise ValueError("Client must be a Google Cloud Storage Client.")
    if not isinstance(bucket_name, str) or not bucket_name:
        logger.error("Invalid bucket name provided.")
        raise ValueError("Bucket name must be a non-empty string.")
    if not isinstance(source_blob_name, str) or not source_blob_name:
        logger.error("Invalid source blob name provided.")
        raise ValueError("Source blob name must be a non-empty string.")
    if not isinstance(on_thread, bool):
        logger.error("Invalid on_thread value provided.")
        raise ValueError("on_thread must be a boolean.")
    if destination_file_path is not None and not isinstance(destination_file_path, str):
        logger.error("Invalid destination file path provided.")
        raise ValueError("Destination file path must be a string when specified.")

    if on_thread:
        t = Thread(target=_download, args=[client, logger, bucket_name, source_blob_name, destination_file_path, download_to_filename, download_as_bytes, download_as_text, on_thread])
        t.start()
        return t
    else:
        content = _download(client, logger, bucket_name, source_blob_name, destination_file_path, download_to_filename, download_as_bytes, download_as_text, on_thread)
        logger.info("Download operation completed. The content is returned.")
        return content

# UPLOAD AND UPDATE OPERATION
def upload_results_and_update_db_async(st_client, db_client, logger, bucket_name, destinations, images, document_name, data, collection_name):
    """
    Uploads images to a specified Google Cloud Storage bucket and updates a document in a Firestore collection.
    This operation is performed in a separate thread.

    Args:
        st_client (storage.Client): The Google Cloud Storage client used to interact with the bucket.
        db_client (firestore.Client): The Firestore client used to interact with the database.
        logger (Logger): The logger to use for logging operations.
        bucket_name (str): The name of the bucket where images will be uploaded.
        destinations ([str]): A list of destination blob names in the bucket for each image.
        images ([Image]): A list of image objects to be uploaded.
        document_name (str): The name of the document to update in the Firestore collection.
        data (dict): The data to update in the document.
        collection_name (str): The name of the Firestore collection containing the document.

    Returns:
        Thread: The thread object in which the upload and update operations are performed.

    Raises:
        ValueError: If any input parameters are invalid.
    """
    if not isinstance(st_client, storage.Client):
        raise ValueError("st_client must be an instance of google.cloud.storage.Client")
    if not isinstance(db_client, firestore.Client):
        raise ValueError("db_client must be an instance of google.cloud.firestore.Client")
    if not isinstance(logger, Logger):
        raise ValueError("logger must be an instance of logging.Logger")
    if not isinstance(bucket_name, str) or not bucket_name:
        raise ValueError("bucket_name must be a non-empty string")
    if not isinstance(destinations, list) or not all(isinstance(d, str) for d in destinations):
        raise ValueError("destinations must be a list of non-empty strings")
    if not isinstance(images, list) or not all(isinstance(img, Image.Image) for img in images):
        raise ValueError("images must be a list of PIL.Image.Image objects")
    if not isinstance(document_name, str) or not document_name:
        raise ValueError("document_name must be a non-empty string")
    if not isinstance(data, dict):
        raise ValueError("data must be a dictionary")
    if not isinstance(collection_name, str) or not collection_name:
        raise ValueError("collection_name must be a non-empty string")

    if len(images) != len(destinations):
        raise ValueError("The number of images and destinations must match")

    def upload_and_update():
        try:
            bucket = st_client.bucket(bucket_name)
            for index, image in enumerate(images):
                blob = bucket.blob(destinations[index])
                byte_stream = io.BytesIO()
                image.save(byte_stream, format='JPEG')
                byte_stream.seek(0)
                blob.upload_from_file(byte_stream)

            doc_ref = db_client.collection(collection_name).document(document_name)
            doc_snapshot = doc_ref.get()
            if doc_snapshot.exists:
                doc_ref.update(data)
                logger.info(f"Successfully updated document '{document_name}' in collection '{collection_name}'.")
            else:
                logger.error(f"Document '{document_name}' does not exist in collection '{collection_name}'.")
                raise Exception(f"Document '{document_name}' does not exist in collection '{collection_name}'.")
        except Exception as error:
            logger.exception("Exception occurred in upload_and_update function.")
            raise error

    t = Thread(target=upload_and_update)
    t.start()
    logger.info("Upload and update operation started on a separate thread.")
    return t