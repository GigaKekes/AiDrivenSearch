import requests
import urllib.parse
import yaml
from xml.etree import ElementTree as ET

def build_yandex_xml_url(
    folder_id: str,
    api_key: str,
    query: str,
    region: int = 213,
    lang: str = 'ru',
    sortby: str = 'rlv',
    filter_type: str = 'strict',
    maxpassages: int = 3,
    groupby: str = 'attr=d.mode=deep.groups-on-page=5.docs-in-group=3',
    page: int = 0
) -> tuple[str, dict]:
    base_url = 'https://yandex.ru/search/xml'
    params = {
        'folderid': folder_id,
        'apikey': api_key,
        'query': query,
        'lr': region,
        'l10n': lang,
        'sortby': sortby,
        'filter': filter_type,
        'maxpassages': maxpassages,
        'groupby': groupby,
        'page': page,
    }
    return base_url, params


if __name__ == '__main__':

    with open("api_key.yaml", "r") as f:
        config = yaml.safe_load(f)

    API_KEY = config["secret"]
    FOLDER_ID = config["folder_id"]
    query = 'искусственный интеллект'

    url, params = build_yandex_xml_url(
        folder_id=FOLDER_ID,
        api_key=API_KEY,
        query=query,
        region=11316,
        page=0
    )

    # Отправляем GET-запрос
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        print("Запрос выполнен успешно.")
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
        
        print(results)
    else:
        print(f"Ошибка: {response.status_code} - {response.text}") 
    
    
    
    # Логирование ответа в xml файл
    with open("response.xml", "w") as f:
        f.write(response.text)

