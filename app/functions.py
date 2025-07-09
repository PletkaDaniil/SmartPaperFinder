import arxiv
from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer("all-MiniLM-L6-v2")

def search_arxiv(query: str, max_results: int):
    search = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.Relevance,
    )
    results = []
    for result in search.results():
        results.append({
            "title": result.title,
            "summary": result.summary,
            "url": result.entry_id,
            "published": result.published,
        })
    return results

def semantic_sort(query: str, articles: list):
    query_embedding = model.encode(query, convert_to_tensor=True)
    summaries = [a['summary'] for a in articles]
    summary_embeddings = model.encode(summaries, convert_to_tensor=True)
    similarities = util.cos_sim(query_embedding, summary_embeddings)[0]
    
    for ind, article in enumerate(articles):
        article['score'] = float(similarities[ind])
    return sorted(articles, key=lambda x: x['score'], reverse=True)
