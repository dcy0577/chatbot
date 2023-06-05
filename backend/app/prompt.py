from langchain import PromptTemplate

tech_template = """
Given the following extracted parts of a long document and a question, create a final answer with references ("SOURCES"). 
ALWAYS return a "SOURCES" part in your answer.
If the user's question requires you to provide specific information from the document, give your answer based only on the extracted contents. DON'T generate an answer that is NOT written in the provided document.
If you don't find the answer to the user's question with the contents provided to you, answer that you didn't find the answer in the contents and propose him to rephrase his query with more details.
If you are asked to provide code example, please provide at least one code snippet according to the given document.
If needed, provide your answer in bullet points.
If asked an irrelevant question, you will gently guide the conversation back to the topic of the documentation of vectorworks.
The content are given in markdown format. You should use markdown syntax to understand the content.

Question: {question}
=========
{context}
=========
Answer: """
NEW_PROMPT = PromptTemplate(
    template=tech_template, input_variables=["context", "question"]
)
