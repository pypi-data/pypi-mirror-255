from logging import Logger
from google.cloud import pubsub_v1
from .health import set_health_to_false

def subscribe_to_pubsub(client, logger, project_id, subscription_name, callback, max_messages=None, timeout=None) -> None:
    """
    Subscribes to a Pub/Sub subscription and listens for messages, invoking a callback function.

    This function sets up a subscriber client to listen to messages on a specified subscription
    within a Google Cloud Pub/Sub project. It applies flow control settings based on the maximum
    number of messages and optionally applies a timeout for the subscription to listen.

    Args:
        client (pubsub_v1.SubscriberClient): The Pub/Sub subscriber client.
        logger (Logger): Logger object for logging.
        project_id (str): The Google Cloud project ID.
        subscription_name (str): The name of the subscription to listen to.
        callback (Callable): The callback function to process messages.
        max_messages (int, optional): The maximum number of messages to hold in memory.
        timeout (float, optional): The timeout in seconds for the subscription to listen.

    Raises:
        ValueError: If any of the input parameters are invalid.
        Exception: For errors during the subscription process.
    """
    if not isinstance(logger, Logger):
        raise ValueError("Logger must be a Logger object.")
    if not isinstance(client, pubsub_v1.SubscriberClient):
        logger.error("Invalid client type provided.")
        raise ValueError("Client must be a Pubsub Subscriber Client.")
    if not isinstance(project_id, str) or not project_id:
        logger.error("Invalid project ID provided.")
        raise ValueError("Project ID must be a non-empty string.")
    if not isinstance(subscription_name, str) or not subscription_name:
        logger.error("Invalid subscription name provided.")
        raise ValueError("Subscription name must be a non-empty string.")

    logger.info(f"Subscribing to Pub/Sub subscription '{subscription_name}' in project '{project_id}'.")

    subscription_path = client.subscription_path(project_id, subscription_name)
    flow_control = pubsub_v1.types.FlowControl(max_messages=max_messages)

    with client:
        try:
            streaming_pull_future = client.subscribe(subscription_path, callback, flow_control)
            streaming_pull_future.result(timeout=timeout)
            logger.info("Subscription to Pub/Sub completed successfully.")
        except Exception as e:
            logger.exception(f"Exception occurred while subscribing to Pub/Sub: {e}")
            streaming_pull_future.cancel()
            streaming_pull_future.result()
    set_health_to_false()