import os
import requests
from dotenv import load_dotenv
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.schema import Document

# 1. 환경 변수에서 API 키 가져오기
load_dotenv()  # .env 파일에서 환경 변수 로드

openai_api_key = os.getenv('OPENAI_API_KEY')
movie_api_key = os.getenv('MOVIE_API_KEY')
os.environ["OPENAI_API_KEY"] = openai_api_key

# 2. 모델 초기화
model = OpenAI(model="gpt-4", temperature=0.3)

# 3. TMDb API를 이용한 영화 데이터 로드
TMDB_API_URL = "https://api.themoviedb.org/3/search/movie"
headers = {"Authorization": f"Bearer {movie_api_key}"}

def get_movie_data(query):
    params = {"query": query, "api_key": movie_api_key}
    response = requests.get(TMDB_API_URL, headers=headers, params=params)
    movie_data = response.json()
    
    if movie_data['results']:
        return movie_data['results'][0]  # 가장 첫 번째 영화 데이터 반환
    return None

# 4. Langchain을 이용한 영화 데이터 처리
class MovieDataLoader:
    def __init__(self, movie_data):
        self.movie_data = movie_data
    
    def load(self):
        documents = [
            {
                "content": self.movie_data['title'] + " " + self.movie_data['overview'],
                "metadata": {
                    "title": self.movie_data['title'],
                    "release_date": self.movie_data['release_date'],
                    "overview": self.movie_data['overview']
                }
            }
        ]
        return documents

# 5. Chunking (문서 분할)
def chunk_text(text):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    return text_splitter.split_text(text)

# 6. 임베딩 (Embedding)
embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")

# 7. 벡터 저장소 (Vector Store) 생성
def create_vector_store(chunks):
    documents = [Document(page_content=chunk) for chunk in chunks]  # chunks를 Document 객체로 변환
    return FAISS.from_documents(documents=documents, embedding=embeddings)

# 8. 검색기 (Retriever) 생성
def create_retriever(vector_store):
    return vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 5})

# 9. 프롬프트 템플릿 정의
contextual_prompt = PromptTemplate.from_template(
    "You are a professional chatbot that answers movie-related questions. Please answer the user's questions kindly.\n\nContext: {context}\n\nQuestion: {question}"
)

# 10. RAG 체인 구성
class SimplePassThrough:
    def invoke(self, inputs, **kwargs):
        return inputs

class ContextToPrompt:
    def __init__(self, prompt_template):
        self.prompt_template = prompt_template

    def invoke(self, inputs):
        if isinstance(inputs, dict):  # inputs가 dict일 때
            context_text = inputs.get('context', '')
            question_text = inputs.get('question', '')
        else:
            context_text = inputs  # 그냥 문자열일 경우
            question_text = ""
        formatted_prompt = self.prompt_template.format_messages(
            context=context_text,
            question=question_text
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

# RAG 체인 설정
rag_chain = {
    'context': RetrieverWrapper(create_retriever(create_vector_store(chunk_text(get_movie_data("Inception")['overview'])))),
    'prompt': ContextToPrompt(contextual_prompt),
    'llm': model
}

def process_movie_query(movie_name, user_question):
    # TMDb API에서 영화 데이터를 로드
    movie_data = get_movie_data(movie_name)
    if not movie_data:
        return "Movie not found."

    # 영화 데이터 처리
    loader = MovieDataLoader(movie_data)
    docs = loader.load()

    # 문서 분할 (Chunking)
    chunks = chunk_text(docs[0]['content'])

    # 벡터 저장소 생성 및 검색기 설정
    vector_store = create_vector_store(chunks)
    retriever = create_retriever(vector_store)

    # RAG 체인 실행
    context = retriever.invoke({"question": user_question})
    prompt = ContextToPrompt(contextual_prompt).invoke({"context": context, "question": user_question})
    
    # AI 모델로 답변 생성
    answer = model(prompt)
    return answer
