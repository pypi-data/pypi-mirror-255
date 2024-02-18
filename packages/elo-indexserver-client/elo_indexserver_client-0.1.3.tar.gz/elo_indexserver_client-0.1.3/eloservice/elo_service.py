from eloclient import Client
from eloclient.api.ix_service_port_if import (ix_service_port_if_checkin_sord_path)
from eloclient.models import (BRequestIXServicePortIFCheckinSordPath)

from eloclient.models import Sord, SordZ, SordC
from eloservice.file_util import FileUtil
from eloservice.login_util import LoginUtil
from eloservice.mask_util import MaskUtil


class EloService:
    elo_client: Client
    login_util: LoginUtil
    elo_connection = None
    mask_util = None
    file_util = None

    def __init__(self, url: str, user: str, password: str):
        self.login_util = LoginUtil(url, user, password)
        self.elo_client: Client = self.login_util.elo_client
        self.elo_connection = self.login_util.elo_connection
        self.mask_util = MaskUtil(self.elo_client, self.elo_connection)
        self.file_util = FileUtil(self.elo_client, self.elo_connection)

    def renew_token(self):
        self.login_util.renew_token()
        self.elo_client = self.login_util.elo_client
        self.elo_connection = self.login_util.elo_connection

    def create_folder(self, path: str, separator="¶") -> str:
        """
        This function creates new folder in ELO
        Depending on the given path it is possible to create 1 or multiple folders. If the folder already exists,
        nothing is changed and the sordID of the existing folder is returned.
        :param path: The path in ELO to the needed folder/ doc (e.g. = ¶Alpha AG¶Eingangsrechnungen¶2023¶November¶20¶)
        :param separator: The separator which should be used to split the path (default = "¶")
        :return: The sordID of the created folder
        """
        parent_id = "1"  # the parent ID of the root element
        sords = self._split_path_elements(path, separator)

        body = BRequestIXServicePortIFCheckinSordPath(
            ci=self.elo_connection.ci,
            parent_id=parent_id,
            sords=sords,
            sord_z=SordZ(SordC().mb_all)
        )

        erg = ix_service_port_if_checkin_sord_path.sync_detailed(client=self.elo_client, json_body=body)
        object_id = erg.parsed.result[-1]
        if object_id is None:
            raise ValueError("Could not create folder")
        return object_id

    def overwrite_mask_fields(self, sord_id: str, mask_name: str, metadata: dict):
        """
        This function removes the old metadata and overwrite it with the new metadata
        :param sord_id: The sordID of the mask in ELO
        :param mask_name: The name of the mask in ELO
        :param metadata: The metadata which should be overwritten
        """
        self.mask_util.overwrite_mask_fields(sord_id, mask_name, metadata)

    def upload_file(self, file_path: str, parent_id: str, filemask_id="0", filename="") -> str:
        """
        This function uploads a file to ELO
        :param filename: The name of the file in ELO, if not given the name of the file_path is used
        :param filemask_id:  The maskID of the filemask in ELO, default is "0" (--> mask "Freie Eingabe" = STD mask)
        :param file_path: The path of the file which should be uploaded
        :param parent_id: The sordID of the parent folder in ELO
        :return: The sordID of the uploaded file
        """
        return self.file_util.upload_file(file_path, parent_id, filemask_id, filename)

    def _split_path_elements(self, path, separator="¶") -> list[Sord]:
        """
        This help function splits a path in subparts and return the splitte parts
        :param path: A path with a given separator, e.g = "/Alpha AG/Eingangsrechnungen/2023/November/20"
        :param separator: The separator which should be used to split the path (default = "¶")
        :return: The subparts of the path = path slices
        """
        return [Sord(name=path_element) for path_element in filter(None, path.split(separator))]
