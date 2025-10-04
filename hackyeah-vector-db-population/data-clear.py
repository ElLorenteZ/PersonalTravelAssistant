from pymilvus import connections, utility

# Configuration
MILVUS_HOST = "localhost"
MILVUS_PORT = "19530"
COLLECTION_NAME = "trip_reviews"

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

def clear_collection():
    """Drop the collection if it exists"""
    if utility.has_collection(COLLECTION_NAME):
        print(f"Dropping collection '{COLLECTION_NAME}'...")
        utility.drop_collection(COLLECTION_NAME)
        print(f"Collection '{COLLECTION_NAME}' has been deleted successfully!")
    else:
        print(f"Collection '{COLLECTION_NAME}' does not exist.")

def main():
    # Connect to Milvus
    connect_to_milvus()

    # Clear collection
    clear_collection()

    print("\nVector database cleared!")

if __name__ == "__main__":
    main()
