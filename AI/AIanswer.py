#LLM & RAG 챗봇 생성 및 응답 생성
import json
import requests
import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_community.vectorstores import FAISS
from dotenv import dotenv_values
from langchain.schema import Document
from django.shortcuts import get_object_or_404
from articles.models import Article

def generate_response_with_setup(query_text: str):
    try:
        # 환경 변수에서 API 키 가져오기
        config = dotenv_values(".env")
        openai_api_key = config.get('OPENAI_API_KEY')
        moviedata_token = config.get('MOVIEDATA_TOKEN')
        os.environ["OPENAI_API_KEY"] = openai_api_key

        # 모델 초기화
        model = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)

        moviedata_url = "https://api.themoviedb.org/3/trending/movie/day?language=ko-KR"
        headers = {"Authorization": f"Bearer {moviedata_token}"} # Bearer 토큰 방식으로 API 키 전달

        # moviedata_url = "https://api.themoviedb.org/3"
        # search_movie_endpoint = f"{moviedata_url}/search/movie"

        
        # 외부 API 호출 함수
        def get_movies(page=1):
            
            params = {"page": page,}
            response = requests.get(moviedata_url, headers=headers, params=params)
            # 응답 데이터를 JSON으로 변환
            movies_data = response.json()
            # JSON 파일로 저장
            with open('response.json', 'w', encoding='utf-8') as f:
                json.dump(movies_data, f, ensure_ascii=False, indent=4)

            return movies_data
        
        movies_data = get_movies()
        
        class MoviesLoader:
            def __init__(self, movies_data):
                self.movies_data = movies_data

            def load(self):
                documents = [
                    Document(
                        page_content=item['title'] + item['overview'],
                        metadata={
                            "title": item['title'],
                            "release_date": item['release_date'],
                            "vote_average": item['vote_average'],
                            "id": item['id'],
                        }
                    )
                    for item in self.movies_data['results']
                ]
                return documents

        # 문서 로드
        loader = MoviesLoader(movies_data=movies_data)
        docs = loader.load()

        # 5. Chunking (문서 분할)
        recursive_text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=100,            # 한 번에 처리할 텍스트 크기
            chunk_overlap=10,          # 분할된 텍스트 간 겹치는 부분의 크기
            length_function=len,       # 텍스트의 길이를 계산할 함수
            is_separator_regex=False   # 구분자가 정규식인지를 설정
        )
        # 리뷰도 추가
        Movie_Review = Article.objects.values("movie_title", "rating" ,"content")
        movie_review_docs = [
            Document(
                page_content=item['content'],
                metadata={
                    "movie_title": item['movie_title'],
                    "rating": item['rating'],
                }
            )
            for item in Movie_Review
        ]
        # 문서를 분할하여 chunks를 생성
        splits = recursive_text_splitter.split_documents(docs)
        splits += recursive_text_splitter.split_documents(movie_review_docs)
        # 6. 임베딩 (Embedding)
        embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")
        # 7. 벡터 저장소 (Vector Store) 생성
        # 분할된 문서와 임베딩을 이용해 FAISS 벡터 저장소 생성
        vectorstore = FAISS.from_documents(documents=splits, embedding=embeddings)
        # 8. 검색기 (Retriever) 생성
        retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 10})

        # 9. 프롬프트 템플릿 정의
        contextual_prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a chatbot who recommends movies. Please answer the image and information of the movie you recommended in Korean"),
            ("user", "Context: {context}\\n\\nQuestion: {question}")
        ])
        class ContextToPrompt:
            def __init__(self, prompt_template):
                self.prompt_template = prompt_template

            def invoke(self, inputs):
                # response_docs 내용을 trim해줌 (가독성을 높여줌)
                if isinstance(inputs, list):  # inputs가 list인 경우. 즉 여러개의 문서들이 검색되어 리스트로 전달된 경우
                    # \n을 구분자로 넣어서 한 문자열로 합쳐줌
                    context_text = "\n".join([doc.page_content for doc in inputs])
                else:
                    context_text = inputs  # 리스트가 아닌경우는 그냥 리턴해줌
                    # 프롬프트
                formatted_prompt = self.prompt_template.format_messages(  # 템플릿의 변수에 삽입해줌
                    # {context} 변수에 context_text, 즉 검색된 문서 내용을 삽입함
                    context=context_text,
                    question=inputs.get("question", "")
                )
                return formatted_prompt
        # Retriever 클래스 (query)

        class RetrieverWrapper:
            def __init__(self, retriever):
                self.retriever = retriever

            def invoke(self, inputs):
                # 0단계 : query의 타입에 따른 전처리
                if isinstance(inputs, dict):  # inputs가 딕셔너리 타입일경우, question 키의 값을 검색 쿼리로 사용
                    query = inputs.get("question", "")
                else:  # 질문이 문자열로 주어지면, 그대로 검색 쿼리로 사용
                    query = inputs
                # 1단계 : query를 리트리버에 넣어주고, response_docs를 얻어모
                response_docs = self.retriever.get_relevant_documents(query)  # 검색을 수행하고 검색 결과를 response_docs에 저장
                return response_docs
        # 10. RAG 체인 구성
        rag_chain_debug = {
            'context': RetrieverWrapper(retriever),
            'prompt': ContextToPrompt(contextual_prompt),
            'llm': model
        }

        # 응답 생성
        response_docs = rag_chain_debug["context"].invoke({"question": query_text})
        context_text = "\n".join([doc.page_content for doc in response_docs])

        messages = [
            SystemMessage(content="Answer the user's questions using the provided context."),
            SystemMessage(content=f"Context:\n{context_text}")
        ]
        

        messages.append(HumanMessage(content=query_text))
        result = rag_chain_debug["llm"].invoke(messages)
        return result.content

    except Exception as e:
        print("Error:", str(e))
        return "An error occurred during response generation."