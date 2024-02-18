import sys
import os

# Get the path to the current directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Add the current directory to sys.path
sys.path.insert(0, current_dir)

import logging
from ploomes_client.core.utils import generate_email
from ploomes_client.core.ploomes_client import PloomesClient
from ploomes_client.collections.users import Users


logger = logging.getLogger(__name__)


class ApiKeyRotator:
    """
    This class encapsulates the logic for rotating API keys in response to rate limiting or other
    restrictions imposed by the Ploomes API. By adhering to the Single Responsibility Principle (SRP),
    this class ensures a clean separation of concerns whereby API key rotation logic is isolated from the
    core PloomesClient functionality, thereby promoting easier maintenance and extension.
    """

    def __init__(self, client: PloomesClient) -> None:
        """
        Initializes the ApiKeyRotator with a reference to the PloomesClient instance.

        Args:
            client (PloomesClient): The PloomesClient instance for which API key rotation is managed.
        """
        self.client = client
        self.users = Users(client)
        self.current_user = None

    def get_current_user_name(self) -> str:
        """
        Retrieves the name of the current user based on the current API key.

        This is necessary to later search for or create a new user with a different API key but the
        same name, as part of the rotation mechanism.

        Returns:
            str: The name of the current user, or an empty string if the user could not be retrieved.
        """
        logger.warning(self.client.api_key)
        current_user = self.users.get_users(
            filter_=f"UserKey eq '{self.client.api_key}'", top=1
        ).first
        logger.warning(current_user)
        if current_user:
            self.current_user = current_user
            return current_user.get("Name")
        logger.error("Failed to fetch the current user")
        return ""

    def get_new_api_key(self, user_name: str) -> str:
        """
        Attempts to retrieve a new API key by finding another user with the same name but a different
        API key. If no such user is found, creates a new user with the same name.

        Args:
            user_name (str): The name of the current user, used to find or create a new user.

        Returns:
            str: The new API key, or an empty string if a new user could not be found or created.
        """
        new_user = self.users.get_users(
            filter_=f"Name eq '{user_name}' and UserKey ne '{self.client.api_key}'"
        ).first
        if not new_user:
            # The rationale here is to ensure continuity of service by creating a new user
            # with a new API key when an existing user with a different API key isn't found.
            new_user_payload = {
                "Name": user_name,
                "Email": generate_email(),
                "AvatarUrl": self.current_user.get("AvatarUrl"),
                "Integration": True,
                "ProfileId": 1,
            }
            new_user = self.users.post_user(new_user_payload).first
            if not new_user or "UserKey" not in new_user:
                logger.error("Failed to create a new user")
                return ""
        return new_user["UserKey"]

    def rotate_api_key(self) -> None:
        """
        Orchestrates the API key rotation process by first retrieving the current user's name,
        then attempting to find or create a new user with a new API key, and finally updating
        the PloomesClient instance with the new API key.

        This method ensures that the PloomesClient's API key remains updated, promoting continued
        access to the Ploomes API even in the face of rate limiting or other restrictions.
        """
        logger.warning("Rotating API key...")
        user_name = self.get_current_user_name()
        logger.warning(user_name)
        if user_name:
            new_api_key = self.get_new_api_key(user_name)
            if new_api_key:
                logger.warning(f"New API key: {new_api_key}")
                self.client.api_key = new_api_key
                self.client.headers = {
                    "User-Key": new_api_key,
                    "Content-Type": "application/json",
                }
