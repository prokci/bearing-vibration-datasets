import os


class ComputerSettings:
    @staticmethod
    def get_user_dict():
        base_path = os.getenv("DATA_DIR", os.path.join(".", "data"))
        return {
            'path': base_path,
            'env_path': os.getenv("ENV_PATH", os.path.join(".", ".env"))
        }
    