from llama_index.core import VectorStoreIndex, Document, Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

def build_index(parsed_resumes):
    embed_model = HuggingFaceEmbedding(model_name="all-MiniLM-L6-v2")
    Settings.embed_model = embed_model
    documents = [Document(text=str(r)) for r in parsed_resumes]
    return VectorStoreIndex.from_documents(documents)

def query_index(index, jd_text, top_k=20):
    query_engine = index.as_query_engine(similarity_top_k=top_k)
    response = query_engine.query(jd_text)
    return [node.text for node in response.source_nodes]