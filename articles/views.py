# articles/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny, IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Article
from .serializers import ArticleListSerializer, ArticleDetailSerializer
from django.core.cache import cache
from .serializers import CommentSerializer
from .models import Comment
import os
from django.conf import settings
from AI.AIanswer import load_movies_from_file
import json
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.throttling import AnonRateThrottle
from django.shortcuts import redirect
from django.contrib import messages
from django.shortcuts import render


class ArticleList(APIView):
    permission_classes = [AllowAny]  # 인증이 필요하지 않음
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'articles/reviewboard.html'
    throttle_classes = [AnonRateThrottle]  # Rate limiting 적용

    def get(self,request):
        '''리뷰 목록 폼'''
        return Response({'message': '리뷰 목록 페이지입니다.'})

class ArticleListAPI(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        """게시글 목록 조회"""
        articles = Article.objects.all() # 모든 게시글을 가져옴
        serializer = ArticleListSerializer(
            articles, many=True
        )  # 목록용 Serializer 사용
        return Response(serializer.data) # 직렬화된 데이터 반환

class ArticleCreate(APIView):

    permission_classes = [IsAuthenticatedOrReadOnly] # 로그인 해야만 가능
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'articles/articlecreate.html'
    throttle_classes = [AnonRateThrottle]  # Rate limiting 적용
    
    def get(self, request):
        """리뷰 생성 폼 표시"""
        return Response({'message': '리뷰 생성 페이지입니다.'})

    def post(self, request):
        """리뷰 생성"""

        # 요청 데이터와 파일 데이터를 병합
        data = request.data.copy()
        data.update(request.FILES)

        serializer = ArticleDetailSerializer(data=request.data)  # 상세 Serializer 사용
        if serializer.is_valid():
            serializer.save(author=request.user) # 요청 사용자 정보를 작성자로 설정 후 저장
            movies = load_movies_from_file("response.json")
            article = Article.objects.filter(author = request.user).order_by("-id").first()
            for movie in movies:
                if movie.get("title").strip() == article.movie_title.strip():
                    # 리뷰 키가 없으면 초기화
                    if "reviews" not in movie:
                        movie["reviews"] = []
                    # 리뷰 추가
                    movie["reviews"].append({"review": article.content, "rating": article.rating})
                    print(f"'{article.movie_title}' 영화에 리뷰가 추가되었습니다.")
                    with open("response.json", "w", encoding="utf-8") as f:
                        json.dump(movies, f, ensure_ascii=False, indent=4)
                    
            return Response({"article_id": article.id}, status=201)        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ArticleDetail(APIView):
    # 비로그인 사용자에게는 읽기 권한만, 로그인 사용자에게는 삭제 및 게시글 좋아요 권한 부여
    permission_classes = [IsAuthenticatedOrReadOnly]
    # 게시글 ID를 통해 특정 게시글 객체를 가져오며, 없으면 404 오류 반환
    def get_object(self, article_pk):
        return get_object_or_404(Article, pk=article_pk)

    def get(self, request, article_pk):
        """게시글 상세 조회(댓글 목록도 포함)"""
        article = self.get_object(article_pk)
        
        # 로그인한 사용자이고 작성자가 아닌 경우에만 조회수 증가 처리
        # 24시간 동안 같은 IP에서 같은 게시글 조회 시 조회수가 증가하지 않음
        if request.user != article.author:
            # 해당 사용자의 IP와 게시글 ID로 캐시 키를 생성
            cache_key = f"view_count_{request.META.get('REMOTE_ADDR')}_{article_pk}"
            
            # 캐시에 없는 경우에만 조회수 증가
            if not cache.get(cache_key):
                article.views += 1
                article.save()
                # 캐시 저장 (24시간 유효)
                cache.set(cache_key, True, 60 * 30) # 30분마다 조회수 증가

        serializer = ArticleDetailSerializer(article)  # 상세 Serializer 사용
        
        return Response(serializer.data)
    
    def post(self,request,article_pk):
        """리뷰 좋아요 기능"""
        article = self.get_object(article_pk)
        me = request.user # 현재 요청 사용자
        if me == article.author: # 자신의 글은 좋아요 불가
            return Response(
                {"error": "자신의 글은 좋아요 할 수 없습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        # 이미 좋아요한 경우 좋아요 취소
        if article.article_like.filter(id=me.id).exists():
            article.article_like.remove(me)
            is_liked = False
            message = f"{article.Article_title}을 좋아요를 취소했습니다."
            article.total_likes_count = article.article_like.count()  # 게시글 좋아요 수 갱신

        else : # 좋아요 추가
            article.article_like.add(me)
            is_liked = True
            message = f"{article.Article_title}을 좋아요를 했습니다."
            article.total_likes_count = article.article_like.count()  # 게시글 좋아요 수 갱신
        
        article.save()  # 좋아요 수 반영 후 저장

        return Response(
        {
            "is_liked": is_liked,
            "message": message,
        },
        status=status.HTTP_200_OK,
        )

class ArticleDelete(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, article_pk):
        """게시글 삭제"""
        article = get_object_or_404(Article, pk=article_pk)

        # 작성자 확인
        if request.user != article.author:
            messages.error(request, '삭제 권한이 없습니다.')  # 오류 팝업 메시지 표시(html에서 가져와서 써야 보이는 듯)
            return redirect('article_detail', article_pk=article_pk)

        # 게시글에 첨부된 이미지 삭제
        file_path = os.path.join(settings.MEDIA_ROOT, article.image.name)
        if os.path.exists(file_path):
            os.remove(file_path)

        article.delete()
        messages.success(request, '게시글이 성공적으로 삭제되었습니다.')  # 성공 팝업 메시지 표시(html에서 가져와서 써야 보이는 듯)
        return redirect('article_list')  # 게시글 목록 페이지로 리다이렉트
    

class ArticleEdit(APIView):
    # 로그인 사용자만 수정 권한 부여
    permission_classes = [IsAuthenticated] # 로그인 해야만 가능
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'articles/Articleedit.html'
    throttle_classes = [AnonRateThrottle]  # Rate limiting 적용

    # 게시글 ID를 통해 특정 게시글 객체를 가져오며, 없으면 404 오류 반환
    def get_object(self, article_pk):
        return get_object_or_404(Article, pk=article_pk)

    def get(self, request, article_pk):

        article = self.get_object(article_pk)
        if request.user != article.author: # 작성자만 수정 가능
            messages.error(request, '수정 권한이 없습니다.') # 오류 팝업 메시지 표시(html에서 가져와서 써야 보이는 듯)
            return redirect('article_detail', article_pk=article_pk)
        """리뷰 수정 폼 표시"""
        serializer = ArticleDetailSerializer(article)
        return Response({'article': serializer.data, 'message': '리뷰 수정 페이지입니다.'})

    def post(self, request, article_pk):
        """게시글 수정"""
        article = self.get_object(article_pk)
        if request.user != article.author: # 작성자만 수정 가능
            messages.error(request, '수정 권한이 없습니다.') # 오류 팝업 메시지 표시(html에서 가져와서 써야 사용자에게 보이는 듯)
            return redirect('article_detail', article_pk=article_pk)
        
        serializer = ArticleDetailSerializer(article, data=request.data, partial=True)  # 상세 Serializer 사용
        if serializer.is_valid():
            serializer.save(author = article.author) # 작성자 정보 유지
            messages.success(request, '게시글이 성공적으로 수정되었습니다.') # 수정 성공 팝업 메시지 표시(html에서 가져와서 써야 사용자에게 보이는 듯)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        messages.error(request, '입력한 데이터가 유효하지 않습니다.') # 수정 실패 팝업 메시지 표시(html에서 가져와서 써야 사용자에게 보이는 듯)
        return Response({'article': serializer.data, 'errors': serializer.errors})

        


class CommentCreate(APIView):
    # 비로그인 사용자에게는 읽기 권한만, 로그인 사용자에게는 생성 권한 부여
    permission_classes = [IsAuthenticatedOrReadOnly]
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'articles/commentcreate.html'
    throttle_classes = [AnonRateThrottle]  # Rate limiting 적용
    def get_article(self, article_pk):
        # 게시글 ID를 통해 게시글 객체 가져오기
        return get_object_or_404(Article, pk=article_pk)

    def get(self, request, article_pk):
        """댓글 폼 생성"""
        article = self.get_article(article_pk)
        return Response({'article': article.Article_title, 'message': '댓글 작성 페이지입니다.'})

    def post(self, request, article_pk):
        """댓글 생성"""
        article = self.get_article(article_pk)
        serializer = CommentSerializer(data=request.data) # 댓글 생성용 Serializer
        if serializer.is_valid():
            serializer.save(author=request.user, article=article) # 작성자와 게시글 정보 저장
            messages.success(request, '댓글이 성공적으로 작성되었습니다.') # 작성 성공 팝업 메시지 표시(html에서 가져와서 써야 사용자에게 보이는 듯)
            return redirect('article_detail', article_pk=article_pk)
        messages.error(request, '댓글 작성에 실패했습니다.') # 작성 실패 팝업 메시지 표시(html에서 가져와서 써야 사용자에게 보이는 듯)
        return Response({'article': article, 'errors': serializer.errors})
    

class CommentLike(APIView):
    # 로그인 사용자만 댓글 좋아요 권한 부여
    permission_classes = [IsAuthenticatedOrReadOnly]
    """댓글 좋아요 기능"""
    def get_comment(self, comment_pk):
        return get_object_or_404(Article, pk=comment_pk) # 특정 댓글 가져오기
    
    def post(self, request, article_pk, comment_pk): 
        comment = Comment.objects.get(id=comment_pk, article_id=article_pk)
        me = request.user

        if me == comment.author: # 자신의 댓글은 좋아요 불가
            return Response(
                {"error": "자신의 댓글은 좋아요 할 수 없습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        # 이미 좋아요한 경우 좋아요 취소
        if comment.comment_like.filter(id=me.id).exists():
            comment.comment_like.remove(me)
            is_liked = False
            message = "댓글 좋아요를 취소했습니다."
            comment.total_commentlikes_count = comment.comment_like.count()  # 댓글 좋아요 수 갱신
        
        else : # 좋아요 추가
            comment.comment_like.add(me)
            is_liked = True
            message = "댓글 좋아요를 했습니다."
            comment.total_commentlikes_count = comment.comment_like.count()  # 댓글 좋아요 수 갱신

        comment.save()  # 좋아요 수 반영 후 저장

        return Response(
        {
            "is_liked": is_liked,
            "message": message,
        },
        status=status.HTTP_200_OK,
        )


class CommentEdit(APIView):
    # 로그인 사용자만 수정 권한 부여
    permission_classes = [IsAuthenticated]
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'comments/comment_edit.html'
    def get_article(self, article_pk):
        # 게시글 ID를 통해 게시글 객체 가져오기
        return get_object_or_404(Article, pk=article_pk)
    
    def get_comment(self, article, comment_pk):
        # 게시글과 댓글 ID를 통해 특정 댓글 객체 가져오기
        return get_object_or_404(Comment, pk=comment_pk, article=article)
    
    def get(self, request, article_pk, comment_pk):
        '''댓글 수정 폼'''
        article = self.get_article(article_pk)
        comment = self.get_object(article, comment_pk)
        if request.user != comment.author:
            messages.error(request, '수정 권한이 없습니다.') # 오류 팝업 메시지 표시(html에서 가져와서 써야 보이는 듯)
            return redirect('article_detail', article_pk=article_pk)
        return Response({'comment': comment, 'message': '댓글 수정 페이지입니다.'})

    def post(self, request, article_pk, comment_pk):
        """댓글 수정"""
        article = self.get_article(article_pk)
        comment = self.get_comment(article, comment_pk)
        if request.user != comment.author: # 작성자만 수정 가능
            return Response({'detail': '수정 권한이 없습니다.'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = CommentSerializer(comment, data=request.data) # 수정용 Serializer
        if serializer.is_valid():
            serializer.save() # 댓글 내용 수정 저장
            messages.success(request, '댓글이 성공적으로 수정되었습니다.') # 수정 성공 팝업 메시지 표시(html에서 가져와서 써야 보이는 듯)
            return redirect('article_detail', article_pk=article_pk)
        messages.error(request, '댓글 수정에 실패했습니다.') # 수정 실패 메시지 표시(html에서 가져와서 써야 보이는 듯)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class CommentDelete(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, article_pk, comment_pk):
        article = get_object_or_404(Article, pk=article_pk)
        return get_object_or_404(Comment, pk=comment_pk, article=article)

    def post(self, request, article_pk, comment_pk):
        """댓글 삭제"""
        comment = self.get_object(article_pk, comment_pk)
        if request.user != comment.author:
            messages.error(request, '삭제 권한이 없습니다.') # 오류 팝업 메시지 표시(html에서 가져와서 써야 보이는 듯)
            return redirect('article_detail', article_pk=article_pk)

        comment.delete()
        messages.success(request, '댓글이 성공적으로 삭제되었습니다.') # 삭제 성공 팝업 메시지 표시(html에서 가져와서 써야 보이는 듯)
        return redirect('article_detail', article_pk=article_pk)

