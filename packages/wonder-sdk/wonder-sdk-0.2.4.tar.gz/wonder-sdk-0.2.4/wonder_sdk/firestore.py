from logging import Logger
from threading import Thread
from google.cloud import firestore

# GET OPERATION
def get_data(client, collection_name, document_name, logger):
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

    doc = client.collection(collection_name).document(document_name).get()
    if doc.exists:
        logger.info(f"Document '{document_name}' retrieved successfully.")
        return doc.to_dict()
    else:
        logger.error(f"Document '{document_name}' does not exist in collection '{collection_name}'.")
        raise Exception(f"Document '{document_name}' does not exist in collection '{collection_name}'.")

# SET OPERATION
def _set(client: firestore.Client, collection_name: str, data: object, logger: Logger, document_name=None) -> str:
    doc_ref = None
    doc_name = None
    if document_name:
        doc_ref = client.collection(collection_name).document(document_name)
        doc_name = document_name
    else:
        doc_ref = client.collection(collection_name).document()
        doc_name = doc_ref.id  # Retrieve the auto-generated document ID
    logger.info(f"Setting data in collection '{collection_name}', document '{doc_name}'.")
    doc_ref.set(data)
    logger.info(f"Data set in collection '{collection_name}', document '{doc_name}'.")
    return document_name

def set_data(client, data, collection_name, logger, document_name=None, on_thread=False) -> Thread or str:
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

    if on_thread:
        logger.info("Set operation is starting on a separate thread.")
        t = Thread(target=_set, args=[client, collection_name, data, logger, document_name])
        t.start()
        return t
    else:
        doc_id = _set(client, collection_name, data, logger, document_name)
        return doc_id


# UPDATE OPERATION
def _update(client: firestore.Client, collection_name: str, document_name: str, data: object, logger: Logger) -> None:
    logger.info(f"Updating document '{document_name}' in collection '{collection_name}'.")
    doc_ref = client.collection(collection_name).document(document_name)
    doc_snapshot = doc_ref.get()
    if doc_snapshot.exists:
        doc_ref.update(data)
        logger.info(f"Updated document '{document_name}' in collection '{collection_name}'.")
    else:
        logger.error(f"Update failed. Document '{document_name}' does not exist in collection '{collection_name}'.")
        raise Exception(f"Update failed. Document '{document_name}' does not exist in collection '{collection_name}'.")

def update_data(client, document_name, data, collection_name, logger, on_thread=False) -> Thread or None:
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

    if on_thread:
        logger.info("Update operation is starting on a separate thread.")
        t = Thread(target=_update, args=[client, collection_name, document_name, data, logger])
        t.start()
        return t
    else:
        _update(client, collection_name, document_name, data, logger)
        return None