import os
from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.document_loaders import UnstructuredMarkdownLoader, UnstructuredHTMLLoader
from langchain.text_splitter import CharacterTextSplitter, RecursiveCharacterTextSplitter, Language, SpacyTextSplitter, NLTKTextSplitter, MarkdownTextSplitter

input_folder_path = "/home/dchangyu/LLM_experiments/data_markdown"
persist_directory = '/home/dchangyu/chatbot/streamlit/db'
# Embeddings
embeddings = HuggingFaceEmbeddings(model_name="all-mpnet-base-v2")

def ingest():
    # Load the documents
    documents = []
    for file in os.listdir(input_folder_path):
        if file.endswith('.md'):
            md_path = os.path.join(input_folder_path, file)
            loader = UnstructuredMarkdownLoader(md_path)
            documents.extend(loader.load())

    # Text Splitter
    # text_splitter = RecursiveCharacterTextSplitter.from_language(language=Language.MARKDOWN, chunk_size=2000, chunk_overlap=0)
    # # text_splitter = NLTKTextSplitter(chunk_size=1000)

    # no splitting
    docs = [doc for doc in documents]

    # Create the vectorized db
    db = Chroma.from_documents(documents=docs, 
                            embedding=embeddings, 
                            persist_directory=persist_directory)
    db.persist()

if __name__ == "__main__":
    ingest()
