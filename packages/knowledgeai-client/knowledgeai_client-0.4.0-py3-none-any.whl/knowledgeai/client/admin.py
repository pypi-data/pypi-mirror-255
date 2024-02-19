import json
import logging
from typing import Any, List

import requests
from requests.models import Response

from knowledgeai.client.schema import User

log: logging.Logger = logging.getLogger(__name__)


class KnowledgeAIAdminClient:
    """
    This class provides a client for the admin part of the Aila Knowledge API.
    It allows you to list users, create a new user, get a specific user,
    and update an existing user.
    """

    def __init__(self, url: str, admin_api_key: str, timeout: int = 90) -> None:
        """
        Constructor for the KnowledgeAIAdminClient.

        Args:
            url (str): The base URL of the Aila Knowledge API.
            admin_api_key (str): The API key for the admin user.
            timeout (int, optional): The timeout for the HTTP requests. Defaults to 90.
        """

        self.url: str = url
        self.api_key: str = admin_api_key
        self.timeout = timeout

    def list_users(self) -> List[User]:
        """
        Method to list all users.

        Returns:
            List[User]: A list of User objects.

        Raises:
            HTTPError: If the HTTP request returned an unsuccessful status code.

        Example:
            >>> users = client.list_users()
            >>> for user in users:
            ...     print(user.name)
        """

        url: str = self.url + "/admin/user/"
        headers: dict[str, str] = {
            "accept": "application/json",
            "x-apikey": self.api_key,
        }
        response: Response = requests.get(url, headers=headers, timeout=self.timeout)
        response.raise_for_status()
        return [User(**user) for user in response.json()]

    def create_user(self, user: User) -> User:
        """
        Method to create a new user.

        Args:
            user (User): The user to create.

        Returns:
            User: The created user.

        Raises:
            HTTPError: If the HTTP request returned an unsuccessful status code.

        Example:
            >>> from knowledgeai.schema import IsoLanguage, LLM, Plan, User
            >>> user = User(
            ...     name="pytest",
            ...     company="pytest",
            ...     language=IsoLanguage.ENGLISH,
            ...     plan=Plan.BASIC,
            ...     llm=LLM.OPENAI,
            ... )
            >>> client.create_user(user)
        """

        url: str = self.url + "/admin/user"
        headers: dict[str, str] = {
            "accept": "application/json",
            "x-apikey": self.api_key,
            "Content-Type": "application/x-www-form-urlencoded",
        }
        data: dict[str, Any] = {
            "name": user.name,
            "company": user.company,
            "language": user.language.value,
            "plan": user.plan.value,
            "llm": user.llm.value,
        }

        response: Response = requests.post(
            url, headers=headers, data=data, timeout=self.timeout
        )
        response.raise_for_status()
        user_dict = json.loads(response.content)
        return User(**user_dict)

    def get_user(self, api_key: str) -> User:
        """
        Method to get a specific user.

        Args:
            api_key (str): The API key of the user.

        Returns:
            User: The user.

        Raises:
            HTTPError: If the HTTP request returned an unsuccessful status code.

        Example:
            >>> user = client.get_user("put key here")
            >>> print(user.name)
        """

        url: str = self.url + "/admin/user/" + api_key
        headers: dict[str, str] = {
            "accept": "application/json",
            "x-apikey": self.api_key,
        }
        response: Response = requests.get(url, headers=headers, timeout=self.timeout)
        response.raise_for_status()
        return User(**response.json())

    def update_user(self, user: User) -> User:
        """
        Method to update an existing user.

        Args:
            user (User): The user to update.

        Returns:
            User: The updated user.

        Raises:
            HTTPError: If the HTTP request returned an unsuccessful status code.

        Example:
            >>> user = client.get_user("put key here")
            >>> user.company = "new company name"
            >>> client.update_user(user)
        """

        url: str = self.url + "/admin/user/" + user.api_key
        headers: dict[str, str] = {
            "accept": "application/json",
            "x-apikey": self.api_key,
            "Content-Type": "application/x-www-form-urlencoded",
        }
        data = {
            "api_key": user.api_key,
            "name": user.name,
            "company": user.company,
            "language": user.language.value,
            "plan": user.plan.value,
            "llm": user.llm.value,
        }

        response: Response = requests.put(
            url, headers=headers, data=data, timeout=self.timeout
        )
        response.raise_for_status()
        return User(**response.json())
