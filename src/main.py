from paraphrase import paraphrase_query
from web_search import search_web
from reranker import rerank_documents
from answer_generator import generate_answer

def ai_overview_pipeline(user_query, history=None):
    print("🔁 Перефразировка запроса...")
    refined = paraphrase_query(user_query, history)
    print("📝 Перефразированный запрос:", refined)
    
    print("🌐 Веб-поиск...")
    raw_docs = search_web(refined)
    print("🔍 Результаты поиска:", raw_docs)
    
    print("📊 Реранкинг...")
    top_docs = rerank_documents(refined, raw_docs)
    print("📄 Топ-результаты:", top_docs)
    
    print("🤖 Генерация ответа...")
    answer = generate_answer(user_query, top_docs, history)
    print("📝 Ответ:", answer)

    return answer

if __name__ == "__main__":
    
    history = []
    while True:
        print("\n\n====================\n")
        q = input("Введите ваш вопрос: ")
        res = ai_overview_pipeline(q, history)
        history.append("Пользователь: " + q)
        history.append("AI-агент: " + res)
        
        print("\n📝 Ответ:\n", res)

