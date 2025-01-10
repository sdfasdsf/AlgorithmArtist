from rest_framework import serializers
import requests

# 1. 환경 변수에서 API 키 가져오기
config = dotenv_values(".env")
openai_api_key = config.get('OPENAI_API_KEY')
#openai_api_key = os.getenv("LLM_11_CAT_PROJECT")
#from getpass import getpass
#os.environ["OPENAI_API_KEY"] = getpass("OpenAI API key 입력: ")
# 외부데이터셋 API KEY이름 =# config.get("NAVER_CLIENT_ID")
moviedata_key =  config.get('http://www.omdbapi.com/?i=tt3896198&apikey=79649873')
os.environ["OPENAI_API_KEY"] = openai_api_key
# 2. 모델 초기화 (model)
# model = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)
# class AIRequestSerializer(serializers.Serializer):내부의 
# openai_api_key 는 ExternalAPIRequestSerializer(serializers.Serializer): 클래스 내부의 API_KEY 와 일치해야한다.
####

class ExternalAPIRequestSerializer(serializers.Serializer):
    openai_api_key = serializers.CharField(max_length=100)  # API 키를 받을 필드
    api_url = serializers.URLField()  # 호출할 외부 API의 URL 필드
    params = serializers.DictField(child=serializers.CharField())  # API 호출 시 추가할 파라미터 필드

# AI 엔진 요청을 위한 Serializer
class AIRequestSerializer(serializers.Serializer):
    prompt = serializers.CharField(max_length=255)  # AI 엔진에 보낼 프롬프트
    moviedata_key = serializers.CharField(max_length=100)  # OpenAI API 키
#API를 이용한 데이터 로드
moviedata_url = " 아직안정함 .json "
headers = {
    "Authorization": f"Bearer {moviedata_key}"  # Bearer 토큰 방식으로 API 키 전달
}

# 외부 API 호출 함수
def get_movies(query, display=80):
    params = {
        "query": query,
        "display": display
    }
    response = requests.get(moviedata_url, headers=headers, params=params)
    
    # 응답 데이터를 JSON으로 변환
    moviesdata = response.json()

    # JSON 파일로 저장
    with open('response.json', 'w', encoding='utf-8') as f:
        json.dump(moviesdata, f, ensure_ascii=False, indent=4)

    return moviedata
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

# 문서 로드 (loader)
loader = MoviesLoader(movies_data = movies_data)
docs = loader.load()

# 5. Chunking (문서 분할)
recursive_text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=100,            # 한 번에 처리할 텍스트 크기
    chunk_overlap=10,          # 분할된 텍스트 간 겹치는 부분의 크기
    length_function=len,       # 텍스트의 길이를 계산할 함수
    is_separator_regex=False   # 구분자가 정규식인지를 설정
)

# 문서를 분할하여 chunks를 생성
splits = recursive_text_splitter.split_documents(docs)

# 6. 임베딩 (Embedding)
embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")  # OpenAI의 텍스트 임베딩 모델 사용

# 토큰화된 문서를 모델에 입력하여 임베딩 벡터를 생성하고, 이를 평균하여 전체 문서의 벡터를 생성

# 7. 벡터 저장소 (Vector Store) 생성
vectorstore = FAISS.from_documents(documents=splits, embedding=embeddings)  # 분할된 문서와 임베딩을 이용해 FAISS 벡터 저장소 생성

# 8. 검색기 (Retriever) 생성
retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 10})  # 벡터 저장소에서 유사한 항목을 검색

# 9. 프롬프트 템플릿 정의
contextual_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a chatbot who recommends movies, please answer in Korean"),
    ("user", "Context: {context}\\n\\nQuestion: {question}")
])

# # 10. RAG 체인 구성
 # 디버깅을 위해 만든 클래스

 # 프롬프트 클래스 (response docs -> context)
class ContextToPrompt:
    def __init__(self, prompt_template):
        self.prompt_template = prompt_template
    def invoke(self, inputs):
        # response_docs 내용을 trim해줌 (가독성을 높여줌)
        if isinstance(inputs, list): # inputs가 list인 경우. 즉 여러개의 문서들이 검색되어 리스트로 전달된 경우
            context_text = "\n".join([doc.page_content for doc in inputs]) # \n을 구분자로 넣어서 한 문자열로 합쳐줌
        else:
            context_text = inputs # 리스트가 아닌경우는 그냥 리턴해줌
        # 프롬프트
        formatted_prompt = self.prompt_template.format_messages( # 템플릿의 변수에 삽입해줌
            context=context_text, # {context} 변수에 context_text, 즉 검색된 문서 내용을 삽입함
            question=inputs.get("question", "")
        )
        return formatted_prompt
 # Retriever 클래스 (query)
class RetrieverWrapper:
    def __init__(self, retriever):
        self.retriever = retriever
    def invoke(self, inputs):
        # 0단계 : query의 타입에 따른 전처리
        if isinstance(inputs, dict): # inputs가 딕셔너리 타입일경우, question 키의 값을 검색 쿼리로 사용
            query = inputs.get("question", "")
        else: # 질문이 문자열로 주어지면, 그대로 검색 쿼리로 사용
            query = inputs
        # 1단계 : query를 리트리버에 넣어주고, response_docs를 얻어모
        response_docs = self.retriever.get_relevant_documents(query) # 검색을 수행하고 검색 결과를 response_docs에 저장
        return response_docs
# RAG 체인 설정
rag_chain_debug = {
    'context':RetrieverWrapper(retriever),
    'prompt':ContextToPrompt(contextual_prompt),
    'llm':model
}
def generate_response(query_text: str, history: List[Dict[str, str]]):
    try:
        print(retriever.get_relevant_documents(query_text))
        # 1. 리트리버로 question에 대한 검색 결과를 response_docs에 저장함
        response_docs = rag_chain_debug["context"].invoke({"question": query_text})
        # 2. 컨텍스트 텍스트 추출
        context_text = "\n".join([doc.page_content for doc in response_docs])
        # 3. 메시지 구성
        messages = []
        # 시스템 메시지 추가
        messages.append(SystemMessage(content="Answer the user's questions using the provided context. And if user wants, please provide summary as well. "))
        # If the context does not contain the answer, say that you do not know.
        # 컨텍스트를 시스템 메시지로 추가
        messages.append(SystemMessage(content=f"Context:\n{context_text}"))
        # 대화 내역 추가
        for past_message in history:
            if past_message['role'] == 'user':
                messages.append(HumanMessage(content=past_message['content']))
            elif past_message['role'] == 'assistant':
                messages.append(AIMessage(content=past_message['content']))
        # 현재 사용자 메시지 추가
        messages.append(HumanMessage(content=query_text))
        # 4. LLM에 메시지 전달
        result = rag_chain_debug["llm"].invoke(messages)
        return result.content  # 결과 반환
    except Exception as e:
        print("Error in generate_response:", str(e))
        raise e  # 예외가 발생하면 처리하고, 적절한 메시지 반환
# serializer 직렬화 하는중
#__________________________________________
# 외부 API 데이터 조회 기능을 제공하는 메서드
class ExternalAPIService:
    def fetch_external_data(self, api_url, params=None, api_key=None):
        """외부 데이터 API를 호출하는 메서드"""
        try:
            headers = {
                'Authorization': f'Bearer {api_key}'  # API 키를 사용하여 인증
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

    def __init__(self, contextualprompt, api_key):
         self.prompt = contextual_prompt  # 프롬프트
         self.api_key = api_key  # API 키
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

 # 프롬프트 클래스 (response docs -> context)
class ContextToPrompt:
    def __init__(self, prompt_template):
        self.prompt_template = prompt_template
    def invoke(self, inputs):
        # response_docs 내용을 trim해줌 (가독성을 높여줌)
        if isinstance(inputs, list): # inputs가 list인 경우. 즉 여러개의 문서들이 검색되어 리스트로 전달된 경우
            context_text = "\n".join([doc.page_content for doc in inputs]) # \n을 구분자로 넣어서 한 문자열로 합쳐줌
        else:
            context_text = inputs # 리스트가 아닌경우는 그냥 리턴해줌
        # 프롬프트
        formatted_prompt = self.prompt_template.format_messages( # 템플릿의 변수에 삽입해줌
            context=context_text, # {context} 변수에 context_text, 즉 검색된 문서 내용을 삽입함
            question=inputs.get("question", "")
        )
        return formatted_prompt
 # Retriever 클래스 (query)
class RetrieverWrapper:
    def __init__(self, retriever):
        self.retriever = retriever
    def invoke(self, inputs):
        # 0단계 : query의 타입에 따른 전처리
        if isinstance(inputs, dict): # inputs가 딕셔너리 타입일경우, question 키의 값을 검색 쿼리로 사용
            query = inputs.get("question", "")
        else: # 질문이 문자열로 주어지면, 그대로 검색 쿼리로 사용
            query = inputs
        # 1단계 : query를 리트리버에 넣어주고, response_docs를 얻어모
        response_docs = self.retriever.get_relevant_documents(query) # 검색을 수행하고 검색 결과를 response_docs에 저장
        return response_docs
# RAG 체인 설정
rag_chain_debug = {
    'context':RetrieverWrapper(retriever),
    'prompt':ContextToPrompt(contextual_prompt),
    'llm':model
}
def generate_response(query_text: str, history: List[Dict[str, str]]):
    try:
        print(retriever.get_relevant_documents(query_text))
        # 1. 리트리버로 question에 대한 검색 결과를 response_docs에 저장함
        response_docs = rag_chain_debug["context"].invoke({"question": query_text})
        # 2. 컨텍스트 텍스트 추출
        context_text = "\n".join([doc.page_content for doc in response_docs])
        # 3. 메시지 구성
        messages = []
        # 시스템 메시지 추가
        messages.append(SystemMessage(content="Answer the user's questions using the provided context. And if user wants, please provide summary as well. "))
        # If the context does not contain the answer, say that you do not know.
        # 컨텍스트를 시스템 메시지로 추가
        messages.append(SystemMessage(content=f"Context:\n{context_text}"))
        # 대화 내역 추가
        for past_message in history:
            if past_message['role'] == 'user':
                messages.append(HumanMessage(content=past_message['content']))
            elif past_message['role'] == 'assistant':
                 messages.append(AIMessage(content=past_message['content']))
        # 현재 사용자 메시지 추가
        messages.append(HumanMessage(content=query_text))
        # 4. LLM에 메시지 전달
        result = rag_chain_debug["llm"].invoke(messages)
        return result.content  # 결과 반환
    except Exception as e:
        print("Error in generate_response:", str(e))
        raise e  # 예외가 발생하면 처리하고, 적절한 메시지 반환
# 
# #