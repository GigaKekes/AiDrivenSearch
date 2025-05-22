import time
import requests

import urllib.parse
import yaml

from xml.etree import ElementTree as ET
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor, as_completed


DEFAULT_NUM_RESULTS = 10

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
    def __init__(self, api_key: str, folder_id: str):
        self.api_key = api_key
        self.folder_id = folder_id

    def build_url(self, query: str, **kwargs) -> tuple[str, dict]:
        
        num_results = kwargs.get("num_results", DEFAULT_NUM_RESULTS)
        groupby_param = f"attr=d.mode=flat.groups-on-page={num_results}"
        
        base_url = 'https://yandex.ru/search/xml'
        params = {
            'folderid': self.folder_id,
            'apikey': self.api_key,
            'query': query,
            'lr': kwargs.get("region", '213'),
            'l10n': kwargs.get("lang", 'ru'),
            'sortby': kwargs.get("sortby", 'rlv'),
            'filter': kwargs.get("filter_type", 'strict'),
            'maxpassages': kwargs.get("maxpassages", 3),
            'groupby': groupby_param,
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
            'num': kwargs.get("num_results", DEFAULT_NUM_RESULTS),
            'lr': kwargs.get("lang", 'lang_ru'),
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

cse, api_key_google = load_google_config()
folder_id, api_key_yandex = load_yandex_config()

def parallel_search(searchers, query, num_results):
    results = {}
    with ThreadPoolExecutor(max_workers=len(searchers)) as executor:
        future_to_engine = {
            executor.submit(searcher.search, query, num_results): name
            for name, searcher in searchers.items()
        }

        for future in as_completed(future_to_engine):
            engine_name = future_to_engine[future]
            try:
                results[engine_name] = future.result()
            except Exception as e:
                results[engine_name] = f"Ошибка: {e}"

    return results


def parallel_search_yandex_google(query : str, num_results : int = 5, unbox_unique : bool = True) -> list[dict[str]] | dict[list[dict[str]]] | None:
    google_engine = GoogleSearch(api_key=api_key_google, cse_id=cse)
    yandex_engine = YandexSearch(api_key=api_key_yandex, folder_id=folder_id)
    
    searchers = {
        "Google": WebSearcher(google_engine),
        "Yandex": WebSearcher(yandex_engine)
    }
    
    results = parallel_search(searchers, query, num_results=num_results)
    if unbox_unique:
        unique_urls = {r["url"] for res in results.values() if isinstance(res, list) for r in res if "url" in r}
        return list(unique_urls) 
    return results
    

if __name__ == "__main__":
    query = "что такое искусственный интеллект"
    results = parallel_search_yandex_google(query, num_results=5)
    print(results)
