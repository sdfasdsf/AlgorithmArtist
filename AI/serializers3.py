"""
import openai
import os
import json
import requests
from dotenv import dotenv_values
from typing import List, Dict
from langchain.prompts import ChatPromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

import os
from dotenv import dotenv_values

# 1. 환경 변수에서 API 키 가져오기
config = dotenv_values(".env")  # .env 파일에서 설정된 변수 읽기

# MOVIEDATA_API_KEY와 OPENAI_API_KEY 가져오기
moviedata_key = config.get('MOVIEDATA_API_KEY')  # MOVIEDATA_API_KEY 가져오기
openai_api_key = config.get('OPENAI_API_KEY')    # OPENAI_API_KEY 가져오기

# API 키가 설정되지 않은 경우 예외 발생
if not moviedata_key:
    raise ValueError("MOVIEDATA_API_KEY is not set in the environment.")

if not openai_api_key:
    raise ValueError("OPENAI_API_KEY is not set in the environment.")

# OpenAI API 키로 설정
os.environ["OPENAI_API_KEY"] = openai_api_key

# 영화 데이터 API 키 설정
os.environ["MOVIEDATA_API_KEY"] = moviedata_key

# 외부 API 호출 함수 (영화 데이터를 가져오는 부분)
def get_movies(query, display=80):
    try:
        # OpenAI API를 호출하여 영화 추천 결과를 받음
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant who recommends movies."},
                {"role": "user", "content": f"추천해주세요: {query}"}
            ]
        )

        # 응답에서 영화 목록을 JSON 형태로 파싱 (기본적으로 string 형태로 올 수 있음)
        moviesdata = response['choices'][0]['message']['content']
        
        # 예시 영화 데이터 형태
        # 여기서 실제로 받은 데이터를 알맞게 구조화해야 할 수 있습니다.
        # 예시로, 아래와 같이 'items'와 같은 형태로 데이터를 만들어주었습니다.
        movies_data_json = {
            "items": [
                {
                    "title": "Movie Title 1",
                    "link": "https://example.com/movie1",
                    "description": "Description for movie 1",
                    "pubDate": "2025-01-01"
                },
                {
                    "title": "Movie Title 2",
                    "link": "https://example.com/movie2",
                    "description": "Description for movie 2",
                    "pubDate": "2025-01-02"
                }
            ]
        }

        # 응답 데이터를 JSON으로 저장
        with open('response.json', 'w', encoding='utf-8') as f:
            json.dump(movies_data_json, f, ensure_ascii=False, indent=4)

        return movies_data_json
    except Exception as e:
        print("Error in get_movies:", str(e))
        raise e


# MoviesLoader 클래스 수정 (Document import 추가)
class MoviesLoader:
    def __init__(self, movies_data):
        self.movies_data = movies_data

    def load(self):
        # movies_data에서 'items' 키로 데이터를 가져옴
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
        외부 데이터 API를 호출하는 메서드
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
      #AI 엔진에 프롬프트를 보내고 응답을 받는 메서드
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
        #AI 엔진에 프롬프트를 보내고 응답을 받는 메서드
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
        
    def get_movie_info(self):
        #영화 제목, 감독, 장르 등의 정보를 Movie 모델에서 가져오는 메서드
        # 영화 추천 시 또는 감독별 영화 찾기
        if '감독' in self.user_question:
            director = self.user_question.split()[-1]  # 사용자가 요청한 감독
            movies = Movie.objects.filter(director__icontains=director)
            return [movie.title for movie in movies] if movies else "해당 감독의 영화를 찾을 수 없습니다."
        elif '추천' in self.user_question or '인기' in self.user_question:
            movie = Movie.objects.order_by('?').first()  # 랜덤 영화 추천
            return {
                'title': movie.title,
                'genre': movie.genre,
                'description': movie.description
            }
        else:
            return None

    def get_ai_data(self):
    #    AI 응답과 영화 정보를 결합하여 반환하는 메서드
        # 영화 정보 가져오기
        movie_info = self.get_movie_info()
        if movie_info:
            # 영화 관련 응답을 생성
            movie_response = f"추천하는 영화: {movie_info.get('title', '')}\n장르: {movie_info.get('genre', '')}\n설명: {movie_info.get('description', '')}"
            self.bot_response = movie_response
        else:
            # OpenAI 응답 생성
            self.bot_response = self.query_ai_engine()

        # AI 응답을 DB에 저장
        ai_instance = AI.objects.create(user_question=self.user_question, bot_response=self.bot_response)
        ai_instance.save()
        return ai_instance
        
        
#___________________________________________________________________
    def get_ai_data(self):
        #모델 데이터와 응답을 결합하여 반환하는 메서드
        # 예시: AI 모델에서 데이터를 불러오는 과정
        ai_instance = AI.objects.create(user_question=self.prompt)  # 질문을 저장
        ai_instance.bot_response = self.query_ai_engine()  # 챗봇 응답
        ai_instance.save()  # 모델 저장
        return ai_instance  # AI 인스턴스 반환
    
    """
#________________________________________________########
# 
# 예전 코드  ai 코드들
# # 10. RAG 체인 구성
 # 디버깅을 위해 만든 클래스