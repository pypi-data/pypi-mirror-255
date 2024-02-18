from attrs import define as define
from eloclient.models import client_info, EditInfoC, EditInfoZ
from eloclient import Client

from eloclient.models import BRequestIXServicePortIFLogin
from eloclient.api.ix_service_port_if import (ix_service_port_if_login)
import base64
import logging
import re

@define
class Cookie:
    key: str
    value: str


@define
class EloConnection:
    url: str
    user: str
    password: str
    ci: client_info.ClientInfo  # ClientInfo object can be omitted when using HTTP Basic Auth
    cookies: list[Cookie] = []


def _log_http_response(response):
    request = response.request
    logging.debug(f"Response event hook: {request.method} {request.url} - Status {response.status_code}")


class LoginUtil:
    elo_connection: EloConnection
    url: str
    user: str
    password: str

    def __init__(self, url: str, user: str, password: str):
        """
        :param url: The URL to the ELO IX server rest endpoint e.g. http://eloserver.com:6056/ix-Archive/rest/
        :param user: The user for the ELO IX server e.g. Administrator
        :param password: The password for the ELO IX server user e.g. secret
        """
        self.url = url
        self.user = user
        self.password = password
        self.elo_client = None  # is set in renew_token
        self.renew_token()

    def renew_token(self) -> EloConnection:
        """
        Calls the login endpoint to receive a ticket that is valid for a certain time.
        """
        client = Client(base_url=self.url,
                        httpx_args={
                            "event_hooks": {"request": [self._log_http_request],
                                            "response": [_log_http_response]}})

        with client as client:
            # It is important to set the clientInfo object with 'string' and 0 otherwise the login will fail
            clientInfo = client_info.ClientInfo(
                call_id="",
                country="AT",
                language="de",
                ticket="string",
                # format "GMT" + sign + hh + ":" + mm.
                time_zone="GMT+01:00",
                options=0
            )

            login = BRequestIXServicePortIFLogin(
                user_name=self.user,
                user_pwd=self.password,
                client_computer="",
                run_as_user="",
                ci=clientInfo
            )

            connection = ix_service_port_if_login.sync_detailed(client=client, json_body=login)
            # In case the request is not correctly formatted the ticket will be this string and not an actual ticket
            if connection.parsed.result.client_info.ticket == "de.elo.ix.client.ticket_from_cookie":
                raise Exception("Login failed - Ticket is not valid")

            # List of tuples
            headers: list[tuple] = connection.headers.raw
            cookies: list[Cookie] = []
            for header in headers:
                if str(header[0]) == "b'Set-Cookie'":
                    header_content = str(header[1])
                    index_splitter = header_content.find("=")
                    header_key, header_value = (header_content[0:index_splitter], header_content[index_splitter + 1:])
                    header_value = re.sub(pattern=";.*Path=\\/.*'", repl="", string=header_value)
                    header_value = re.sub(pattern=";.*HttpOnly'", repl="", string=header_value)
                    header_key = header_key.replace("b'", "")
                    cookies.append(Cookie(key=header_key, value=header_value))

            # Swap cookies
            cookies[0], cookies[1] = cookies[1], cookies[0]

            self.elo_connection = EloConnection(
                url=self.url,
                user=self.user,
                password=self.password,
                ci=connection.parsed.result.client_info,
                cookies=cookies
            )

            self.elo_client = self.prepare_elo_client(self.elo_connection)

    def _log_http_request(self, request):
        logging.debug(f"Request event hook: {request.method} {request.url} - Waiting for response")
        logging.debug(f"Request headers {request.headers}")
        logging.debug(f"Request detail {request.content}")

    def _gen_http_basic_hash(self, user, pw) -> str:
        return base64.b64encode((user + ":" + pw).encode("utf-8")).decode("utf-8")

    def prepare_elo_client(self, elo_connection) -> Client:
        client = Client(base_url=elo_connection.url, httpx_args={"event_hooks": {"request": [self._log_http_request],
                                                                                 "response": [_log_http_response]}})
        # TODO migrate to AuthenticatedClient
        client = client.with_cookies({"JSESSIONID": elo_connection.ci.ticket + ".ELO-DESKTOP-E6H3J7R-1"})
        client = client.with_headers({
            "Authorization": "Basic " + self._gen_http_basic_hash(elo_connection.user, elo_connection.password)
        })
        return client
