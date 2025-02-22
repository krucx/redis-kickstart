import random


class RandomUtil:

    @staticmethod
    def get_random_number() -> str:
        return str(random.randint(1, 10000))

    @staticmethod
    def get_random_filename() -> str:
        return f"file-{RandomUtil.get_random_number()}.txt"
