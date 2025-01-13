import json
import requests
import os
from dotenv import dotenv_values
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.vectorstores.base import VectorStore
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_community.chat_message_histories import ChatMessageHistory
from datetime import datetime
from typing import List, Dict
from rest_framework import serializers
from .models import AI
# AI 응답 생성을 위한 Serializer(직렬화)

class AISerializer(serializers.ModelSerializer):
    class Meta:
        model = AI
        fields = ['id', 'user_question', 'bot_response', 'created_at', 'author']
        read_only_fields = ['created_at', 'author']  # 작성자와 생성시간은 읽기 전용