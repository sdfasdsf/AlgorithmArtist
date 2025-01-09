import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage
from langchain_community.vectorstores import FAISS
from langchain.vectorstores.base import VectorStore
from langchain_core.prompts import ChatPromptTemplate 
from langchain.text_splitter import CharacterTextSplitter
from langchain_core.runnables import RunnablePassthrough
from langchain.chains import LLMchain

# API 키 설정
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# 모델 초기화
model = ChatOpenAI(model="gpt-4o-mini")

# 문서 리스트, 임베딩 함수 사용하여 FAISS 벡터 저장소 생성
text_splitter = CharacterTextSplitter(
    chunk_size=100,
    chunk_overlap=10,
    length_fuction=len,
    is_separator_regex=False,
)

splits = text_splitter.split
vectorstore = FAISS.from_documents(documents=splits, embedding=embeddings)

#
retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 4})

# 프롬프트 템플릿 정의
contextual_prompt = ChatPromptTemplate.from_messages([
    ("system", "Answer the question using only the following context."),
    ("user", "Context: {context}\\n\\nQuestion: {question}")
])

class SimplepassThrough:
    def invoke(self, inputs, **kwargs):
        return inputs
    
class ContextoPrompt:
    def __init__(self, prompt_template):
        self.prompt_template = prompt_template

# Retriever를 invoke() 메서드로 래핑하는 클래스 정의
class RetrieverWrapper:
    def __init__(self, retriever):
        self.retriever = retriever

    def invoke(self, inputs):
        if isinstance(inputs, dict):
            query = inputs.get("question", "")
        else:
            query = inputs
        # 검색 수행
        response_docs = self.retriever.get_relevant_documents(query)
        return response_docs

llm_chain = LLMchain(llm=model, prompt=contextual_prompt)

# RAG 체인 설정
rag_chain_debug = {
    "context": RetrieverWrapper(retriever),
    "prompt": ContextoPrompt(contextual_prompt),
    "llm": model
}

# 챗봇 구동
while True:
    print("========================")
    query = input("질문을 입력하세요 : ")
    
    # 1. Retriever로 관련 문서 검색
    response_docs = rag_chain_debug["context"].invoke({"question": query})
    
    # # 2. 문서를 프롬프트로 변환
    prompt_messages = rag_chain_debug["prompt"].invoke({
        "context": response_docs,
        "question": query
    })
    
    # # 3. LLM으로 응답 생성
    response = rag_chain_debug["llm"].invoke(prompt_messages)
    
    print("\n답변:")
    print(response.content)

