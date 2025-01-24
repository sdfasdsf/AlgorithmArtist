from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny, IsAuthenticated
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.throttling import AnonRateThrottle



class Main(APIView):

    permission_classes = [AllowAny]  # 인증이 필요하지 않음
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'Main/home.html'
    throttle_classes = [AnonRateThrottle]  # Rate limiting 적용

    def get(self,request):
        '''리뷰 목록 폼'''
        return Response({'message': '리뷰 목록 페이지입니다.'})
    
class Movie(APIView):

    permission_classes = [AllowAny]  # 인증이 필요하지 않음
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'Main/movie.html'
    throttle_classes = [AnonRateThrottle]  # Rate limiting 적용

    def get(self,request, movie_id):
        '''리뷰 목록 폼'''
        return Response({'message': '리뷰 목록 페이지입니다.'})






