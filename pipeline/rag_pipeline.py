from llama_index import GPTVectorStoreIndex, SimpleDirectoryReader

def build_rag_pipeline(documents):
    reader = SimpleDirectoryReader(documents)
    docs = reader.load_data()
    index = GPTVectorStoreIndex.from_documents(docs)
    return index

def query_rag(index, query):
    response = index.query(query)
    return response
