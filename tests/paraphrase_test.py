from src.paraphrase import paraphrase_query


def test_paraphrase_query():
    # Пример использования функции
    user_query = "Какой самый высокий водопад в мире?"
    history = []
    
    # Вызов функции ai_overview_pipeline
    answer = paraphrase_query(user_query, history)
    
    # Вывод ответа
    print("Ответ:", answer)

def test_paraphrase_query_with_history():
    # Пример использования функции
    user_query = "Где он родился?"
    history = ["Пользователь: Кто написал 'Войну и мир'?", "ИИ ответ: Роман 'Война и мир' написал Лев Толстой"]
    
    # Вызов функции ai_overview_pipeline
    answer = paraphrase_query(user_query, history)
    
    # Вывод ответа
    print("Ответ:", answer)

if __name__ == "__main__":
    test_paraphrase_query_with_history()