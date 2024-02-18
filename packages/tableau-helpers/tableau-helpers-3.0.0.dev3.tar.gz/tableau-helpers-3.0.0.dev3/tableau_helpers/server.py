import logging
import os
from pathlib import Path
from typing import Optional, Union

import tableauserverclient as TSC

log = logging.getLogger(__name__)


class MultipleProjectsShareNameException(Exception):
    def __init__(self, name_shared, projects: Optional[list[TSC.ProjectItem]] = None):
        messages: list[str] = [
            f'Multiple projects share the name "{name_shared}",',
            "try providing a project name including parent projects separated by '/'",
            "or try referencing using the id of the project instead:",
        ]
        if projects is not None:
            project_descs = [
                f"  name: {x.name}; id: {x.id}; desc: {x.description}" for x in projects
            ]
            messages.extend(project_descs)

        message = "\n".join(messages)
        super().__init__(message)


class ProjectNotFoundException(Exception):
    def __init__(self, name_or_id):
        message = f'No project was found with the given name or id: "{name_or_id}",'
        super().__init__(message)


class ServerHelper:
    def __init__(
        self,
        tableau_server_url: Optional[str] = None,
        tableau_api_version: Optional[str] = None,
        verify: Union[bool, str] = True,
        token_name: Optional[str] = None,
        personal_access_token: Optional[str] = None,
    ):
        self.server: TSC.Server = ServerHelper._open_connection(
            tableau_server_url=tableau_server_url,
            tableau_api_version=tableau_api_version,
            verify=verify,
            token_name=token_name,
            personal_access_token=personal_access_token,
        )

    @staticmethod
    def _open_connection(
        tableau_server_url: Optional[str] = None,
        tableau_api_version: Optional[str] = None,
        verify: Union[bool, str] = True,
        token_name: Optional[str] = None,
        personal_access_token: Optional[str] = None,
    ):
        if tableau_server_url is None:
            tableau_server_url = os.getenv("TABLEAU_SERVER_URL")
        if tableau_server_url is None:
            log.critical("tableau_server_url is None, try setting TABLEAU_SERVER_URL")
        if token_name is None:
            token_name = os.getenv("TABLEAU_TOKEN_NAME")
        if token_name is None:
            log.critical(
                "token_name is None, try setting TABLEAU_TOKEN_NAME with a PAT name"
            )
        if personal_access_token is None:
            personal_access_token = os.getenv("TABLEAU_PERSONAL_ACCESS_TOKEN")
        if personal_access_token is None:
            log.critical(
                "personal_access_token is None, try setting"
                " TABLEAU_PERSONAL_ACCESS_TOKEN with a PAT key"
            )
        tableau_site = os.getenv("TABLEAU_SITE", None)
        if tableau_site is None:
            tableau_site == ""
            log.warning("TABLEAU_SITE is not set, the server default will be used")

        tableau_ssl_cert = os.getenv("TABLEAU_SSL_CERT_PATH", None)
        if tableau_ssl_cert is not None and verify is True:
            verify = tableau_ssl_cert

        server = TSC.Server(tableau_server_url)

        if isinstance(verify, str):
            server.add_http_options({"verify": verify})
        if tableau_api_version is None:
            tableau_api_version = os.getenv("TABLEAU_API_VERSION", None)
        if tableau_api_version is None:
            log.warning(
                "TABLEAU_API_VERSION is not set, behavior may change when updating"
                " tableau-server"
            )
            server.use_server_version()
        else:
            server.version = tableau_api_version

        auth = TSC.PersonalAccessTokenAuth(
            token_name=token_name,
            personal_access_token=personal_access_token,
            site_id=tableau_site,
        )
        server.auth.sign_in_with_personal_access_token(auth)
        return server

    def get_project_id(
        self,
        project_name: str,
        parent_id: Optional[str] = None,
    ) -> str:
        server = self.server
        projects: list[TSC.ProjectItem]
        project_name_remainder = None
        if project_name.find("/") > 0:
            project_name_parts = project_name.split("/", 1)
            project_name = project_name_parts[0]
            project_name_remainder = project_name_parts[1]
        req_option = TSC.RequestOptions()
        proj_filter = TSC.Filter(
            TSC.RequestOptions.Field.Name,
            TSC.RequestOptions.Operator.Equals,
            project_name,
        )
        req_option.filter.add(proj_filter)
        projects, _ = server.projects.get(req_option)
        if parent_id is not None:
            projects = [x for x in projects if x.parent_id == parent_id]
        # it isn't clear if tableau can return multiple projects with the same name
        # we should avoid unintentional writing to the wrong project
        if len(projects) > 1:
            raise MultipleProjectsShareNameException(project_name, projects)
        elif len(projects) < 1:
            # try finding a matching id instead of name as a backup
            projects = [x for x in projects if x.id == project_name]

        if len(projects) < 1:
            raise ProjectNotFoundException(project_name)

        project_id = projects[0].id
        if project_name_remainder is None:
            if project_id is None:
                raise ValueError("Error getting project ID")
            return project_id

        return self.get_project_id(project_name_remainder, project_id)

    def get_flow(self, project_name, flow_name) -> Optional[TSC.FlowItem]:
        project_id: str = self.get_project_id(project_name)
        flows: list[TSC.FlowItem]
        req_option = TSC.RequestOptions()
        flow_filter = TSC.Filter(
            TSC.RequestOptions.Field.Name,
            TSC.RequestOptions.Operator.Equals,
            flow_name,
        )
        req_option.filter.add(flow_filter)
        flows, _ = self.server.flows.get(req_option)
        for flow in flows:
            if flow.project_id == project_id:
                return flow
        return None

    def create_or_replace_hyper_file(
        self,
        source: Path,
        dest_project: str,
        name: Optional[str] = None,
    ):
        """

        :param source: the hyperfile to be uploaded
        :param dest_project: the project name, path, or id
        :param name: optionally set a different name from the filename
        :return: None
        """  # noqa
        project_id = self.get_project_id(
            project_name=dest_project,
        )
        server = self.server
        publish_mode = TSC.Server.PublishMode.Overwrite
        datasource = TSC.DatasourceItem(project_id, name=name)
        server.datasources.publish(datasource, source, publish_mode)


def get_project_id(
    project_name: str,
    parent_id: Optional[str] = None,
    tableau_server_url: Optional[str] = None,
    verify: Union[bool, str] = True,
    token_name: Optional[str] = None,
    personal_access_token: Optional[str] = None,
) -> Optional[str]:
    helper = ServerHelper(
        tableau_server_url=tableau_server_url,
        verify=verify,
        token_name=token_name,
        personal_access_token=personal_access_token,
    )
    return helper.get_project_id(project_name=project_name, parent_id=parent_id)


def create_or_replace_hyper_file(
    hyperfile_path: Path,
    project: str,
    name: Optional[str] = None,
    tableau_server_url: Optional[str] = None,
    verify: Union[bool, str] = True,
    token_name: Optional[str] = None,
    personal_access_token: Optional[str] = None,
):
    """

    :param hyperfile_path: the hyperfile to be uploaded
    :param project: the project name or id
    :param name: optionally set a different name from the filename
    :param tableau_server_url: the full url to your tableau_server
        (https://...), when None the ENVVAR "TABLEAU_SERVER_URL"
        will be loaded.
    :param verify: optionally disable ssl or point to a trusted
        cert path
    :param token_name: the name of your PAC, when None the
        ENVVAR "TABLEAU_TOKEN_NAME" will be loaded
    :param personal_access_token: the value of your PAC, when None
        the ENVVAR "TABLEAU_PERSONAL_ACCESS_TOKEN" will be loaded
    :return: None
    """  # noqa
    helper = ServerHelper(
        tableau_server_url=tableau_server_url,
        verify=verify,
        token_name=token_name,
        personal_access_token=personal_access_token,
    )
    helper.create_or_replace_hyper_file(
        source=hyperfile_path,
        dest_project=project,
        name=name,
    )
