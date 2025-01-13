# ai/views.py
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from .serializers import AISerializer
from .models import AI
from .ai import process_movie_query  # AI 처리 함수 임포트

@api_view(['POST'])
def TMOVINGBOT(request):
    """
    영화 질문을 받아서 AI가 답변을 생성하고 저장하는 API.
    """
    if request.method == 'POST':
        user_question = request.data.get('question')  # 사용자가 보낸 질문
        movie_name = request.data.get('movie_name')  # 영화 이름

        if not user_question or not movie_name:
            return Response({"error": "Both question and movie_name are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # AI 처리 함수 호출하여 답변을 생성
            bot_response = process_movie_query(movie_name, user_question)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # AI 모델에 저장
        ai_instance = AI.objects.create(
            user_question=user_question,
            bot_response=bot_response,
            author=request.user  # 로그인한 사용자를 작성자로 설정
        )

        # 직렬화 후 응답
        serializer = AISerializer(ai_instance)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    
#views 보이는 거니까 serializer ai 서비스 질문 결과값 가져오는 걸로 하고 데이터 베이스 클라이언트  인증  account