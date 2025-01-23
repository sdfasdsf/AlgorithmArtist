from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from .models import AI
from rest_framework.views import APIView
from .serializers import AIRequestSerializer
from .AIanswer import generate_response_with_setup
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from .models import AI
from .serializers import AIRequestSerializer
from .AIanswer import generate_response_with_setup
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.throttling import AnonRateThrottle  


class AIanswerbot(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'AI/TMOVINGBOTHOME.html'
    throttle_classes = [AnonRateThrottle]  # Rate limiting 적용

    def get(self,request):
        """챗봇 폼 표시"""
        return Response({'message': '챗봇 페이지입니다.', 'user': request.user}, template_name=self.template_name)


class AIanswer(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        """응답 생성"""
        # 사용자 질문을 기반으로 챗봇 응답을 생성합니다.
        serializer = AIRequestSerializer(data=request.data)
        if serializer.is_valid():
            #질문 DB 저장
            ai_instance = serializer.save(author=request.user)  # 자동으로 처리되는 부분

            user_question = ai_instance.user_question
            
            # if request.user ==
            history = []
            recent_entries = AI.objects.filter(author=request.user).exclude(pk=ai_instance.pk).order_by('-id')[:5]


            for entry in recent_entries:
                if entry.bot_response and entry.bot_response != "An error occurred during response generation.":
                    history.append({"role": "user", "content": entry.user_question})
                    history.append({"role": "assistant", "content": entry.bot_response})
            print("history:", history)
            # 답변 생성 (여기서는 함수 호출로 처리하는 부분)
            answer = generate_response_with_setup(user_question, history)

            ai_instance.bot_response = answer
            ai_instance.save()
                
            
            return Response({
                    'user_question': user_question,
                    'bot_response': answer,
                    'history': history
                }, status=status.HTTP_201_CREATED)
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)









