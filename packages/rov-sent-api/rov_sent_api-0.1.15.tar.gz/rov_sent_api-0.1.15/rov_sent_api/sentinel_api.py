# JSON parser
import json
import logging

# system modules
import os
import sys
from datetime import datetime, timedelta
from enum import Enum, auto
from typing import Any, Dict, List, Literal, Optional

import numpy as np
import rasterio
import requests
from pyproj import Transformer
from rasterio.windows import from_bounds


class SentinelApi:
    # base URL of the product catalogue
    catalogue_odata_url = "https://catalogue.dataspace.copernicus.eu/odata/v1"
    auth_server_url = "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"
    download_url = "https://zipper.dataspace.copernicus.eu/odata/v1"

    class AutoName(Enum):
        @staticmethod
        def _generate_next_value_(name, start, count, last_values):
            return name

    class ProductType(AutoName):
        SLC = auto()
        GRD = auto()
        OCN = auto()
        S2MSI2A = auto()
        S2MSI1C = auto()
        S2MS2Ap = auto()

    def __init__(self, user, password) -> None:
        self.user = user
        self.password = password

    def _find_query(
        self,
        productType: ProductType,
        tile: str,
        init_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        cloud_cover: Optional[int] = None,
        limit: Optional[int] = None,
        order_desc: Optional[int] = True,
    ) -> str:
        """Create query to find a list of products using the given filters

        Args:
            productType (ProductType): type of product to find
            tile (str): the Tile in the Sentinel system
            init_date (datetime, optional): the initial date of the search
            end_date (datetime, optional): the end date of the search
            cloud_cover (int, optional): the maximum cloud cover allowed in percentage
            limit (int, optional): the maximum number of products to return
            order_desc (bool, optional): order the products descending on Start date

        Returns:
            str: OData query.
        """

        init_date = (
            f" and ContentDate/Start gt {init_date.isoformat()}" if init_date else ""
        )
        end_date = (
            f" and ContentDate/Start lt {end_date.isoformat()}" if end_date else ""
        )
        cloud_cover = (
            f" and Attributes/OData.CSC.DoubleAttribute/any(att:att/Name eq 'cloudCover' and att/OData.CSC.DoubleAttribute/Value lt {cloud_cover}.00)"
            if cloud_cover
            else ""
        )
        order_by = (
            "&$orderby=ContentDate/Start desc"
            if order_desc
            else "&$orderby=ContentDate/Start asc"
        )
        limit = f"&$top={limit}" if limit else ""
        search_query = f"{self.catalogue_odata_url}/Products?$filter=contains(Name, '_T{tile}_'){cloud_cover} and Attributes/OData.CSC.StringAttribute/any(att:att/Name eq 'productType' and att/OData.CSC.StringAttribute/Value eq '{productType.value}'){init_date}{end_date}&$expand=Attributes{order_by}{limit}"
        return search_query

    def find(
        self,
        productType: ProductType,
        tile: str,
        init_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        cloud_cover: Optional[int] = None,
        limit: Optional[int] = None,
        order_desc: Optional[int] = True,
    ) -> List[Dict[str, Any]]:
        """Finds a list of products using the given filters

        Args:
            productType (ProductType): type of product to find
            tile (str): the Tile in the Sentinel system
            init_date (datetime, optional): the initial date of the search
            end_date (datetime, optional): the end date of the search
            cloud_cover (int, optional): the maximum cloud cover allowed in percentage
            limit (int, optional): the maximum number of products to return
            order_desc (bool, optional): order the products descending on Start date

        Returns:
            List[Dict[str, Any]]: a list of all products
        """
        search_query = self._find_query(
            productType, tile, init_date, end_date, cloud_cover, limit, order_desc
        )
        response = requests.get(search_query).json()
        output = []

        for product in response["value"]:
            output.append(_parse_odata_response(product))

        return output

    def create_cog_s3_path(
        self, tile: str, date: datetime, satellite_platform: Literal["A", "B"]
    ) -> str:
        """Creates an s3 path for Sentinel 2 Cog products that are stored in a s3 bucket mantained by Element 84. See
        https://registry.opendata.aws/sentinel-2-l2a-cogs/ for more info

        Args:
            tile (str): the utm tile of the product (ex. 19HCD)
            date (datetime): the date in which the product was captured
            satellite_platform (str): the Sentinel 2 satellite platform that captured the product

        Returns:
            str: s3 path of the cog for this sentinel product.
        """
        return (
            "s3://sentinel-cogs/sentinel-s2-l2a-cogs/"
            f"{tile[:-3]}/{tile[-3]}/{tile[-2:]}/{date.year}/{date.month}/"
            f"S2{satellite_platform}_{tile}_{date.strftime('%Y%m%d')}_0_L2A"
        )

    def info(self, uuid: str, full=False) -> Dict[str, Any]:
        """Get the info of a particular product

        Args:
            uuid (str): the uuid of the product
            full (bool, optional): If it's necessary to expand the result. Defaults to False.

        Returns:
            Dict[str, Any]: a dict with all the info
        """
        query = f"{self.catalogue_odata_url}/Products({uuid})"
        if full:
            query += "?&$expand=Attributes"

        try:
            response = requests.get(query).json()
            return _parse_odata_response(response)
        except Exception as e:
            print(e)
            return False

    def _get_access_token(self) -> str:
        data = {
            "client_id": "cdse-public",
            "username": self.user,
            "password": self.password,
            "grant_type": "password",
        }
        try:
            r = requests.post(
                self.auth_server_url,
                data=data,
            )
            r.raise_for_status()
        except Exception as e:
            raise Exception(
                f"Access token creation failed. Reponse from the server was: {r.json()}"
            )
        return r.json()["access_token"]

    def extract_window_from_cog(
        self,
        cog_s3_path: str,
        filename: str,
        window_coords: tuple[float, float, float, float],
        window_crs: str = "EPSG:4326",
    ) -> np.ndarray:
        """Extracts a window from a COG Sentinel 2 product stored in the sentinel-cogs s3 bucket

        Args:
            cog_s3_path (str): path to sentinel 2 cog product folder
            filename (str): specific file that will be opened (ex. TCI)
            window_coords (tuple[float, float, float, float]): window coordinates in the form `(west, north, east, south)`
            window_crs (_type_, optional): CRS of window coordinates. Defaults to "EPSG:4326".

        Returns:
            np.ndarray: pixel values from that window
        """
        with rasterio.open(os.path.join(cog_s3_path, f"{filename}.tif")) as src:
            transformer = Transformer.from_crs(window_crs, src.crs)
            p1 = transformer.transform(window_coords[1], window_coords[0])
            p2 = transformer.transform(window_coords[3], window_coords[2])
            window = from_bounds(
                left=p1[0],
                bottom=p2[1],
                right=p2[0],
                top=p1[1],
                transform=src.transform,
            )
            array = []
            for channel in range(src.count):
                array.append(src.read(channel + 1, window=window))
            return np.stack(array, axis=-1).squeeze()

    def download(self, uuid: str, path: str = "./", replace: bool = True) -> str:
        """Download a particular product

        Args:
            uuid (str): the uuid of the product to download
            path (str, optional): the path where to download the product. Defaults to "./".
            replace (bool, optional): if true will replace existing file at path, else will keep current file.

        Returns:
            str: the absolute path of the downloaded product
        """
        access_token = self._get_access_token()
        url = f"{self.download_url}/Products({uuid})/$value"

        headers = {"Authorization": f"Bearer {access_token}"}
        info = self.info(uuid)
        title = info["title"] + ".zip"
        final_path = os.path.join(path, title)

        if not replace and os.path.exists(final_path):
            return os.path.abspath(final_path)

        with requests.Session() as session:
            session.headers.update(headers)
            response = session.get(url, headers=headers, stream=True)

            total_size = info["size"]
            chunk_size = 8192
            with open(final_path, "wb") as file:
                for i, chunk in enumerate(response.iter_content(chunk_size=chunk_size)):
                    if chunk:
                        file.write(chunk)
                        # print percentage if total payload size available, else Mb downloaded
                        log_msg = (
                            f"\r{title} {i*chunk_size} / {total_size} ({round(i * chunk_size / total_size * 100, 4)}%)"
                            if total_size != 0
                            else f"\r {title} {round(i*chunk_size/(1e6),2)} Mb downloaded"
                        )
                        sys.stdout.write(log_msg)
                        sys.stdout.flush()

            return os.path.abspath(final_path)

    def is_online(self, uuid: str) -> bool:
        """Test if this product is online for

        Args:
            uuid (str): the uuid of the product to test

        Returns:
            bool: if is it online or not
        """
        info = self.info(uuid)
        return info["Online"]


def _parse_odata_response(product):
    output = {
        "id": product["Id"],
        "title": product["Name"],
        "size": int(product["ContentLength"]),
        "date": _parse_iso_date(product["ContentDate"]["Start"]),
        "footprint": product["Footprint"],
        "s3_path": product["S3Path"],
        "Online": product.get("Online", True),
    }
    if "Checksum" in product:
        for algorithm in product["Checksum"]:
            if "Algorithm" in algorithm:
                output[algorithm["Algorithm"].lower()]: algorithm["Value"]
    # Parse the extended metadata, if provided
    converters = [float, int, _parse_iso_date]
    if "Attributes" in product:
        for attr in product["Attributes"]:
            value = attr["Value"]
            for f in converters:
                try:
                    value = f(attr["Value"])
                    break
                except ValueError:
                    pass
            output[attr["Name"]] = value
    return output


def _parse_iso_date(content):
    if "." in content:
        return datetime.strptime(content, "%Y-%m-%dT%H:%M:%S.%fZ")
    else:
        return datetime.strptime(content, "%Y-%m-%dT%H:%M:%SZ")
