import json
import faiss
import numpy as np

from sentence_transformers import SentenceTransformer

# Load embedding model
model = SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2"
)

# Load FAISS index
index = faiss.read_index(
    "data/shl_faiss.index"
)

# Load metadata
with open(
    "data/shl_metadata.json",
    "r",
    encoding="utf-8"
) as f:

    metadata = json.load(f)


def is_valid_assessment(item):

    url = item["url"].lower()
    name = item["name"].lower()

    # Remove broad/non-assessment pages
    invalid_keywords = [
        "product-catalog",
        "video-interviews",
        "solutions",
        "report"
    ]

    if any(
        word in url or word in name
        for word in invalid_keywords
    ):
        return False

    return True


def rerank_results(results, query):

    query = query.lower()

    scored = []

    for item in results:

        score = 0

        text = (
            item["name"] + " " +
            item["description"]
        ).lower()

        # Simple keyword boosting
        for word in query.split():

            if word in text:
                score += 1

        scored.append((score, item))

    scored.sort(
        key=lambda x: x[0],
        reverse=True
    )

    return [item for score, item in scored]


def search_assessments(
    query,
    top_k=5
):

    query_embedding = model.encode([query])

    query_embedding = np.array(
        query_embedding,
        dtype="float32"
    )

    distances, indices = index.search(
        query_embedding,
        top_k * 3
    )

    results = []

    for idx in indices[0]:

        if idx < len(metadata):

            item = metadata[idx]

            if is_valid_assessment(item):

                results.append({
                    "name": item["name"],
                    "url": item["url"],
                    "description": item["description"]
                })

    # Remove duplicates
    unique_results = []

    seen_urls = set()

    for item in results:

        if item["url"] not in seen_urls:

            unique_results.append(item)

            seen_urls.add(item["url"])

    # Rerank
    reranked = rerank_results(
        unique_results,
        query
    )

    return reranked[:top_k]


# Test retrieval
if __name__ == "__main__":

    query = (
        "Java backend developer "
        "with communication skills"
    )

    results = search_assessments(query)

    print("\nTop Results:\n")

    for i, item in enumerate(results, start=1):

        print(f"{i}. {item['name']}")
        print(item["url"])
        print()