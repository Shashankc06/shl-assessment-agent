import pandas as pd

CSV_PATH = "data/shl_catalog.csv"


def search_assessments(query, top_k=5):

    df = pd.read_csv(CSV_PATH)

    query = query.lower()

    results = []

    for _, row in df.iterrows():

        searchable_text = (
            str(row.get("name", "")) + " " +
            str(row.get("description", "")) + " " +
            str(row.get("skills", ""))
        ).lower()

        if any(word in searchable_text for word in query.split()):

            results.append({
                "name": row.get("name", ""),
                "url": row.get("url", ""),
                "description": row.get("description", ""),
                "test_type": row.get("test_type", "Assessment")
            })

    return results[:top_k]