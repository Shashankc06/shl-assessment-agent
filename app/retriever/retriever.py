import pandas as pd


CSV_PATH = "data/shl_catalog.csv"


def search_assessments(query, top_k=10):

    try:

        df = pd.read_csv(CSV_PATH)

    except Exception:

        return []

    query = query.lower()

    matched_results = []

    for _, row in df.iterrows():

        searchable_text = " ".join([
            str(row.get("name", "")),
            str(row.get("description", "")),
            str(row.get("job_level", "")),
            str(row.get("test_type", "")),
            str(row.get("skills", ""))
        ]).lower()

        query_words = query.split()

        score = sum(
            1 for word in query_words
            if word in searchable_text
        )

        if score > 0:

            matched_results.append({
                "name": row.get("name", ""),
                "url": row.get("url", ""),
                "description": row.get("description", ""),
                "test_type": row.get("test_type", "Assessment"),
                "remote_support": row.get(
                    "remote_support",
                    "Yes"
                ),
                "adaptive_support": row.get(
                    "adaptive_support",
                    "No"
                ),
                "duration": row.get(
                    "duration",
                    "Unknown"
                ),
                "score": score
            })

    matched_results = sorted(
        matched_results,
        key=lambda x: x["score"],
        reverse=True
    )

    return matched_results[:top_k]