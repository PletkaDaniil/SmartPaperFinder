import ijson
import json
import pandas as pd
from decimal import Decimal

def decode_indexed_abstract(indexed_abstract):
    """
        Декодируем аннотацию в обычный текст
    """
    try:
        inverted_index = indexed_abstract["InvertedIndex"]
        index_map = {pos: word for word, positions in inverted_index.items() for pos in positions}
        text = " ".join(index_map[pos] for pos in sorted(index_map))
        return text
    except Exception:
        return None

def convert_decimal(obj):
    """
        Рекурсивно преобразуем объекты Decimal в float в структуре данных (список, словарь и т.д.)
    """
    if isinstance(obj, list):
        return [convert_decimal(i) for i in obj]
    elif isinstance(obj, dict):
        return {k: convert_decimal(v) for k, v in obj.items()}
    elif isinstance(obj, Decimal):
        return float(obj)
    else:
        return obj

def is_valid_item(item):
    """
        Проверяем объект на наличие корректных необходимых полей
    """
    required_fields = ["title", "indexed_abstract", "n_citation", "fos", "year", "doc_type"]
    if not all(k in item for k in required_fields):
        return False

    if not isinstance(item["year"], int) or not isinstance(item["doc_type"], str) or item["doc_type"].strip() == "":
        return False

    if not item["title"] or decode_indexed_abstract(item["indexed_abstract"]) is None:
        return False

    valid_fos = [
        {"name": f["name"], "w": f["w"]}
        for f in item["fos"]
        if "name" in f and "w" in f
    ]

    return len(valid_fos) > 0

def process_item(item):
    """
        Извлекаем и форматируем нужные данные
    """
    title = item["title"]
    abstract = decode_indexed_abstract(item["indexed_abstract"])
    n_citation = item["n_citation"]
    year = item["year"]
    doc_type = item["doc_type"]
    doi = item.get("doi", None)

    fos_list = [
        {"name": f["name"], "w": f["w"]}
        for f in item["fos"]
        if "name" in f and "w" in f
    ]
    
    return {
        "title": title,
        "abstract": abstract,
        "n_citation": n_citation,
        "year": year,
        "doc_type": doc_type,
        "doi": doi,
        "fos": fos_list
    }

def load_and_clean_data(file_path, max_items):
    """
        Загружаем JSON-файл и обрабатываем, возвращая очищенный список статей
    """
    clean_data = []
    with open(file_path, "r", encoding="utf-8") as f:
        for item in ijson.items(f, "item"):
            if not is_valid_item(item):
                continue
            processed = process_item(item)
            clean_data.append(processed)
            if len(clean_data) >= max_items:
                break
    return clean_data

def save_to_csv(data, output_path):
    """
        Сохраняем обработанные данные в CSV-файл
    """
    df = pd.DataFrame(data)
    df["fos"] = df["fos"].apply(lambda x: json.dumps(convert_decimal(x)))
    df.to_csv(output_path, index=False)

def main():
    input_path = "app/citation_network_dataset/citation-network-dataset.json"
    output_path = "app/citation_network_dataset/cleaned_dataset.csv"
    clean_data = load_and_clean_data(input_path, max_items=20000)
    save_to_csv(clean_data, output_path)

if __name__ == "__main__":
    main()
