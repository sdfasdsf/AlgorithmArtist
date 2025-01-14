import json
from rest_framework import serializers
import requests
import os
from langchain.text_splitter import RecursiveCharacterTextSplitter, CharacterTextSplitter
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_community.vectorstores import FAISS
from langchain.vectorstores.base import VectorStore
from langchain_core.runnables import RunnablePassthrough
from .models import AI
import openai
from dotenv import dotenv_values
from langchain.schema import Document
from typing import List, Dict

# AI 응답 생성을 위한 Serializer(직렬화)
class AIRequestSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')
    class Meta:
        model = AI
        fields = (
            "id",
            "user_question",
            "bot_response",
            "created_at",
            "author",  # ForeignKey 필드도 포함
        )# 이 부분들이 json 형식으로 응답 됨
        read_only_fields = ("bot_response", "created_at","author")  # 수정 불가능한 필드
    #___________________________________#
    
    



# # serializer 직렬화 하는중
# #__________________________________________
# # 외부 API 데이터 조회 기능을 제공하는 메서드
# class ExternalAPIService:
#     def fetch_external_data(self, api_url, params=None, api_key=None):
#         """외부 데이터 API를 호출하는 메서드"""
#         try:
#             headers = {
#                 'Authorization': f'Bearer {api_key}'  # API 키를 사용하여 인증
#             }
#             response = requests.get(api_url, params=params, headers=headers)  # GET 요청
#             response.raise_for_status()  # 오류 발생 시 예외 처리
#             return response.json()  # 응답을 JSON 형식으로 반환
#         except requests.exceptions.RequestException as e:
#             return f"Error: {str(e)}"

# # AI 서비스 호출 기능을 제공하는 메서드

# class AIService:
#     # Meta 클래스를 사용하여 AI 모델의 필드 설정
#     class Meta:
#         model = AI  # AI 모델 지정
#         fields = ['user_question', 'bot_response', 'created_at']  # 필요한 필드들

#     def __init__(self, prompt, api_key):
#         self.prompt = prompt  # 프롬프트
#         self.api_key = api_key  # API 키

#     def query_ai_engine(self):
#         """AI 엔진에 프롬프트를 보내고 응답을 받는 메서드"""
#         try:
#             openai.api_key = self.api_key  # API 키 설정
#             response = openai.Completion.create(
#                 engine="text-davinci-003",  # 사용하려는 모델
#                 prompt=self.prompt,  # 사용자의 프롬프트
#                 max_tokens=150
#             )
#             return response.choices[0].text.strip()  # 생성된 텍스트 반환
#         except Exception as e:
#             return f"Error: {str(e)}"

#     def get_ai_data(self):
#         """모델 데이터와 응답을 결합하여 반환하는 메서드"""
#         # 예시: AI 모델에서 데이터를 불러오는 과정
#         ai_instance = AI.objects.create(user_question=self.prompt)  # 질문을 저장
#         ai_instance.bot_response = self.query_ai_engine()  # 챗봇 응답
#         ai_instance.save()  # 모델 저장
#         return ai_instance  # AI 인스턴스 반환
    
    
# #________________________________________________########
# # 
# # 예전 코드  ai 코드들
