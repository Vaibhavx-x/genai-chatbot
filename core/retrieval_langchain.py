from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document
from core.logging_config import logger
import os
import json
import time
from concurrent.futures import ThreadPoolExecutor
from faiss import IndexHNSWFlat

TAG = 'retrieval_langchain.py'
VECTOR_STORE_DIR = "./vector_stores/"
TOP_K = 3

# Timed execution decorator for monitoring performance
def timed_execution(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        logger.info(f"{TAG}: Execution time for {func.__name__}: {end_time - start_time:.2f}s")
        return result
    return wrapper

# Load data
def load_data_handbook():
    with open('data/handbook_from_md.json', 'r') as f:
        return json.load(f)

def load_data_direction():
    with open('data/direction_from_web.json', 'r') as f:
        return json.load(f)

# Embedding model setup
hf_embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Parallel processing for embeddings
def parallel_process(data, func, num_threads=4):
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        return list(executor.map(func, data))

# Precompute embeddings
def precompute_embeddings(data):
    texts = [f"{item['header']} - {item['content']}" for item in data]
    return parallel_process(texts, hf_embeddings.embed_query)

# Save embeddings to file
def save_embeddings(embeddings, output_file):
    with open(output_file, 'w') as f:
        json.dump(embeddings, f)

# Build or load vector store
def build_or_load_vector_store(data, name, file_path):
    """
    Build a new FAISS vector store or load an existing one from disk.
    """
    if os.path.exists(file_path):
        logger.info(f"{TAG}: Loading existing vector store for {name} from {file_path}")
        # Allow deserialization if the file is trusted
        return FAISS.load_local(file_path, hf_embeddings, allow_dangerous_deserialization=True)
    else:
        logger.info(f"{TAG}: Building new vector store for {name}")
        limited_data = data
        documents = [Document(page_content=f"{item['header']} - {item['content']}") for item in limited_data]
        logger.info(f"{TAG}: Total documents to be indexed in {name}: {len(documents)}")
        vector_store = FAISS.from_documents(documents, hf_embeddings)
        vector_store.save_local(file_path)  # Save the vector store to disk
        logger.info(f"{TAG}: indexing completed for {name}")
        return vector_store


# Optimize with HNSW for fast queries
def create_hnsw_index(vector_store, dimension, num_neighbors=32, ef_search=50):
    """
    Convert the existing FAISS index to an HNSW index for faster retrieval.
    """
    index = IndexHNSWFlat(dimension, num_neighbors)  # Initialize HNSW index
    index.hnsw.efSearch = ef_search                 # Set the efSearch parameter
    
    # Extract embeddings from the current index
    embeddings = vector_store.index.reconstruct_n(0, vector_store.index.ntotal)
    
    # Add embeddings to the HNSW index
    if embeddings is not None and len(embeddings) > 0:
        index.add(embeddings)
    
    # Replace the original index in the vector store
    vector_store.index = index
    logger.info(f"{TAG}:HSNW index created for {vector_store}")
    return vector_store

# Retrieve context from a vector store
def retrieve_context_from_store(query, vector_store, source_name, top_k=TOP_K):
    retriever = vector_store.as_retriever()
    results = retriever.invoke(query)[:top_k]
    logger.info(f"{TAG}: Retrieved Documents for Query '{query}' from {source_name}:")
    for i, doc in enumerate(results, start=1):
        logger.info(f"{TAG}: {i}. {doc.page_content}")
    return results

# Combined retrieval from both vector stores
@timed_execution
def retrieve_context(query):
    results_handbook = retrieve_context_from_store(query, vector_store_handbook, "handbook")
    results_direction = retrieve_context_from_store(query, vector_store_direction, "direction")
    combined_content = " ".join([doc.page_content for doc in results_handbook + results_direction])
    return combined_content

# Main setup
logger.info(f"{TAG}: Initializing embeddings and vector stores...")

# Data preparation
handbook_data = load_data_handbook()
direction_data = load_data_direction()

# Build vector stores
vector_store_handbook = build_or_load_vector_store(handbook_data, "handbook", os.path.join(VECTOR_STORE_DIR, "faiss_handbook_store"))
# vector_store_handbook = build_vector_store_from_embeddings(handbook_embeddings, handbook_data, "handbook")
vector_store_direction = build_or_load_vector_store(direction_data, "direction", os.path.join(VECTOR_STORE_DIR, "faiss_direction_store"))

# Optimize vector stores with HNSW
dimension = len(hf_embeddings.embed_query("dummy"))  # Example to get embedding dimension
vector_store_handbook = create_hnsw_index(vector_store_handbook, dimension)
vector_store_direction = create_hnsw_index(vector_store_direction, dimension)

logger.info(f"{TAG}: Vector stores are ready for querying.")



