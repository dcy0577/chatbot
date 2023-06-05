# chatbot
Chat with doc with memory base on langchain, Chromadb and Streamlit

### TODO ❗
- Currently there is no split document, as each htm(or md) is related to a topic. Splitting would break the contextual coherence - but then we would need a larger number of tokens.
- Some topics are related, or even subordinate. But they are distributed in different documents. This raises two questions:
    - Indexes need to be created that reflect the logical structure of the document. Possible directions are the graph structure in [LLamaIndex](https://gpt-index.readthedocs.io/en/latest/index.html).
    - But if we do this, we will probably need to split the document. Currently we only return the top-2 documents based on semantic similarity, and due to the small number, we do not yet exceed the token limit. Assuming that the contextual information related to the question needs to be combined with many documents to answer, we need to index the relevant sections from different documents and build a tree index. This implies advanced splitting and indexing techniques.
    - Maybe split md base on heading -> Need store some subordinate relationship in meta data to guide indexing.
- Chromadb is relatively simple, need to test other vector database.
- Open source model instead of OpenAI -> https://github.com/nomic-ai/gpt4all 
