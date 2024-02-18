import io
from logging import Logger
from threading import Thread
from google.cloud import storage, firestore
from PIL import Image

def upload_to_bucket(client, logger, bucket_name, destination_blob_name, source_file_path=None, source_file=None, source_string=None, on_thread=False) -> Thread or None:
    """
    Uploads a file, file object, or string to a Google Cloud Storage bucket, optionally using a separate thread.

    This function uploads data to a specified blob in a Google Cloud Storage bucket. The data can be provided as a file path,
    a file object, or a string. The upload can be performed either synchronously or in a new thread.

    Args:
        client (Storage Client): The Google Cloud Storage client used to interact with the bucket.
        logger (Logger): The logger to use for logging.
        bucket_name (str): The name of the bucket to which the data is uploaded.
        destination_blob_name (str): The name of the destination blob in the bucket.
        source_file_path (str, optional): The path of the file to upload.
        source_file (File, optional): The file object to upload.
        source_string (str, optional): The string data to upload.
        on_thread (bool, optional): Whether to run this operation in a new thread. Defaults to False.

    Returns:
        Thread or None: The Thread object if `on_thread` is True, otherwise None.

    Raises:
        ValueError: If any of the input parameters are invalid.
        Exception: If the upload process fails.
    """
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

    logger.info(f"Uploading file to '{destination_blob_name}' in bucket '{bucket_name}'.")

    def upload(bucket_name, destination_blob_name, source_file_path, source_file, source_string):
        try:
            bucket = client.bucket(bucket_name)
            blob = bucket.blob(destination_blob_name)
            if source_file_path:
                blob.upload_from_filename(source_file_path)
            elif source_file:
                blob.upload_from_file(source_file)
            elif source_string:
                blob.upload_from_string(source_string)
            else:
                raise ValueError("No data provided for upload.")
            logger.info(f"File uploaded to '{destination_blob_name}' in bucket '{bucket_name}'.")
        except Exception as e:
            logger.exception("Exception occurred during the upload process.")
            raise e

    if on_thread:
        t = Thread(target=upload, args=[bucket_name, destination_blob_name, source_file_path, source_file, source_string])
        t.start()
        logger.info("Upload operation started on a separate thread.")
        return t
    else:
        upload(bucket_name, destination_blob_name, source_file_path, source_file, source_string)
        logger.info("Upload operation completed.")
        return None

def download_from_bucket(client, logger, bucket_name, source_blob_name,
                         destination_file_path=None,
                         download_as_file_to_filename=False,
                         download_as_text=False,
                         download_as_bytes=False,
                         download_as_string=False,
                         on_thread=False) -> Thread or str or bytes:
    """
    Downloads a blob from Google Cloud Storage to a specified destination, optionally using a seperate thread.

    This function supports downloading the data in various formats: directly to a file, as text, as bytes,
    or as a string. The operation can be executed synchronously or in a separate thread.

    Args:
        client (storage.Client): The Google Cloud Storage client.
        logger (Logger): Logger object for logging.
        bucket_name (str): Name of the bucket.
        source_blob_name (str): Name of the blob to download.
        destination_file_path (str, optional): Destination file path for downloads.
        download_as_file_to_filename (bool, optional): If True, download directly to a file.
        download_as_text (bool, optional): If True, return the content as text.
        download_as_bytes (bool, optional): If True, return the content as bytes.
        download_as_string (bool, optional): If True, return the content as a string.
        on_thread (bool, optional): If True, perform the download in a separate thread.

    Returns:
        Thread, str, or bytes: Depending on the download type and threading option.
        - If the download type is file, the function returns a Thread object if `on_thread` is True; otherwise, str (destination file name).
        - If the download type is text, bytes, or string, the function returns a Thread object if `on_thread` is True; otherwise, str, bytes, or str, respectively.

    Raises:
        ValueError: For invalid inputs.
        Exception: For errors during the download process.
    """
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

    if download_as_file_to_filename or on_thread:
        if not destination_file_path:
            logger.error("Destination file path must be specified when downloading as a file or on a separate thread.")
            raise ValueError("Destination file path must be specified when downloading as a file or on a separate thread.")

    logger.info(f"Downloading blob '{source_blob_name}' from bucket '{bucket_name}'.")

    def download(bucket_name, source_blob_name, destination_file_path: str, file, text, bytes, string, on_thread) -> str or bytes:
        try:
            bucket = client.bucket(bucket_name)
            blob = bucket.blob(source_blob_name)
            if file:
                blob.download_to_filename(destination_file_path)
                return destination_file_path
            elif text:
                content = blob.download_as_text()
                if on_thread:
                    with open(destination_file_path, 'w') as file:
                        file.write(content)
                else:
                    return content
            elif bytes:
                content = blob.download_as_bytes()
                if on_thread:
                    with open(destination_file_path, 'wb') as file:
                        file.write(content)
                else:
                    return content
            elif string:
                content = blob.download_as_string()
                if on_thread:
                    with open(destination_file_path, 'w') as file:
                        file.write(content.decode('utf-8'))
                else:
                    return content.decode('utf-8')
            else:
                raise ValueError("No download type provided.")
            logger.info(f"Blob '{source_blob_name}' downloaded successfully to '{destination_file_path}'.")
        except Exception as error:
            logger.exception("Exception occurred during the download process.")
            raise error

    if on_thread:
        t = Thread(target=download, args=[bucket_name, source_blob_name, destination_file_path, download_as_file_to_filename, download_as_text, download_as_bytes, download_as_string, True])
        t.start()
        logger.info("Download operation started on a separate thread. The content will be saved to the file path provided.")
        return t
    else:
        content = download(bucket_name, source_blob_name, destination_file_path, download_as_file_to_filename, download_as_text, download_as_bytes, download_as_string, False)
        logger.info("Download operation completed. The content is returned.")
        return content

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