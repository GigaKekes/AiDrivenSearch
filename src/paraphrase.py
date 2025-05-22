from langchain.prompts import ChatPromptTemplate, FewShotChatMessagePromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.chains import LLMChain
from config import llm
import re
import enum

class ParaphaseMode(enum.Enum):
    """
    Enum for paraphrase modes.
    
    - EXPAND: Expands the query with 5 focus queries.
    - SIMPLIFY: Simplifies the query by generating 1 paraphrase.
    """
    EXPAND = 1
    SIMPLIFY = 0


def paraphrase_query(query : str, mode : ParaphaseMode = ParaphaseMode.SIMPLIFY) -> list[str]:
    """
    Функция для перефразировки поискового запроса с использованием LLM.
    Возвращает несколько вариантов перефразированного запроса.
    
    :param query: Исходный поисковый запрос
    :param mode: Режим перефразировки (EXPAND или SIMPLIFY)
    
    :return: Строка с перефразированными запросами
    :raises AssertionError: Если входные данные не соответствуют ожиданиям
    """
    
    assert isinstance(query, str), "Query must be a string"
    assert isinstance(mode, ParaphaseMode), "mode must be an instance of ParaphaseMode"
    
    if mode == ParaphaseMode.EXPAND:
        examples = [
        {
            "input": "как изучать python",
            "output": """
1. Как изучать Python для анализа данных  
2. Как изучать Python с нуля для начинающих  
3. Лучшие ресурсы для изучения Python онлайн  
4. Как изучать Python для веб-разработки  
5. С чего начать изучение Python для автоматизации задач"""
        },
        {
        "input": "apple",
        "output": """
1. История компании Apple  
2. Преимущества iPhone по сравнению с Android  
3. Полезные свойства яблок для здоровья  
4. Текущая стоимость акций компании Apple  
5. Как вырастить яблоню на даче"""
        },
        {
        "input": "машинное обучение",
        "output": """
1. Что такое машинное обучение
2. Основные алгоритмы машинного обучения
3. Курсы и ресурсы по машинному обучению  
4. Роль машинного обучения в искусственном интеллекте  
5. История развития машинного обучения"""
        },
        ]
        
        example_prompt = ChatPromptTemplate.from_messages(
        [
        ("human", "{input}"),
        ("ai", "{output}"),
        ]
        )
        
        few_shot_prompt = FewShotChatMessagePromptTemplate(
        example_prompt=example_prompt,
        examples=examples,
        )
        
        system_prompt = SystemMessagePromptTemplate.from_template("""
Ты — помощник по перефразированию запросов для эффективного поиска информации в интернете, который получает общий пользовательский запрос и генерирует 5 уточняющих версий запроса, каждый из которых фокусируется на отдельном аспекте или подтеме исходного вопроса. 

Требования:
- Сохраняй исходный смысл запроса.
- Запросы должны сохранять смысл, но освещать разные возможные направления уточнения.
- При коротких или неясных запросах — обязательно дополни их для лучшего понимания сути.
- Следи, чтобы дополнения не искажали исходный смысл.
- Стиль формулировок должен оставаться естественным и подходящим для поиска в интернете.
Формат:
- Пронумерованный список.
- Каждый вариант — отдельной строкой.
"""
)
    elif mode == ParaphaseMode.SIMPLIFY:
        
        examples = [
        {
            "input": "где найти книги по python",
            "output": "1. Лучшие сайты для скачивания книг по Python"
        },
        {
            "input": "Как приготовить борщ",
            "output": "1. Рецепт борща с пошаговыми инструкциями"
        },
        {
            "input": "Почему не работает интернет",
            "output": "1. Причины, по которым может не работать интернет"
        }
        ]
        
        example_prompt = ChatPromptTemplate.from_messages(
        [
        ("human", "{input}"),
        ("ai", "{output}"),
        ]
        )
        
        few_shot_prompt = FewShotChatMessagePromptTemplate(
        example_prompt=example_prompt,
        examples=examples,
        )
        
        
        system_prompt = SystemMessagePromptTemplate.from_template("""
Ты — помощник по перефразированию запросов для эффективного поиска информации в интернете. На основе запроса пользователя сгенерируй 1 перефразировку.

Требования:
- Сохраняй исходный смысл запроса.
- При коротких или неясных запросах — обязательно дополни их для лучшего понимания сути.
- Следи, чтобы дополнения не искажали исходный смысл.
- Стиль формулировок должен оставаться естественным и подходящим для поиска в интернете.

Формат:
- Пронумерованный список.
"""
)
    
    final_prompt = ChatPromptTemplate.from_messages(
    [
        system_prompt,
        few_shot_prompt,
        HumanMessagePromptTemplate.from_template("{input}"),
    ]
    )
    
    chain = final_prompt | llm
    
    
    response = chain.invoke({"input": query})
    paraphrases = list(response.split('\n'))
    paraphrases = [p for p in paraphrases if len(p) > 0 and p[0].isdigit()]
    paraphrases = [re.sub(r'^\s*\d+[\.\-\)]\s*', '', p) for p in paraphrases]
    
    return paraphrases

if __name__ == "__main__":
    query = "Как изучить тайм-менеджмент"
    paraphrased_queries = paraphrase_query(query, mode=ParaphaseMode.SIMPLIFY)
    print("Paraphrased Queries:")
    for pq in paraphrased_queries:
        print(pq)