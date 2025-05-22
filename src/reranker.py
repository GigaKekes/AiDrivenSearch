import numpy as np

from sklearn.metrics.pairwise import cosine_similarity

from models import cross_encoder, bi_encoder

def preprocess(texts, is_query=True):
    prefix = "query: " if is_query else "passage: "
    return [prefix + text.strip() for text in texts]

def batch_encode(texts, is_query=True, batch_size=8):
    """Encodes texts using batching."""
    processed_texts = preprocess(texts, is_query)
    embeddings = []
    for i in range(0, len(processed_texts), batch_size):
        batch = processed_texts[i:i + batch_size]
        embeddings_batch = bi_encoder.encode(batch)
        embeddings.extend(embeddings_batch)
    return np.array(embeddings)

def mmr(query_embedding, doc_embeddings, documents, top_n=5, lambda_param=0.7):
    """
    Maximal Marginal Relevance (MMR) for document selection.
    Selects documents that are both relevant to the query and diverse from each other.
    
    :param query_embedding: Embedding of the query.
    :param doc_embeddings: List of document embeddings.
    :param documents: List of documents.
    :param top_n: Number of documents to select.
    :param lambda_param: Trade-off parameter between relevance and diversity.
    :return: List of selected documents.
    """
    
    selected_indices = []
    remaining_indices = list(range(len(doc_embeddings)))
    query_similarities = cosine_similarity(query_embedding, doc_embeddings).flatten()
    print("query similarities", query_similarities)
    for _ in range(top_n):
        mmr_scores = []
        for i in remaining_indices:
            diversity_score = max(
                cosine_similarity([doc_embeddings[i]], [doc_embeddings[j]])[0][0]
                for j in selected_indices
            ) if selected_indices else 0
            
            mmr_score = lambda_param * query_similarities[i] - (1 - lambda_param) * diversity_score
            mmr_scores.append((i, mmr_score))
        best_doc = max(mmr_scores, key=lambda x: x[1])
        selected_indices.append(best_doc[0])
        remaining_indices.remove(best_doc[0])
    
    selected = []
    for idx in selected_indices:
        selected.append(documents[idx])
    return selected

def rerank_documents(query, documents, top_n=5, mmr_lambda=0.5, batch_size=8):
    query_embedding = batch_encode([query], is_query=True, batch_size=1)
    doc_embeddings = batch_encode(documents, is_query=False, batch_size=batch_size)
    print("query embedding", query_embedding)
    return mmr(query_embedding, doc_embeddings, documents, top_n, mmr_lambda)