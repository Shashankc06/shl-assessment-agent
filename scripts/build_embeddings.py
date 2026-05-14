import json
import faiss
import numpy as np

from sentence_transformers import SentenceTransformer

# Load embedding model
model = SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2"
)

# Load scraped catalog
with open(
    "data/shl_catalog.json",
    "r",
    encoding="utf-8"
) as f:

    assessments = json.load(f)

# Prepare text for embeddings
documents = []

for item in assessments:

    text = f"""
    Name: {item['name']}
    Description: {item['description']}
    """

    documents.append(text)

print(f"Loaded {len(documents)} documents")

# Generate embeddings
embeddings = model.encode(
    documents,
    show_progress_bar=True
)

embeddings = np.array(
    embeddings,
    dtype="float32"
)

# Create FAISS index
dimension = embeddings.shape[1]

index = faiss.IndexFlatL2(dimension)

index.add(embeddings)

# Save FAISS index
faiss.write_index(
    index,
    "data/shl_faiss.index"
)

# Save metadata
with open(
    "data/shl_metadata.json",
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        assessments,
        f,
        indent=2,
        ensure_ascii=False
    )

print("FAISS index created!")
print(f"Indexed {len(assessments)} assessments")