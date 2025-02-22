from utils.redis_util import RedisUtil
from utils.random_util import RandomUtil
import os
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Worker:
    """
    A class representing a worker node that consumes messages from a Redis queue.

    Attributes:
        redis (RedisUtil): An instance of RedisUtil for interacting with Redis.
        worker_id (str): A unique identifier for the worker instance.
        queue_name (str): The name of the Redis queue to consume messages from.
    """

    def __init__(self, queue_name="filenames"):
        """
        Initializes a Worker instance with a Redis connection, a unique worker ID,
        and sets the queue name.

        Args:
            queue_name (str): The name of the Redis queue to consume from. Defaults to "filenames".
        """
        self.redis = RedisUtil()
        self.worker_id = f"Worker-{RandomUtil.get_random_number()}"
        self.queue_name = queue_name
        logger.info("Worker node initialized with ID: %s", self.worker_id)

    def run(self):
        """
        Continuously consumes messages from the Redis queue and processes them.

        Args:
            None

        Returns:
            None
        """
        logger.info("Worker %s started. Waiting for messages...", self.worker_id)
        try:
            message = self.redis.pop_queue(self.queue_name)

            if message is None:
                logger.warning("Worker %s: Queue is empty. Waiting...", self.worker_id)
                return

            logger.info("Worker %s: Message processed successfully", self.worker_id)
            # Create result file
            result_folder = os.path.join(
                os.environ.get("RESULT_FOLDER"), self.worker_id
            )
            os.makedirs(result_folder, exist_ok=True)

            result_folder = os.path.join(
                result_folder,
                message["master_id"],
            )
            os.makedirs(result_folder, exist_ok=True)

            result_file = os.path.join(result_folder, message["filename"])

            with open(result_file, "w") as f:
                f.write(
                    f"Worker {self.worker_id} wrote this file at {time.time()} "
                    f"for message received at {message['timestamp']} from {message['master_id']}"
                )

            logger.info(
                "Worker %s created result file: %s", self.worker_id, result_file
            )

        except Exception as e:
            logger.error(
                "Worker %s encountered an error. Error: %s",
                self.worker_id,
                str(e),
                exc_info=True,
            )

    def start(self):
        """
        Starts the worker node and begins consuming messages from the Redis queue.
        """
        logger.info("Starting Worker %s", self.worker_id)
        try:
            while True:
                logger.info("=" * 20)
                self.run()
                logger.info("=" * 20)
        except KeyboardInterrupt:
            logger.info("Worker %s stopped by user.", self.worker_id)
        except Exception as e:
            logger.error(
                "Worker %s encountered a critical error. Error: %s",
                self.worker_id,
                str(e),
                exc_info=True,
            )
            raise


if __name__ == "__main__":
    try:
        worker = Worker()
        worker.start()
    except Exception as e:
        logger.error("Worker initialization failed. Error: %s", str(e), exc_info=True)
