from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer  # Importing a sentence transformer for embeddings
import logging
# Setup logger
logger = logging.getLogger(__name__)

# Load the model outside of the function for efficiency
model = SentenceTransformer("BAAI/bge-base-en")

def get_score(resume_string, job_description_string):
    logger.info("Started getting similarity score")
    client = QdrantClient(":memory:")
    client.set_model("BAAI/bge-base-en")
    documents = [resume_string]
    client.add(
        collection_name="demo_collection",
        documents=documents,
    )

    search_result = client.query(
        collection_name="demo_collection", query_text=job_description_string
    )
    logger.info("Finished getting similarity score")
    return search_result
