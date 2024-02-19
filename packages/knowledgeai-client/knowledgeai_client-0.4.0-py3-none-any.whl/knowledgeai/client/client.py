import json
import logging
import os
from typing import List, Optional, Any
from enum import StrEnum

import magic
import requests
from requests import Response
from requests_toolbelt import MultipartEncoder
from tqdm import tqdm

from knowledgeai.client.schema import (
    LLM,
    AskResponse,
    IsoLanguage,
    Project,
    ProjectConfigKey,
    RetrievedDocument,
    Retriever,
    SourceDocument,
)

log: logging.Logger = logging.getLogger(__name__)


class HttpMethod(StrEnum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"


class Plan(StrEnum):
    FREE = "Free"
    BASIC = "Basic"
    PREMIUM = "Premium"
    ENTERPRISE = "Enterprise"


class KnowledgeAIClient:
    def __init__(self, url: str, api_key: str, timeout: int = 30) -> None:
        self.url: str = url
        self.api_key: str = api_key
        self.timeout = timeout

    @staticmethod
    def read_files_from_directory(directory: str) -> List[str]:
        files = []
        for file in os.listdir(directory):
            if os.path.isfile(os.path.join(directory, file)):
                files.append(os.path.join(directory, file))
        return files

    def _api_call(
        self,
        method: HttpMethod,
        url: str,
        data: Optional[Any] = None,
        params: Optional[Any] = None,
        form: bool = True,
    ) -> Response:
        headers: dict[str, str] = {
            "accept": "application/json",
            "x-apikey": self.api_key,
        }

        if form:
            headers["Content-Type"] = "application/x-www-form-urlencoded"

        if method == HttpMethod.DELETE:
            response: Response = requests.get(
                url, headers=headers, timeout=self.timeout
            )
        elif method == HttpMethod.POST:
            response = requests.post(
                url, headers=headers, data=data, timeout=self.timeout
            )
        elif method == HttpMethod.PUT:
            response = requests.put(
                url, headers=headers, data=data, timeout=self.timeout
            )
        else:
            response = requests.get(
                url, headers=headers, data=data, params=params, timeout=self.timeout
            )

        response.raise_for_status()

        return response

    def upload_directory(
        self, project_id: str, directory: str, roles: str = "user"
    ) -> None:
        """
        Convenience method to upload all files in a directory to the specified project.

        Args:
            project_id (str): The ID of the project to upload the documents to.
            directory (str): The path to the directory containing the files to upload.
            roles (str, optional): The roles to assign to the uploaded documents.
                Comma separated list, defaults to "user".

        Returns:
            None

        Raises:
            requests.exceptions.RequestException: If an error occurs while uploading
            the documents.

        Example:
            >>> client.upload_directory("project_id", "/path/to/directory", "admin,user")
        """
        files: List[str] = self.read_files_from_directory(directory)
        self.index_documents(project_id, files, roles)

    def index_documents(
        self, project_id: str, files: List, roles: str = "user"
    ) -> None:
        """
        Uploads multiple documents to the specified project.

        Args:
            project_id (str): The ID of the project to upload the documents to.
            files (List[str]): A list of file paths to upload.
            roles (str, optional): The roles to assign to the uploaded documents.
                Comma separated list, defaults to "user".

        Returns:
            None

        Raises:
            requests.exceptions.RequestException: If an error occurs while uploading
            the documents.

        Example:
            >>> client.add_multiple_documents(
                    "project_id", ["/path/to/file1.txt", "/path/to/file2.txt"],
                    roles="user,admin"
                )
        """
        url: str = self.url + "/index/document"
        filesp = tqdm(files)

        for file in filesp:
            log.debug("Uploading file: %s", file)
            data = MultipartEncoder(
                fields={
                    "project_id": project_id,
                    "roles": roles,
                    "file": (file, open(file, "rb"), magic.from_file(file, mime=True)),
                }
            )
            headers: dict[str, str] = {
                "x-apikey": self.api_key,
                "Content-Type": data.content_type,
            }
            response: Response = requests.post(
                url=url, headers=headers, data=data, timeout=self.timeout
            )
            log.debug(msg=response.content)

    def index_urls(
        self, project_id: str, index_urls: List[str], roles: Optional[str]
    ) -> None:
        """
        Indexes the specified URL to the specified project.

        Args:
            project_id (str): The ID of the project to index the URL to.
            url (str): The URLs to index.
            roles (str, optional): The roles to assign to the indexed document.
                Comma separated list, defaults to "user".

        Returns:
            None

        Raises:
            requests.exceptions.RequestException: If an error occurs while indexing the URL.

        Example:
            >>> client.index_url("project_id", "https://www.example.com", roles="user,admin")
        """
        url = self.url + "/index/urls"
        data = {"project_id": project_id, "urls": index_urls, "roles": roles}
        self._api_call(HttpMethod.POST, url, data=data)

    def list_projects(self) -> List[Project]:
        """
        Lists all projects.

        Returns:
            List[Project]: A list of projects.

        Raises:
            requests.exceptions.RequestException: If an error occurs while listing the projects.

        Example:
            >>> projects = client.list_projects()
            >>> for project in projects:
            ...     print(project.name)
        """
        url: str = self.url + "/project/"
        response = self._api_call(HttpMethod.GET, url, form=False)

        return [Project(**project) for project in response.json()]

    def get_project(self, project_id: int, with_documents: bool = False) -> Project:
        """
        Gets the project with the specified ID.

        Args:
            project_id (str): The ID of the project to get.
            with_documents (bool, optional): Whether to include the documents in the response,

        Returns:
            Project: The project with the specified ID.

        Raises:
            requests.exceptions.RequestException: If an error occurs while getting the project.

        Example:
            >>> project = client.get_project(1)
            >>> print(project.name)
        """
        url: str = self.url + "/project/" + str(project_id)
        data = {"with_documents": with_documents}
        response = self._api_call(HttpMethod.GET, url, params=data)

        project = response.json()
        return Project(**project)

    def create_project(
        self,
        project_name: str,
        prompt: str,
        language: IsoLanguage = IsoLanguage.ENGLISH,
        llm: LLM = LLM.OPENAI,
    ) -> Project:
        """
        Creates a new project with the specified name.

        Args:
            project_name (str): The name of the project to create.
            language (IsoLanguage, optional): The language of the project, defaults to IsoLanguage.ENGLISH.
            llm (LLM, optional): The language model to use, defaults to LLM.OPENAI.
            prompt (str, optional): The prompt to use for the project, defaults to None.

        Returns:
            Response: The created project.

        Raises:
            requests.exceptions.RequestException: If an error occurs while creating the project.

        Example:
            >>> project = client.create_project("New Project")
            >>> print(project.name)
        """
        url: str = self.url + "/project/create"

        data = {
            "name": project_name,
            "language": language.value,
            "llm": llm.value,
            "prompt": "x",
        }

        if prompt:
            data["prompt"] = prompt

        response = self._api_call(HttpMethod.POST, url, data=data)
        project = response.json()
        return Project(**project)

    def update_project(self, project: Project) -> Response:
        """Updates the specified project.

        Args:
            project (Project): The project to update. Does not update the configuration or the documents.

        Returns:
            Response: The updated project.

        Raises:
            requests.exceptions.RequestException: If an error occurs while updating the project.

        Example:
            >>> project = client.get_project(1)
            >>> project.name = "New Project Name"
            >>> response = client.update_project(project)
        """

        url: str = self.url + "/project/" + str(project.id)
        data = {
            "project_id": project.id,
            "name": project.name,
            "language": project.language.value,
            "model": project.model.value,
            "prompt": project.prompt,
        }

        return self._api_call(HttpMethod.PUT, url, data=data)

    def update_project_configuration(
        self, project_id: int, key: ProjectConfigKey, value: str
    ) -> Project:
        """Updates the configuration of the specified project.

        Args:
            project_id (int): The ID of the project to update the configuration for.
            key (str): The key of the configuration to update.
            value (str): The value to update the configuration to.

        Returns:
            Project: The updated project.

        Raises:
            requests.exceptions.RequestException: If an error occurs while updating the configuration.

        Example:
            >>> project = client.update_project_configuration(1, ProjectConfigKey.WELCOME_MESSAGE, "value")
        """

        url: str = (
            self.url + "/project/" + str(project_id) + "/configuration/" + key.value
        )
        data = {"value": value}
        response = self._api_call(HttpMethod.PUT, url, data=data)

        return Project(**response.json())

    def ask(self, project_id: int, question: str) -> AskResponse:
        """Asks a question to the specified project.

        Args:
            project_id (int): The ID of the project to ask the question to.
            question (str): The question to ask.

        Returns:
            AskResponse: The response to the question.

        Raises:
            requests.exceptions.RequestException: If an error occurs while asking the question.

        Example:
            >>> response = client.ask(1, "What is the capital of Germany?")
            >>> print(response.answer)
        """

        url: str = self.url + "/chat/ask"
        data = {
            "project_id": project_id,
            "question": question,
        }

        response = self._api_call(HttpMethod.POST, url, data=data)
        content = json.loads(response.content)

        references: List[SourceDocument] = []
        for reference in content["source_documents"]:
            references.append(SourceDocument(**reference))

        ask_response = AskResponse(
            question=content["question"],
            answer=content["answer"],
            source_paragraphs=content["source_paragraphs"],
            source_documents=references,
        )

        return ask_response

    def retrieve(
        self, project_id: int, query: str, retrieval_type: Retriever = Retriever.default
    ) -> List[RetrievedDocument]:
        """Retrieves documents for the specified project.

        Args:

            project_id (int): The ID of the project to retrieve documents from.
            query (str): The query to retrieve documents for.
            retrieval_type (Retriever, optional): The type of retrieval to use, defaults to Retriever.default.

        Returns:
            List[RetrievedDocument]: The retrieved documents, containing the splitted paragraph and a dictionary with metadata.

        Raises:
            requests.exceptions.RequestException: If an error occurs while retrieving the documents.

        Example:
            >>> references = client.retrieve(1, "What is the capital of Germany?")
            >>> for reference in references:
            ...     print(reference.content)
        """
        url: str = self.url + "/index/retrieve"
        data = {"project_id": project_id, "query": query, "type": retrieval_type.value}

        response = self._api_call(HttpMethod.POST, url, data=data)
        content = json.loads(response.content)

        references: List[RetrievedDocument] = []
        for reference in content["documents"]:
            references.append(RetrievedDocument(**reference))

        return references
