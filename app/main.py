from functions import search_arxiv, semantic_sort

if __name__ == "__main__":
    query = input("Enter your research query: ")
    articles = search_arxiv(query, 30)
    sorted_articles = semantic_sort(query, articles)

    for article in sorted_articles[:10]:
        print(f"Title: {article['title']}")
        print(f"Similarity Score: {article['score']:.4f}")
        print(f"Published: {article['published'].date()}")
        print(f"URL: {article['url']}")
        print(f"Summary: {article['summary']}")
        print("---" * 15, "\n")
