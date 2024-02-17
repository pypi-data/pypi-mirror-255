"""FortiGate source for MacPyver."""

import requests
from macpyver_core.model import Version
from macpyver_core.version_source import VersionSource

from .exceptions import FortiGateAPIError


class FortiGateSource(VersionSource):
    """MacPyVer VersionSource for FortiGate."""

    _hostname: str
    _access_token: str

    @classmethod
    def set_details(cls, hostname: str, access_token: str) -> None:
        """Set the details for the FortiGate API.

        Sets the details for the FortiGate API. This should be called before
        using the FortiGateSource.

        Args:
            hostname: the hostname of the FortiGate API.
            access_token: the access token for the FortiGate API.
        """
        cls._hostname = hostname
        cls._access_token = access_token

    def get_all_versions(self) -> list[Version]:
        """Get all versions from the FortiGate API.

        Returns:
            A list of Version objects from the FortiGate API.

        Raises:
            FortiGateAPIError: on a API error.
        """
        response = requests.get(
            f"https://{self._hostname}" +
            "/api/v2/monitor/system/firmware?access_token=" +
            f"{self._access_token}",
            verify=False,
            timeout=10)

        only_mature = self.software.extra_information.get(
            'fortigate_only_mature', False)

        if response.status_code == 200:
            try:
                versions = response.json()['results']['available']
                versions.extend([response.json()['results']['current']])
            except KeyError as exc:
                raise FortiGateAPIError('Wrong API response') from exc

            return [
                Version(version=version['version'])
                for version in versions
                if ((only_mature and version['maturity'] == 'M') or
                    (not only_mature))
            ]
        raise FortiGateAPIError('Failed to retrieve FortiGate OS version.')
