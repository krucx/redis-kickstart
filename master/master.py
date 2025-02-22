from utils.redis_util import RedisUtil
from utils.random_util import RandomUtil
import time
import logging
import argparse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Parse command line arguments
parser = argparse.ArgumentParser(description="Run the master node.")
parser.add_argument(
    "--iterations", type=int, required=True, help="Number of iterations to run"
)
args = parser.parse_args()


class Master:
    """
    A class representing a master node that pushes messages to a Redis queue.

    Attributes:
        redis (RedisUtil): An instance of RedisUtil for interacting with Redis.
        master_id (str): A unique identifier for the master instance.
        queue_name (str): The name of the Redis queue to push messages to.
    """

    def __init__(self):
        """
        Initializes a Master instance with a Redis connection, a unique master ID,
        and sets the queue name.
        """
        self.redis = RedisUtil()
        self.master_id = f"Master-{RandomUtil.get_random_number()}"
        self.queue_name = "filenames"
        logger.info("Master node initialized with ID: %s", self.master_id)

    def run(self):
        """
        Generates a message with a unique master ID, a random filename, and a timestamp,
        then pushes this message to the specified Redis queue.

        Args:
            None

        Returns:
            None

        Raises:
            Exception: If pushing the message to the Redis queue fails.
        """
        try:
            message = {
                "master_id": self.master_id,
                "filename": RandomUtil.get_random_filename(),
                "timestamp": time.time(),
            }

            self.redis.push_queue(queue_name=self.queue_name, data=message)

            logger.info(
                "Master %s pushed message: %s to Redis queue %s",
                self.master_id,
                message,
                self.queue_name,
            )

        except Exception as e:
            logger.error(
                "Failed to push message to Redis queue. Error: %s",
                str(e),
                exc_info=True,
            )
            raise

    def start(self, iterations):
        """
        Starts the master node and pushes messages to the Redis queue for the specified number of iterations.

        Args:
            iterations (int): The number of messages to push to the queue.

        Returns:
            None
        """
        try:
            for i in range(iterations):
                logger.info("-" * 20)
                self.run()
                logger.info("-" * 20)
                time.sleep(1)
        except Exception as e:
            logger.error("Master node failed to run. Error: %s", str(e), exc_info=True)
            raise


if __name__ == "__main__":
    try:
        master = Master()
        master.start(iterations=args.iterations)
    except Exception as e:
        logger.error(
            "Master node initialization failed. Error: %s", str(e), exc_info=True
        )
