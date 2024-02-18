from __future__ import annotations

import io
import zipfile
from typing import Optional

import requests
import rich

from vanty.config import config, logger
from vanty.schema import DownloadProjectHttpResponse, LicenseVerifiedHttpResponse


class Client:
    def _download_zip(self, url: str) -> io.BytesIO:
        """
        Downloads the zip file from the url.

        :param url:
        :return:
        """
        response = requests.get(url)
        zipped_file = io.BytesIO(response.content)
        return zipped_file

    def verify(self, license_token: str) -> LicenseVerifiedHttpResponse:
        """
        Authenticates the token.

        :param token:
        :return:
        """
        server_url = config.get("server_url")
        rich.print(f"Verifying license against [blue]{server_url}[/blue]")
        try:
            res = requests.post(
                f"{server_url}/projects/authenticate-license/",
                json={"license_token": license_token},
            )
            data = res.json()
            return LicenseVerifiedHttpResponse(**data, license_token=license_token)
        except Exception as e:
            logger.error(f"Error verifying token: {e}")
            return LicenseVerifiedHttpResponse.error()

    def download(self, project_id: Optional[str]):
        """
        Gets the project.
        :return:
        """

        headers = {"X-API-Token": f"{config.get('token_secret')}"}
        local_folder = config.get("local_folder")
        server_url = config.get("server_url")

        rich.print(f"Downloading project from [blue]{server_url}[/blue]")
        response = requests.get(f"{server_url}/projects/download/", headers=headers)
        data = DownloadProjectHttpResponse(**response.json())

        if data.is_valid is False or data.profile_status == "inactive":
            rich.print(
                "[red]Project Download Failed, the link may have expired!"
                "\n Please try again.[/red]"
            )
            return

        if data.profile_status == "inactive":
            rich.print("[red]Project is no longer active or has expired.[/red]")
            return

        # fetch the zip file
        response = requests.get(data.url)
        if not response.status_code == 200:
            rich.print(
                "[red]File Download Failed, the link may have expired!\n "
                "Please try again.[/red]"
            )
            return

        # save the zip file
        zipped_file = self._download_zip(data.url)
        with zipfile.ZipFile(zipped_file) as zf:
            zf.extractall(path=local_folder)

        rich.print("[green]Project files downloaded successfully[/green]")
