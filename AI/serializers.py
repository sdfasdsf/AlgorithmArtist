from rest_framework import serializers
import requests

# 외부 API 호출을 위한 Serializer
class ExternalAPIRequestSerializer(serializers.Serializer):
    api_key = serializers.CharField(max_length=100)  # API 키를 받을 필드
    api_url = serializers.URLField()  # 호출할 외부 API의 URL 필드
    params = serializers.DictField(child=serializers.CharField())  # API 호출 시 추가할 파라미터 필드

# AI 엔진 요청을 위한 Serializer
class AIRequestSerializer(serializers.Serializer):
    prompt = serializers.CharField(max_length=255)  # AI 엔진에 보낼 프롬프트
    api_key = serializers.CharField(max_length=100)  # OpenAI API 키

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

# AI 서비스 호출 기능을 제공하는 메서드

class AIService:
    # Meta 클래스를 사용하여 AI 모델의 필드 설정
    class Meta:
        model = AI  # AI 모델 지정
        fields = ['user_question', 'bot_response', 'created_at']  # 필요한 필드들

    def __init__(self, prompt, api_key):
        self.prompt = prompt  # 프롬프트
        self.api_key = api_key  # API 키

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

    def get_ai_data(self):
        """모델 데이터와 응답을 결합하여 반환하는 메서드"""
        # 예시: AI 모델에서 데이터를 불러오는 과정
        ai_instance = AI.objects.create(user_question=self.prompt)  # 질문을 저장
        ai_instance.bot_response = self.query_ai_engine()  # 챗봇 응답
        ai_instance.save()  # 모델 저장
        return ai_instance  # AI 인스턴스 반환