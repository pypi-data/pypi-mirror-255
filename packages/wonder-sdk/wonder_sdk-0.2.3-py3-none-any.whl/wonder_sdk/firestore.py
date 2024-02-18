from logging import Logger
from threading import Thread
from google.cloud import firestore

def get_data(client, collection_name, document_name, logger):
    """
    Retrieves a document from a Firestore collection.

    Given a Firestore client, the name of a document, and the name of the collection it belongs to,
    this function fetches the document. If the document exists, it returns its contents as a dictionary.
    If the document does not exist, it raises an exception.

    Args:
        client (Firestore Client): The Firestore client used to interact with the database.
        document_name (str): The name of the document to retrieve.
        collection_name (str): The name of the collection where the document is stored.
        logger (Logger): The logger to use for logging.

    Returns:
        dict: A dictionary containing the data from the Firestore document.

    Raises:
        ValueError: If any of the input parameters are invalid.
        Exception: If the specified document does not exist in the collection.
    """
    if not isinstance(logger, Logger):
        raise ValueError("Logger must be a Logger object.")
    if not isinstance(client, firestore.Client):
        logger.error("Invalid client type provided.")
        raise ValueError("Client must be a Firestore Client.")
    if not isinstance(document_name, str) or not document_name:
        logger.error("Invalid document name provided.")
        raise ValueError("Document name must be a non-empty string.")
    if not isinstance(collection_name, str) or not collection_name:
        logger.error("Invalid collection name provided.")
        raise ValueError("Collection name must be a non-empty string.")

    logger.info(f"Retrieving document '{document_name}' from collection '{collection_name}'.")

    try:
        doc = client.collection(collection_name).document(document_name).get()
        if doc.exists:
            logger.info(f"Document '{document_name}' retrieved successfully.")
            return doc.to_dict()
        else:
            logger.error(f"Document '{document_name}' does not exist in collection '{collection_name}'.")
            raise Exception(f"Document '{document_name}' does not exist in collection '{collection_name}'.")
    except Exception as e:
        logger.exception("Exception occurred in get_data function.")
        raise e

def set_data(client, data, collection_name, logger, document_name=None, on_thread=False) -> Thread or str:
    """
    Sets data in a Firestore document, optionally using a separate thread. If the document name
    is not provided, a new document is created, and its ID is returned.

    Args:
        client (Firestore Client): The Firestore client used to interact with the database.
        data (dict): The data to set in the document.
        collection_name (str): The name of the collection where the document is stored.
        logger (Logger): The logger to use for logging.
        document_name (str, optional): The name of the document to set the data for. If None, a new document is created.
        on_thread (bool, optional): Whether to run this operation in a new thread. Defaults to False.

    Returns:
        Thread or str: The Thread object if `on_thread` is True, the document ID if a new document is created.

    Raises:
        ValueError: If any of the input parameters are invalid.
    """
    if not isinstance(logger, Logger):
        raise ValueError("Logger must be a Logger object.")
    if not isinstance(client, firestore.Client):
        logger.error("Invalid client type provided.")
        raise ValueError("Client must be a Firestore Client.")
    if not isinstance(data, dict) or not data:
        logger.error("Invalid data provided.")
        raise ValueError("Data must be a non-empty dictionary.")
    if not isinstance(collection_name, str) or not collection_name:
        logger.error("Invalid collection name provided.")
        raise ValueError("Collection name must be a non-empty string.")
    if document_name is not None and not isinstance(document_name, str):
        logger.error("Invalid document name provided.")
        raise ValueError("Document name must be a string.")
    if not isinstance(on_thread, bool):
        logger.error("Invalid on_thread value provided.")
        raise ValueError("on_thread must be a boolean.")

    logger.info(f"Setting data in collection '{collection_name}', document '{document_name}'.")

    def set_data_(collection, data_, doc=None):
        try:
            if doc:
                doc_ref = client.collection(collection).document(doc)
            else:
                doc_ref = client.collection(collection).document()
                doc = doc_ref.id  # Retrieve the auto-generated document ID
            doc_ref.set(data_)
            logger.info(f"Data set in collection '{collection}', document '{doc}'.")
            return doc
        except Exception as e:
            logger.exception("Exception occurred in set_data_ function.")
            raise e

    if on_thread:
        t = Thread(target=set_data_, args=[collection_name, data, document_name])
        t.start()
        logger.info("Set operation started on a separate thread.")
        return t
    else:
        doc_id = set_data_(collection_name, data, document_name)
        logger.info("Set operation completed.")
        return doc_id

def update_data(client, document_name, data, collection_name, logger, on_thread=False) -> Thread or None:
    """
    Updates data in a Firestore document, optionally using a separate thread.

    This function updates the data for a specified document in a Firestore collection. If the
    document does not exist, it raises an exception. This operation can run either synchronously
    or in a new thread. When run in a new thread, it starts the thread and returns the Thread object.

    Args:
        client (Firestore Client): The Firestore client used to interact with the database.
        document_name (str): The name of the document to update.
        data (dict): The data to update in the document.
        collection_name (str): The name of the collection where the document is stored.
        logger (Logger): The logger to use for logging.
        on_thread (bool, optional): Whether to run this operation in a new thread. Defaults to False.

    Returns:
        Thread or None: The Thread object if `on_thread` is True; otherwise, None.

    Raises:
        Exception: If the specified document does not exist in the collection.
    """
    if not isinstance(logger, Logger):
        raise ValueError("Logger must be a Logger object.")
    if not isinstance(client, firestore.Client):
        logger.error("Invalid client type provided.")
        raise ValueError("Client must be a Firestore Client.")
    if not isinstance(document_name, str) or not document_name:
        logger.error("Invalid document name provided.")
        raise ValueError("Document name must be a non-empty string.")
    if not isinstance(data, dict) or not data:
        logger.error("Invalid data provided.")
        raise ValueError("Data must be a non-empty dictionary.")
    if not isinstance(collection_name, str) or not collection_name:
        logger.error("Invalid collection name provided.")
        raise ValueError("Collection name must be a non-empty string.")
    if not isinstance(on_thread, bool):
        logger.error("Invalid on_thread value provided.")
        raise ValueError("on_thread must be a boolean.")

    logger.info(f"Updating document '{document_name}' in collection '{collection_name}'.")

    def update_data_(collection, doc, data_):
        try:
            doc_ref = client.collection(collection).document(doc)
            doc_snapshot = doc_ref.get()
            if doc_snapshot.exists:
                doc_ref.update(data_)
                logger.info(f"Successfully updated document '{doc}' in collection '{collection}'.")
            else:
                logger.error(f"Document '{doc}' does not exist in collection '{collection}'.")
                raise Exception(f"Document '{doc}' does not exist in collection '{collection}'.")
        except Exception as e:
            logger.exception("Exception occurred in update_data_ function.")
            raise e

    if on_thread:
        t = Thread(target=update_data_, args=[collection_name, document_name, data])
        t.start()
        logger.info("Update operation started on a separate thread.")
        return t
    else:
        update_data_(collection_name, document_name, data)
        logger.info("Update operation completed.")
        return None