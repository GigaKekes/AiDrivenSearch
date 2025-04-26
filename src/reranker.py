from config import cross_encoder

def rerank_documents(query, documents, top_n=5):
    pairs = [(query, doc['extended_text']) for doc in documents]
    scores = cross_encoder.predict(pairs)
    ranked = sorted(zip(scores, documents), key=lambda x: x[0], reverse=True)
    return [doc for _, doc in ranked[:top_n]]