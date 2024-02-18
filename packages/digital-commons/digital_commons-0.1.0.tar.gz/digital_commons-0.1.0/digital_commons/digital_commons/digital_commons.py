import json
import requests
from typing import Literal, Tuple


class DigitalCommons:
    """Base class for all DigitalCommons Classes with methods built on requests.

    Attributes:
        site_url (str): The site_url of your DigitalCommons API.
        key (str): The Authorization key that matches your site url.
    """

    def __init__(self, site_url: str, key: str):
        self.site_url = site_url.replace("http://", "").replace("https://", "")
        self.headers = {"Authorization": key}

    def __request(self, url: str):
        r = requests.get(
            url=url,
            headers=self.headers,
        )
        return r.json()

    def get_indexed_fields(self, field_type: Literal["all", "default"] = "all"):
        """Get all indexed fields.

        Args:
            field_type (Literal['all', 'default']): A literal indicating whether
                you want all indexed fields or just the defaults.

        Returns:
            dict: A dict with results matching your request.

        Examples:
            >>> DigitalCommons().get_indexed_fields(field_type='default')
            ... #doctest: +NORMALIZE_WHITESPACE
            {'fields': ['author', 'document_type', 'comments', 'publication_date',
            'title', 'url', 'parent_key', 'context_key', 'download_link',
            'download_format']}

        """
        return self.__request(
            f"https://content-out.bepress.com/v2/{self.site_url}/fields?field_type={field_type}"
        )

    def query(
        self,
        query: Tuple[Tuple[str, str], ...],
    ):
        """Query the DigitalCommons API.

        Args:
            query (Tuple[Tuple[str, str], ...]): A tuple of tuples containing
                your query parameters.

        Returns:
            dict: A dict with results matching your query.

        Examples:
            >>> DigitalCommons.query(('q', 'video'),('title', '2013'),('limit', '2'))
            ... #doctest: +NORMALIZE_WHITESPACE
            {'results': [{'context_key': '4088503', 'title':
            '2013 Freerange Video Contest', 'url': 'http://trace.tennessee.edu/utk_studfr13',
            'parent_key': '885231'}, {'url': 'http://trace.tennessee.edu/utk_thirdthursday/77',
            'download_format': 'pdf', 'parent_key': '3115213', 'download_link':
            'https://trace.tennessee.edu/cgi/viewcontent.cgi?article=1105&context=utk_thirdthursday',
            'context_key': '3932951', 'title': 'Third Thursday 2-2013',
            'publication_date': '2013-02-01T08:00:00Z', 'document_type':
            ['newsletter', 'Newsletter', 'Newsletters'],
            'author': ['Institute of Agriculture']}],
            'query_meta': {'total_hits': 49, 'start': 0, 'limit': 2,
            'field_params': {'include_only': ['author', 'document_type',
            'comments', 'publication_date', 'title', 'url', 'parent_key',
            'context_key', 'download_link', 'download_format']}}}

        """
        query_params = "&".join(f"{key}={value}" for key, value in query)
        return self.__request(
            f"https://content-out.bepress.com/v2/{self.site_url}/query?{query_params}"
        )

    def download(self, uuid: str, filename: str = "results.json"):
        """Download the contents of a specific export.

        Args:
            uuid (str): The uuid of the export you want to download.
            filename (str): The filename you want to save the contents to.

        Returns:
            str: A string indicating the success of the download.

        Examples:
            >>> DigitalCommons().download(
            ... '1707399113-f7d64a11-48d5-4638-8530-91a816f002f5',
            ... filename='results.json'
            ... )
            'Downloaded contents to results.json.'
        """
        contents = self.__request(
            f"https://content-out.bepress.com/v2/{self.site_url}/download/{uuid}",
        )
        with open(filename, "w") as f:
            json.dump(contents, f, indent=4)
        return f"Downloaded contents to {filename}."

    def export(
        self,
        query: Tuple[Tuple[str, str], ...],
    ):
        """Export the results of a specific query.

        Args:
            query (Tuple[Tuple[str, str], ...]): A tuple of tuples
                containing your query parameters.

        Returns:
            dict: A dict with an error or the export id of your request.

        Examples:
            >>> DigitalCommons().export(('q', 'video'),('title', '2013'),('limit', '2'))
            {'ExportId': '1707401080-b16bbbcf-937e-4379-8950-b4c12931e91c'}
        """
        query_params = "&".join(
            f"{key}={value}"
            for key, value in query
            if key != "start" and key != "limit"
        )
        return requests.put(
            f"https://content-out.bepress.com/v2/{self.site_url}/export?{query_params}",
            headers=self.headers,
        ).json()

    def export_full(self):
        """Export all published and indexed content from your site.

        Returns:
            dict: A dict with an error or the export id of your request.

        Examples:
            >>> DigitalCommons().export_full()
            {'ExportId': '1707401080-b16bbbcf-937e-4379-8950-b4c12931e91c'}
        """
        return requests.put(
            f"https://content-out.bepress.com/v2/{self.site_url}/export?select_fields=all",
            headers=self.headers,
        ).json()
