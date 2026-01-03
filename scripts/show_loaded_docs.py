import os
import sys
from pathlib import Path
import chromadb

# Add the project root directory to the python path to reuse your logic
project_root = Path(__file__).parent.parent.absolute()
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


def list_stored_documents(chroma_db_path = "./chroma_db", collection_name = "uploaded_docs"):
    """
    Connects to ChromaDB and prints a list of all unique documents.
    """
    # 1. Initialize the Persistent Client
    client = chromadb.PersistentClient(path = chroma_db_path)

    try:
        # 2. Get the collection (adjust the name if you used a specific one)
        collection = client.get_collection(name = collection_name)

        # 3. Retrieve metadata for all entries
        # We only need 'metadatas' to identify files
        results = collection.get(include = ["metadatas"])
        metadatas = results.get('metadatas', [])

        if not metadatas:
            print("No documents found in the database.")
            return

        # 4. Extract unique document names
        # Based on your ingest script, look for 'document_name' or 'company_name'
        unique_docs = set()
        for meta in metadatas:
            # You can customize which metadata field to display
            doc_name = meta.get('document_name')
            company = meta.get('company_name')

            unique_docs.add(f"{company} - {doc_name}")

        print(f"--- Found {len(unique_docs)} Unique Documents ---")
        for doc in sorted(unique_docs):
            print(f"- {doc}")

    except Exception as e:
        print(f"Error accessing collection '{collection_name}': {e}")


if __name__ == "__main__":
    # Config Database folder
    chroma_db_parent_folder = Path(__file__).parents[1]
    chroma_db_final_folder = "/chroma_db"
    chroma_db_path = f"{chroma_db_parent_folder}{chroma_db_final_folder}"

    # Run the list function
    list_stored_documents(chroma_db_path = chroma_db_path)