import arxiv
import requests
import os
import fitz
import numpy as np
from google import genai
from datetime import datetime, timedelta, timezone
from sentence_transformers import SentenceTransformer, util

# Инициализация выбранной модели
model = SentenceTransformer("allenai-specter")

# Инициализация клиента Google GenAI
with open(os.path.abspath("app/API_KEY"), "r") as file:
    api_key = file.read().strip()
client = genai.Client(api_key=api_key)


def translate_text(text):
    """
        Переводим текст на русский язык
    """
    response = client.models.generate_content(
        model='gemini-2.0-flash-001',
        contents=['Translate this text to Russian:', text]
    )
    return response.text

def generate_summary(text):
    """
        Генерируем краткое содержание текста - summary
    """
    response = client.models.generate_content(
        model='gemini-2.0-flash-001',
        contents=['Could you summarize this text?', text]
    )
    return translate_text(response.text)

def get_citation_count(arxiv_id):
    """
        Получаем количество цитирований статьи по её arXiv ID
    """
    try:
        r = requests.post(
            'https://api.semanticscholar.org/graph/v1/paper/batch',
            params={'fields': 'citationCount'},
            json={"ids": [f"ARXIV:{arxiv_id.split('v')[0]}"]}
        )
        if r.status_code != 200:
            print(f"Semantic Scholar API error: {r.status_code}")
            return "--"

        data = r.json()
        print(f"Retrieved citation count for {arxiv_id}: {data}")
        count = data[0].get("citationCount")
        return str(count) if count is not None else "--"

    except (IndexError, KeyError, requests.RequestException) as e:
        print(f"Error retrieving citation count for {arxiv_id}: {e}")
        return "--"

def search_arxiv(query: str, max_results: int):
    """
        Выполняем поиск статей на arXiv по заданному запросу, фильтруем по дате,
        добавляя информацию о количестве цитирований
    """
    client = arxiv.Client()
    search = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.Relevance,
    )

    timer = datetime.now(timezone.utc) - timedelta(days=365)
    results = []
    for result in client.results(search):
        if result.published >= timer:
            arxiv_id = result.entry_id.split("/")[-1]
            citation_count = get_citation_count(arxiv_id)
            results.append({
                "title": result.title,
                "summary": result.summary,
                "url": result.entry_id,
                "pdf_url": result.pdf_url,
                "published": result.published,
                "citations": citation_count
            })
    print(f"Найдено подходящих статей: {len(results)}")
    return results

def download_pdf(pdf_url: str, save_dir="pdfs/"):
    """
        Скачиваем PDF-файл статьи
    """
    os.makedirs(save_dir, exist_ok=True)
    paper_id = pdf_url.split("/")[-1]
    save_path = os.path.join(save_dir, f"{paper_id}.pdf")
    if not os.path.exists(save_path):
        response = requests.get(pdf_url)
        with open(save_path, "wb") as f:
            f.write(response.content)
    return save_path

def extract_text_from_pdf(pdf_path: str):
    """
        Извлекаем текст из PDF-ки
    """
    text = ""
    with fitz.open(pdf_path) as doc:
        for page in doc:
            text += page.get_text()
    return text

def compute_quality_score(similarity, citations, pub_year):
    """
        Вычисляем "качество" статьи 
    """
    current_year = datetime.now(timezone.utc).year
    alpha = 0.4
    beta = 0.6
    citation_rate = citations / (current_year - pub_year + 1)
    return alpha * similarity + beta * np.log1p(citation_rate)

def safe_int(value: int, default=0):
    try:
        return int(value)
    except (ValueError, TypeError):
        return default

def semantic_sort(query: str, articles: list):
    """
        Выполняем сортировку списка статей по запросу:
        - генерируем эмбеддинги текста
        - скачиваем PDF
        - извлекаем текст
        - получаем итоговую оценку (score)
    """
    query_embedding = model.encode(query, convert_to_tensor=True)

    fulltexts = []
    for article in articles:
        try:
            pdf_path = download_pdf(article["pdf_url"])
            print("Ready: ", pdf_path)
            fulltext = extract_text_from_pdf(pdf_path)
            article["fulltext"] = fulltext
            article["generated_summary"] = generate_summary(fulltext)
        except Exception as e:
            print(f"Error processing {article['pdf_url']}: {e}")
            article["fulltext"] = article["summary"]
            article["generated_summary"] = "--"
        fulltexts.append(article["fulltext"])

    text_embeddings = model.encode(fulltexts, convert_to_tensor=True, batch_size=32)
    similarities = util.cos_sim(query_embedding, text_embeddings)[0]

    for ind, article in enumerate(articles):
        similarity = float(similarities[ind])
        article['score'] = compute_quality_score(similarity, safe_int(article["citations"]), article["published"].year)

    return sorted(articles, key=lambda x: x['score'], reverse=True)
