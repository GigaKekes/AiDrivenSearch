import requests
import urllib.parse
import yaml
from xml.etree import ElementTree as ET
from abc import ABC, abstractmethod


class SearchEngine(ABC):
    @abstractmethod
    def build_url(self, query: str, **kwargs) -> tuple[str, dict]:
        pass

    @abstractmethod
    def parse_response(self, response_text: str) -> list[dict]:
        pass

    def search(self, query: str, **kwargs) -> list[dict]:
        base_url, params = self.build_url(query, **kwargs)
        response = requests.get(base_url, params=params)
        if response.status_code != 200:
            raise Exception(f"Ошибка при выполнении запроса: {response.status_code}")

        return self.parse_response(response)


class YandexSearch(SearchEngine):
    def __init__(self, api_key: str, folder_id: str, region: int = 213):
        self.api_key = api_key
        self.folder_id = folder_id
        self.region = region

    def build_url(self, query: str, **kwargs) -> tuple[str, dict]:
        base_url = 'https://yandex.ru/search/xml'
        params = {
            'folderid': self.folder_id,
            'apikey': self.api_key,
            'query': query,
            'lr': kwargs.get("region", self.region),
            'l10n': kwargs.get("lang", 'ru'),
            'sortby': kwargs.get("sortby", 'rlv'),
            'filter': kwargs.get("filter_type", 'strict'),
            'maxpassages': kwargs.get("maxpassages", 3),
            'groupby': kwargs.get("groupby", 'attr=d.mode=deep.groups-on-page=5.docs-in-group=3'),
            'page': kwargs.get("page", 0)
        }
        return base_url, params

    def parse_response(self, response) -> list[dict]:
        root = ET.fromstring(response.text)
        results = []

        for group in root.findall(".//group"):
            for doc in group.findall("doc"):
                url = doc.findtext("url")
                domain = doc.findtext("domain")
                extended_text = doc.find("properties").findtext("extended-text")

                if extended_text:
                    extended_text = extended_text.strip()

                results.append({
                    "url": url,
                    "domain": domain,
                    "extended_text": extended_text
                })

        return results


class GoogleSearch(SearchEngine):
    def __init__(self, api_key: str, cse_id: str):
        self.api_key = api_key
        self.cse_id = cse_id

    def build_url(self, query: str, **kwargs) -> tuple[str, dict]:
        base_url = 'https://www.googleapis.com/customsearch/v1'
        params = {
            'key': self.api_key,
            'cx': self.cse_id,
            'q': query,
            'num': kwargs.get("num_results", 10),
            'start': kwargs.get("start", 1)
        }
        return base_url, params

    def parse_response(self, response: str) -> list[dict]:
        response_json = response.json()
        results = []

        for item in response_json.get("items", []):
            url = item.get("link")
            domain = urllib.parse.urlparse(url).netloc
            extended_text = item.get("snippet")

            if extended_text:
                extended_text = extended_text.strip()

            results.append({
                "url": url,
                "domain": domain,
                "extended_text": extended_text
            })

        return results


class WebSearcher:
    def __init__(self, engine: SearchEngine):
        self.engine = engine

    def search(self, query: str, num_results: int = 5) -> list[dict] | None:
        results = self.engine.search(query)
        return results[:num_results] if results else None


def load_yandex_config(path="api_key.yaml"):
    with open(path, "r") as f:
        config = yaml.safe_load(f)
    return config["folder_id"], config["secret"]


def load_google_config(path="api_key_google.yaml"):
    with open(path, "r") as f:
        config = yaml.safe_load(f)
    return config["cse_id"], config["secret"]


# Пример использования:
if __name__ == "__main__":
    cse, api_key_google = load_google_config()
    folder_id, api_key_yandex = load_yandex_config()
    
    google_engine = GoogleSearch(api_key=api_key_google, cse_id=cse)
    yandex_engine = YandexSearch(api_key=api_key_yandex, folder_id=folder_id)
    
    searcher_google = WebSearcher(google_engine)
    searcher_yandex = WebSearcher(yandex_engine)
    
    
    print("Google Search Results:")
    results = searcher_google.search("искусственный интеллект", num_results=3)
    for r in results:
        print(r)

    print("\nYandex Search Results:")
    results = searcher_yandex.search("искусственный интеллект", num_results=3)
    for r in results:
        print(r)