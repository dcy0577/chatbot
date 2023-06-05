import os
import sys
sys.path.append(os.path.abspath('.'))
from typing import Any, List
from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.document_loaders import UnstructuredMarkdownLoader, UnstructuredHTMLLoader, TextLoader
from langchain.text_splitter import CharacterTextSplitter, RecursiveCharacterTextSplitter, Language, SpacyTextSplitter, NLTKTextSplitter, MarkdownTextSplitter

input_folder_path = "/home/dchangyu/LLM_experiments/data_markdown"
# persist_directory = '/home/dchangyu/chatbot/streamlit/db_chunk2000_overlap200'
persist_directory = 'streamlit/db_no_split_text'
# Embeddings
embeddings = HuggingFaceEmbeddings(model_name="all-mpnet-base-v2")

class MarkdownTextSplitter_new(RecursiveCharacterTextSplitter):
    """Attempts to split the text along Markdown-formatted headings."""

    def __init__(self, separators: List[str], **kwargs: Any):
        """Initialize a MarkdownTextSplitter."""
        super().__init__(separators=separators, **kwargs)

def ingest():
    # Load the documents
    documents_md = []
    documents_text = []
    for file in os.listdir(input_folder_path):
        if file.endswith('.md'):
            md_path = os.path.join(input_folder_path, file)
            # this will lost the markdown format
            # loader_md = UnstructuredMarkdownLoader(md_path)
            loader_txt = TextLoader(md_path, encoding="utf-8")
            # md = loader_md.load()
            # documents_md.extend(md)
            # print(md[0].page_content)
            txt = loader_txt.load()
            documents_text.extend(txt)
            print(txt[0].page_content)
            

    # Text Splitter
    # not working good
    # text_splitter = MarkdownTextSplitter_new(["# ","\n## ", "\n### ","\n#### ", "\n##### ", "\n###### ","\n\n", " ", ""], chunk_size=2000, chunk_overlap=200)
    # text_splitter = RecursiveCharacterTextSplitter.from_language(language=Language.MARKDOWN, chunk_size=2000, chunk_overlap=0)
    # text_splitter = NLTKTextSplitter(chunk_size=1000)

    # no splitting
    docs = [doc for doc in documents_text]

    # with splitting
    # docs = text_splitter.split_documents(documents_text)

    # print(len(docs))
    # for i in docs:
    #     print(i.page_content)
    #     print("=====================================")
    

    # Create the vectorized db
    db = Chroma.from_documents(documents=docs, 
                            embedding=embeddings, 
                            persist_directory=persist_directory)
    db.persist()

if __name__ == "__main__":
    ingest()
