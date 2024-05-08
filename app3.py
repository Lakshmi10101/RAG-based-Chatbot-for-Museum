from langchain.prompts import PromptTemplate
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain_openai import OpenAI
import chainlit as cl

import yaml

DB_FAISS_PATH = 'faiss_vectorstore/'


custom_prompt_template = """You are a musuem guide. Use the following template to answer the user's question.
If you don't know the answer, just say that you don't know, don't try to make up an answer.

Context: {context}
Question: {question}

Only return the helpful answer below and nothing else.
Helpful answer:
"""

OPENAI_CONFIG_FILE = 'api_key.yaml'

with open(OPENAI_CONFIG_FILE, 'r') as f:
    config = yaml.safe_load(f)

apikey = config['openai']['access_key']


def set_custom_prompt():
    """
    Prompt template for QA retrieval for each vectorstore
    """
    prompt = PromptTemplate(template=custom_prompt_template,
                            input_variables=['context', 'question'])
    return prompt

# Retrieval QA Chain
def retrieval_qa_chain(llm, prompt, db):
    qa_chain = RetrievalQA.from_chain_type(llm=llm,
                                       chain_type='stuff',
                                       retriever=db.as_retriever(search_kwargs={'k': 5}),
                                       return_source_documents=True,
                                       chain_type_kwargs={'prompt': prompt}
                                       )
    return qa_chain

# Loading the LLM model
def load_llm():
    # Load the locally downloaded model here
    llm = OpenAI(openai_api_key=apikey)
    return llm

# QA Model Function
def qa_bot():
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2",
                                       model_kwargs={'device': 'cpu'})
    db = FAISS.load_local(DB_FAISS_PATH, embeddings)
    llm = load_llm()
    qa_prompt = set_custom_prompt()
    qa = retrieval_qa_chain(llm, qa_prompt, db)

    return qa

# Formulating response
def final_result(query):
    qa_result = qa_bot()
    response = qa_result({'query': query})
    return response

# Chainlit starter code
@cl.on_chat_start
async def start():
    chain = qa_bot()
    msg = cl.Message(content="Starting the chatbot...")
    await msg.send()
    msg.content = "Hi, Welcome to Chhatrapati Shivaji Maharaj Vastu Sangrahalaya."
    await msg.update()

    cl.user_session.set("chain", chain)


# Called every time user inputs a query
@cl.on_message
async def main(user_input: cl.Message):
    chain = cl.user_session.get("chain") 
    cb = cl.AsyncLangchainCallbackHandler(
        stream_final_answer=True, answer_prefix_tokens=["FINAL", "ANSWER"]
    )
    cb.answer_reached = True
    response = await chain.acall(user_input.content, callbacks=[cb])
    answer = response["result"]
    print(answer)
    sources = response["source_documents"]

    if not sources:
        answer += "\nNo sources found"
# =============================================================================
#     if sources:
#         answer += f"\nSources:" + str(sources)
#     else:
#         answer += "\nNo sources found"
# =============================================================================
        
    await cl.Message(content=answer).send()
