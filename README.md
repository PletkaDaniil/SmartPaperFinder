# SmartPaperFinder

https://github.com/user-attachments/assets/6f80b0a7-7df4-4ba8-b886-864a923c9ee6

## Описание проекта

С ростом числа публикаций на arXiv исследователям становится все труднее отслеживать ключевые работы в своей области. Стандартный поиск по ключевым словам часто неэффективен для сложных и узкоспециализированных запросов. Проект направлен на создание интеллектуальной системы, которая по запросу пользователя будет находить, анализировать и структурировать релевантные научные статьи. Система должна не просто находить статьи, а ранжировать их по смысловой близости к запросу, извлекать ключевые выводы, методологию и результаты, предоставляя пользователю концентрированную сводку по теме.

## Запуск основной части проекта

Для успешного запуска и дальнейшей работы необходимо заполнить файл [API_KEY](app/API_KEY) вашим личным API-ключом, полученным в [Google AI Studio](https://aistudio.google.com/prompts/new_chat). (В случае возникновения ошибок попробуйте использовать VPN)

```
python -m venv venv
```
```
venv/scripts/activate
```
```
pip install poetry
```
```
poetry install
```
```
poetry run python app/main.py
```

## Реализация

1. Основная часть проекта настроена в файлах [main.py](app/main.py) и [functions.py](app/functions.py)

2. В качестве основного интрумента (для построения эмбеддингов) была выбрана модель ["allenai-specter"](https://huggingface.co/sentence-transformers/allenai-specter), поскольку она предобучена на научных статьях. При наличии достаточных вычислительных ресурсов можно рассмотреть и другие, более мощные модели

3. **Ход работы проекта**

    a) Сбор релевантных статей с arXiv за последний год по запросу пользователя

    b) Вычлинение необходимой информации, например, **title**, **summary**, **url** и других метаданных

    c) Загрузка полного текста найденных статей в формате PDF

    d) Построение эмбеддингов с использованием выбранной модели и сравнение их с эмбеддингом пользовательского запроса

    e) Добавление информации о количестве цитирований из [Semantic Scholar](https://www.semanticscholar.org/)) для каждой статьи

    f) Генерирование краткой аннтоации (summary) на русском языке к каждой статье (с помощью модели **gemini-2.0-flash-001**). Для работы требуется получить [API-ключ](app/API_KEY) с ресурса [Google AI Studio](https://aistudio.google.com/prompts/new_chat)
    
    g) Формирование и выдача пользователю ТОП-10 наиболее релевантных статей в отсортированном виде

4. **Предсказывание числа цитирований**

    Отдельным направлением разработки стало предсказание будущего числа цитирований на основе содержания статьи, её названия, аннотации и других параметров. Реализация представлена в файле [Citation_analysis.ipynb](Citation_analysis.ipynb). Для корректной работы необходимо загрузить в Colab файл с данными [cleaned_dataset.csv](app/citation_network_dataset/cleaned_dataset.csv).

    Как видно из метрик результат который 

5. **Формирование датасета**

    Вы также можете самостоятельно создать файл [cleaned_dataset.csv](app/citation_network_dataset/cleaned_dataset.csv). Для этого нужно перейти на Kaggle и скачать датасет [Citation Network Dataset](https://www.kaggle.com/datasets/mathurinache/citation-network-dataset?resource=download) в папку ``app/citation_network_dataset``. Датасет будет называться ``dblp.v12.json`` — переименуйте его в ``citation-network-dataset.json``. Затем можно запустить файл [citation_dataset.py)](app/citation_network_dataset/citation_dataset.py) следующей командой:

    ```
    poetry run python app/citation_network_dataset/citation_dataset.py
    ```

