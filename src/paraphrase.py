from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_core.messages import SystemMessage, HumanMessage
from src.config import llm
import re

def paraphrase_query(query : str, history : None | str | list = None, num_paraphrases : int = 5) -> list[str]:
    """
    Функция для перефразировки поискового запроса с использованием LLM.
    Возвращает несколько вариантов перефразированного запроса.
    
    :param query: Исходный поисковый запрос
    :param history: История запросов пользователя (строка или список)
    :param num_paraphrases: Количество вариантов перефразировки
    :return: Строка с перефразированными запросами
    :raises AssertionError: Если входные данные не соответствуют ожиданиям
    """
    
    
    assert isinstance(query, str), "Query must be a string"
    assert isinstance(history, (str, list, type(None))), "History must be a string, list or None"
    assert isinstance(num_paraphrases, int) and num_paraphrases > 0, "num_paraphrases must be a positive integer"
    
    system_prompt = SystemMessage(content="""
Ты — помощник по перефразированию запросов для эффективного поиска информации в интернете.
На основе запроса пользователя и истории взаимодействия сгенерируй N разных перефразировок.

Требования:
- Сохраняй исходный смысл запроса.
- Используй разные формулировки, синонимы и уточнения.
- При коротких или неясных запросах — обязательно дополни их для лучшего понимания сути.
- Если в истории взаимодействия упоминается конкретный объект, персонаж или тема, к которому относится текущий запрос, обязательно уточни это в перефразировках, используя эту информацию явно.
- Следи, чтобы дополнения не искажали исходный смысл.
- При уточнении исходи из предположения, что пользователь продолжает разговор на ту же тему, что и ранее.
- Стиль формулировок должен оставаться естественным и подходящим для поиска в интернете.

Формат:
- Пронумерованный список.
- Каждый вариант — отдельной строкой.
"""
)
    formated_history = "\n".join(history) if isinstance(history, list) else history
    human_prompt = HumanMessage(content=f"""
История: 
{formated_history or "нет"}

Текущий запрос:
{query}

Количествыо перефразировок: {num_paraphrases}
"""
    )
    
    print("Human prompt:", human_prompt.content)
    
    response = llm.invoke([system_prompt, human_prompt])
    paraphrases = list(response.split('\n'))
    paraphrases = [p for p in paraphrases if len(p) > 0 and p[0].isdigit()]
    paraphrases = [re.sub(r'^\s*\d+[\.\-\)]\s*', '', p) for p in paraphrases]
    
    return paraphrases
