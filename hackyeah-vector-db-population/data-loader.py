import os
import glob
from pymilvus import connections, Collection, FieldSchema, CollectionSchema, DataType, utility
from sentence_transformers import SentenceTransformer

# Configuration
MILVUS_HOST = "localhost"
MILVUS_PORT = "19530"
COLLECTION_NAME = "trip_reviews"
DIMENSION = 384  # all-MiniLM-L6-v2 embedding dimension
DOCS_PATH = "../hackyeah-history-trips/*.md"

def connect_to_milvus():
    """Connect to Milvus vector database"""
    print(f"Connecting to Milvus at {MILVUS_HOST}:{MILVUS_PORT}...")
    connections.connect(
        alias="default",
        host=MILVUS_HOST,
        port=MILVUS_PORT,
        timeout=30
    )
    print("Connected successfully!")

def create_collection():
    """Create collection if it doesn't exist"""
    if utility.has_collection(COLLECTION_NAME):
        print(f"Collection '{COLLECTION_NAME}' already exists. Dropping it...")
        utility.drop_collection(COLLECTION_NAME)

    # Define schema
    fields = [
        FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
        FieldSchema(name="filename", dtype=DataType.VARCHAR, max_length=256),
        FieldSchema(name="content", dtype=DataType.VARCHAR, max_length=65535),
        FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=DIMENSION)
    ]

    schema = CollectionSchema(fields=fields, description="Trip reviews collection")
    collection = Collection(name=COLLECTION_NAME, schema=schema)

    # Create index
    index_params = {
        "metric_type": "L2",
        "index_type": "IVF_FLAT",
        "params": {"nlist": 128}
    }
    collection.create_index(field_name="embedding", index_params=index_params)
    print(f"Collection '{COLLECTION_NAME}' created successfully!")

    return collection

def load_documents():
    """Load all markdown documents from the directory"""
    print(f"Loading documents from {DOCS_PATH}...")
    docs = []

    for filepath in glob.glob(DOCS_PATH):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            filename = os.path.basename(filepath)
            docs.append({
                'filename': filename,
                'content': content
            })
            print(f"  Loaded: {filename}")

    print(f"Total documents loaded: {len(docs)}")
    return docs

def generate_embeddings(documents, model_name='all-MiniLM-L6-v2'):
    """Generate embeddings for documents using SentenceTransformer"""
    print(f"Generating embeddings using {model_name}...")
    model = SentenceTransformer(model_name)

    texts = [doc['content'] for doc in documents]
    embeddings = model.encode(texts, show_progress_bar=True)

    return embeddings

def insert_data(collection, documents, embeddings):
    """Insert documents and embeddings into Milvus"""
    print("Inserting data into Milvus...")

    data = [
        [doc['filename'] for doc in documents],
        [doc['content'] for doc in documents],
        embeddings.tolist()
    ]

    collection.insert(data)
    collection.flush()
    print(f"Inserted {len(documents)} documents successfully!")

def main():
    # Connect to Milvus
    print("Connecting to Milvus")
    connect_to_milvus()

    # Create collection
    print("Creating collection")
    collection = create_collection()

    # Load documents
    print("Loading documents")
    documents = load_documents()

    if not documents:
        print("No documents found!")
        return

    # Generate embeddings
    print("Generating embeddings")
    embeddings = generate_embeddings(documents)

    # Insert data
    print("Inserting data")
    insert_data(collection, documents, embeddings)

    # Load collection
    collection.load()
    print(f"\nCollection loaded and ready for queries!")
    print(f"Total entities: {collection.num_entities}")

if __name__ == "__main__":
    main()
