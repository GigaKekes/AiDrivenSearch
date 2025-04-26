from config import llm

def generate_answer(query, documents, history=None):
    context = "\n\n".join(
        f"{doc['domain']}:\n{doc['extended_text']}\nURL: {doc['url']}"
        for doc in documents
    )
    prompt = f"""
Ответь на вопрос пользователя, используя информацию из веб-результатов. 
Не используй информацию из других источников или из своей памяти.
На каждый вопрос отвечай только на основе предоставленных данных.
Для каждого куска текста добавляй ссылку на источник.

История: {history or "нет"}

Контекст из интернета:
{context or 'нет'}

Ответь на запрос: "{query}"
"""
    return llm.invoke(prompt).strip()