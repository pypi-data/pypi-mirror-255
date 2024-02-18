import os
import logging


logger = logging.getLogger(__name__)


def get_public_key_from_url(public_key_url: str, file_path: str):
    """Upload public key from URL."""

    import httpx

    public_key = None

    try:
        with httpx.Client() as client:
            response = client.get(public_key_url)

            if response.status_code != 200:
                raise Exception(f"Status code: {response.status_code}")

            public_key = response.text

            with open(file_path, "w") as f:
                f.write(public_key)

    except Exception as e:
        logger.warning("Could not load public key from URL: " + str(e))

    return public_key


def get_public_key_from_file(file_path: str):
    """Get public key from pem file."""
    public_key = None
    try:
        if not os.path.isfile(file_path):
            raise Exception("Public key file not found")

        with open(file_path, "r") as f:
            public_key = f.read()

    except Exception as e:
        logger.warning("Could not load public key from file: " + str(e))

    return public_key


class Config:
    public_key = None
    public_key_url = os.getenv("PUBLIC_KEY_URL", "https://auth.example.com/pk")
    jwt_issuer = os.getenv("JWT_ISSUER", "mu-sse")
    jwt_algorithm = os.getenv("JWT_ALGORITHM", "RS256")
    public_key_file_path = os.getenv("PUBLIC_KEY_FILE_PATH", "public_key.pem")

    def __init__(self):
        self.update_public_key()

    def update_public_key(self):
        """Update public key."""
        if self.public_key_url is not None and self.public_key_url != "":
            self.public_key = get_public_key_from_url(
                self.public_key_url, self.public_key_file_path
            )

        if (
            self.public_key is None
            and self.public_key_file_path is not None
            and self.public_key_file_path != ""
        ):
            self.public_key = get_public_key_from_file(self.public_key_file_path)

        if self.public_key is None:
            logger.error("No public key available")


config = Config()
