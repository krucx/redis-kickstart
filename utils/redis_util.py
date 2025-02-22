import redis
import os
import json


class RedisUtil:
    """
    Utility class for interacting with Redis.

    This class provides methods to push data to and pop data from a Redis queue.
    It establishes a connection to the Redis server using environment variables and
    handles data serialization/deserialization.
    """

    def __init__(self):
        """
        Initializes the RedisUtil instance.

        Establishes a connection to the Redis server using the following environment variables:
        - REDIS_HOST: The hostname of the Redis server.
        - REDIS_PORT: The port number of the Redis server.
        - REDIS_PASSWORD: The password for the Redis server.

        Raises:
            ValueError: If any of the required environment variables are not set.
            redis.exceptions.ConnectionError: If connection to Redis server fails.
        """
        required_env_vars = {
            "REDIS_HOST": os.environ.get("REDIS_HOST", None),
            "REDIS_PORT": os.environ.get("REDIS_PORT", None),
            "REDIS_PASSWORD": os.environ.get("REDIS_PASSWORD", None),
        }

        # Check if all required environment variables are set
        for var, value in required_env_vars.items():
            if not value:
                raise ValueError(f"Environment variable {var} is not set.")

        self.redis_conn = redis.Redis(
            host=required_env_vars["REDIS_HOST"],
            port=int(required_env_vars["REDIS_PORT"]),
            password=required_env_vars["REDIS_PASSWORD"],
            decode_responses=True,
        )

        # Test the connection to Redis
        try:
            self.redis_conn.ping()
        except redis.exceptions.ConnectionError as e:
            raise redis.exceptions.ConnectionError(
                "Failed to connect to Redis server"
            ) from e

    def push_queue(self, queue_name: str, data: dict) -> None:
        """
        Pushes data to the specified Redis queue.

        Args:
            queue_name (str): The name of the Redis queue.
            data (dict): The data to be pushed to the queue as a dictionary.

        Raises:
            ValueError: If the input data cannot be serialized to JSON.
        """
        try:
            json_data = json.dumps(data)
        except:
            raise ValueError(f"Input data {data} is not serializable to JSON.")

        self.redis_conn.rpush(queue_name, json_data)

    def pop_queue(self, queue_name: str) -> dict:
        """
        Pops data from the specified Redis queue.

        Args:
            queue_name (str): The name of the Redis queue.

        Returns:
            dict: The data popped from the queue as a dictionary.

        Raises:
            ValueError: If the popped data is not valid JSON.
        """
        result = self.redis_conn.blpop(queue_name)

        try:
            return json.loads(result[1])
        except:
            raise ValueError(f"Return value {result} is not a valid JSON string.")
