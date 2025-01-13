import json
import os
import requests
from dotenv import dotenv_values
from rest_framework import serializers
from langchain_openai import ChatOpenAI, OpenAIEmbeddings # type: ignore
from langchain.schema import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_community.vectorstores import FAISS
from langchain.vectorstores.base import VectorStore
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.runnables import RunnablePassthrough
from langchain.chains import LLMChain
import openai
from typing import List, Dict

# 1. 환경 변수에서 API 키 가져오기
config = dotenv_values(".env")  # 환경변수 파일 경로 수정
openai_api_key = config.get('OPENAI_API_KEY')
moviedata_key = config.get('MOVIEDATA_API_KEY')  # API 키 이름에 맞게 수정
os.environ["OPENAI_API_KEY"] = openai_api_key

# 외부 API 호출 함수
def get_movies(query, display=80):
    moviedata_url = "http://www.omdbapi.com/"  # 실제 API URL로 수정
    headers = {
        "Authorization": f"Bearer {moviedata_key}"
    }
    params = {
        "query": query,
        "display": display
    }
    response = requests.get(moviedata_url, headers=headers, params=params)
    moviesdata = response.json()

    # 응답 데이터를 JSON으로 저장
    with open('response.json', 'w', encoding='utf-8') as f:
        json.dump(moviesdata, f, ensure_ascii=False, indent=4)

    return moviesdata

# MoviesLoader 클래스 수정 (Document import 추가)
class MoviesLoader:
    def __init__(self, movies_data):
        self.movies_data = movies_data

    def load(self):
        documents = [
            Document(
                page_content=item['title'] + item['link'],
                metadata={
                    "link": item['link'],
                    "description": item['description'],
                    "pubDate": item['pubDate']
                }
            )
            for item in self.movies_data['items']
        ]
        return documents

# 5. Chunking (문서 분할)
recursive_text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=100,  # 한 번에 처리할 텍스트 크기
    chunk_overlap=10,  # 분할된 텍스트 간 겹치는 부분의 크기
    length_function=len,
    is_separator_regex=False
)

# 문서 로드 (loader)
movies_data = get_movies("action movies")  # 영화 데이터 가져오기 예시
loader = MoviesLoader(movies_data=movies_data)
docs = loader.load()

# 문서를 분할하여 chunks를 생성
splits = recursive_text_splitter.split_documents(docs)

# 6. 임베딩 (Embedding)
embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")

# 7. 벡터 저장소 (Vector Store) 생성
vectorstore = FAISS.from_documents(documents=splits, embedding=embeddings)

# 8. 검색기 (Retriever) 생성
retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 10})

# 9. 프롬프트 템플릿 정의
contextual_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a chatbot who recommends movies, please answer in Korean"),
    ("user", "Context: {context}\\n\\nQuestion: {question}")
])

# 10. RAG 체인 구성 (디버깅을 위해 만든 클래스)
class ContextToPrompt:
    def __init__(self, prompt_template):
        self.prompt_template = prompt_template

    def invoke(self, inputs):
        if isinstance(inputs, list):
            context_text = "\n".join([doc.page_content for doc in inputs])
        else:
            context_text = inputs
        formatted_prompt = self.prompt_template.format_messages(
            context=context_text,
            question=inputs.get("question", "")
        )
        return formatted_prompt

class RetrieverWrapper:
    def __init__(self, retriever):
        self.retriever = retriever

    def invoke(self, inputs):
        if isinstance(inputs, dict):
            query = inputs.get("question", "")
        else:
            query = inputs
        response_docs = self.retriever.get_relevant_documents(query)
        return response_docs

# 모델 초기화
model = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.3)

# RAG 체인 설정
rag_chain_debug = {
    'context': RetrieverWrapper(retriever),
    'prompt': ContextToPrompt(contextual_prompt),
    'llm': model
}

def generate_response(query_text: str, history: List[Dict[str, str]]):
    try:
        response_docs = rag_chain_debug["context"].invoke({"question": query_text})
        context_text = "\n".join([doc.page_content for doc in response_docs])
        messages = [SystemMessage(content=f"Context:\n{context_text}")]
        for past_message in history:
            if past_message['role'] == 'user':
                messages.append(HumanMessage(content=past_message['content']))
            elif past_message['role'] == 'assistant':
                messages.append(AIMessage(content=past_message['content']))
        messages.append(HumanMessage(content=query_text))
        result = rag_chain_debug["llm"].invoke(messages)
        return result.content
    except Exception as e:
        print("Error in generate_response:", str(e))
        raise e

    
# serializer 직렬화 하는중
#__________________________________________
# 외부 API 데이터 조회 기능을 제공하는 메서드

# 2. ExternalAPIService 클래스 수정
class ExternalAPIService:
    def fetch_external_data(self, api_url, params=None):
        """외부 데이터 API를 호출하는 메서드"""
        try:
            headers = {
                'Authorization': f'Bearer {moviedata_key}'  # 환경 변수에서 가져온 API 키 사용
            }
            response = requests.get(api_url, params=params, headers=headers)  # GET 요청
            response.raise_for_status()  # 오류 발생 시 예외 처리
            return response.json()  # 응답을 JSON 형식으로 반환
        except requests.exceptions.RequestException as e:
            return f"Error: {str(e)}"
#______________________________
# AI 서비스 호출 기능을 제공하는 메서드
class AIService(serializers.Serializer):
    # Meta 클래스를 사용하여 AI 모델의 필드 설정
    class Meta:
        model = AI  # AI 모델 지정
        fields = ['user_question', 'bot_response', 'created_at']  # 필요한 필드들

    def __init__(self, contextualprompt):
         self.prompt = contextualprompt  # 프롬프트
         self.api_key = openai_api_key  # 환경 변수에서 가져온 OpenAI API 키 사용

    def query_ai_engine(self):
        """AI 엔진에 프롬프트를 보내고 응답을 받는 메서드"""
        try:
            import openai
            openai.api_key = self.api_key  # 환경 변수에서 가져온 OpenAI API 키 설정
            response = openai.Completion.create(
                engine="text-davinci-003",  # 사용하려는 모델
                prompt=self.prompt,  # 사용자의 프롬프트
                max_tokens=150
            )
            return response.choices[0].text.strip()  # 생성된 텍스트 반환
        except Exception as e:
            return f"Error: {str(e)}"
#________________________________________
    def query_ai_engine(self):
        """AI 엔진에 프롬프트를 보내고 응답을 받는 메서드"""
        try:
            openai.api_key = self.api_key  # API 키 설정
            response = openai.Completion.create(
                engine="text-davinci-003",  # 사용하려는 모델
                prompt=self.prompt,  # 사용자의 프롬프트
                max_tokens=150
            )
            return response.choices[0].text.strip()  # 생성된 텍스트 반환
        except Exception as e:
            return f"Error: {str(e)}"
#___________________________________________________________________
    def get_ai_data(self):
        """모델 데이터와 응답을 결합하여 반환하는 메서드"""
        # 예시: AI 모델에서 데이터를 불러오는 과정
        ai_instance = AI.objects.create(user_question=self.prompt)  # 질문을 저장
        ai_instance.bot_response = self.query_ai_engine()  # 챗봇 응답
        ai_instance.save()  # 모델 저장
        return ai_instance  # AI 인스턴스 반환
    
    
#________________________________________________########
# 
# 예전 코드  ai 코드들
# # 10. RAG 체인 구성
 # 디버깅을 위해 만든 클래스