from models import llm
from langchain_core.messages import SystemMessage, HumanMessage

def generate_answer(query, documents: list[str]) -> str:
    """
    Генерирует ответ на основе полученного из интернета контекста (documents) и пользовательского запроса (query).

    :param query: Пользовательский вопрос
    :param documents: Список строк с контекстом (результатами поиска), каждая строка включает ссылку
    :return: Ответ, основанный только на этих документах
    """

    context = "\n\n".join(f"[{i+1}] {url}, {doc}" for i, (url, doc) in enumerate(documents)) if documents else "нет"

    system_prompt = SystemMessage(
        content=(
            "Ты — помощник, который отвечает на вопросы пользователя исключительно на основе полученного контекста из интернета."
            "Не используй знания из своей памяти"
            "Каждое утверждение должно иметь ссылку на источник"
            "Если информации недостаточно, честно сообщи об этом."
        )
    )

    human_prompt = HumanMessage(
        content=(
            f"Контекст из интернета:\n{context}\n\n"
            f"Вопрос пользователя: \"{query}\"\n\n"
            "Ответь на этот вопрос, используя только указанный контекст и добавляя ссылки на источники."
        )
    )

    return llm.invoke([system_prompt, human_prompt]).strip()