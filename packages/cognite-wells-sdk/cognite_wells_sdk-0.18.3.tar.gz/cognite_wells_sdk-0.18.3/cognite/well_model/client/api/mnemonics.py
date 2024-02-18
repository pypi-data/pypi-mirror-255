import logging
from typing import List

from requests import Response

from cognite.well_model.client.api.api_base import BaseAPI
from cognite.well_model.client.models.resource_list import MnemonicMatchList
from cognite.well_model.models import MnemonicMatchGroup, MnemonicMatchItems, MnemonicSearch

logger = logging.getLogger(__name__)


class MnemonicsAPI(BaseAPI):
    def search(self, mnemonics: List[str]) -> MnemonicMatchList:
        """Search for measurement types using mnemonics

        Args:
            mnemonics (List[str]): List of mnemonics

        Returns:
            List[MnemonicMatchGroup]: List of match groups. There is one group
                for each mnemonic in the search term.

        Examples:
            Search for measurement types that matches the GR mnemonic
                >>> from cognite.well_model import CogniteWellsClient
                >>> wm = CogniteWellsClient()
                >>> matches = wm.mnemonics.search(["GR"])
                >>> matches.to_pandas()[["mnemonic", "companyName", "measurementType"]]
                  mnemonic                           companyName measurementType
                0       GR  Baker Atlas (formerly Dresser Atlas)       gamma ray
                1       GR                    Baker Hughes Inteq       gamma ray
                2       GR                   Halliburton Logging       gamma ray
                3       GR                   Halliburton Logging       gamma ray
                4       GR                     Numar MRI Logging       gamma ray
                5       GR                          Schlumberger       gamma ray
        """
        if len(mnemonics) == 0:
            return MnemonicMatchList([])
        path = self._get_path("/mnemonics/search")
        json = MnemonicSearch(mnemonics=mnemonics).json()
        response: Response = self.client.post(path, json)
        groups: List[MnemonicMatchGroup] = MnemonicMatchItems.parse_obj(response.json()).items
        return MnemonicMatchList(groups)
