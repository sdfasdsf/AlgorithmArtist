# articles/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django.shortcuts import get_object_or_404
from .models import Article
from .serializers import ArticleListSerializer, ArticleDetailSerializer
from django.core.cache import cache
from .serializers import CommentSerializer
from .models import Comment
import os
from django.conf import settings


class ArticleListCreate(APIView):
    # 비로그인 사용자에게는 읽기 권한만, 로그인 사용자에게는 쓰기 권한까지 부여
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        """게시글 목록 조회"""
        articles = Article.objects.all() # 모든 게시글을 가져옴
        serializer = ArticleListSerializer(
            articles, many=True
        )  # 목록용 Serializer 사용
        return Response(serializer.data) # 직렬화된 데이터 반환

    def post(self, request):
        """게시글 생성"""
        serializer = ArticleDetailSerializer(data=request.data)  # 상세 Serializer 사용
        if serializer.is_valid():
            serializer.save(author=request.user) # 요청 사용자 정보를 작성자로 설정 후 저장
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ArticleDetail(APIView):
    # 비로그인 사용자에게는 읽기 권한만, 로그인 사용자에게는 수정/삭제 및 게시글 좋아요 권한 부여
    permission_classes = [IsAuthenticatedOrReadOnly]
    # 게시글 ID를 통해 특정 게시글 객체를 가져오며, 없으면 404 오류 반환
    def get_object(self, article_pk):
        return get_object_or_404(Article, pk=article_pk)

    def get(self, request, article_pk):
        """게시글 상세 조회"""
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
        """게시글 좋아요 기능"""
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

    
    def put(self, request, article_pk):
        """게시글 수정"""
        article = self.get_object(article_pk)
        if request.user != article.author: # 작성자만 수정 가
            return Response({'detail': '수정 권한이 없습니다.'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = ArticleDetailSerializer(article, data=request.data, partial=True)  # 상세 Serializer 사용
        if serializer.is_valid():
            serializer.save(author = article.author) # 작성자 정보 유지
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, article_pk):
        """게시글 삭제"""
        article = self.get_object(article_pk) # 작성자만 삭제 가능
        if request.user != article.author:
            return Response({'detail': '삭제 권한이 없습니다.'}, status=status.HTTP_403_FORBIDDEN)
        
        # 게시글에 첨부된 이미지 삭제
        file_path = os.path.join(settings.MEDIA_ROOT, article.image.name)
        if os.path.exists(file_path):
            os.remove(file_path)
        article.delete()  # 게시글 삭제
        return Response(status=status.HTTP_204_NO_CONTENT)  # 성공적으로 삭제됨
    


        


class CommentListCreate(APIView):
    # 비로그인 사용자에게는 읽기 권한만, 로그인 사용자에게는 생성 권한 부여
    permission_classes = [IsAuthenticatedOrReadOnly]
    def get_article(self, article_pk):
        # 게시글 ID를 통해 게시글 객체 가져오기
        return get_object_or_404(Article, pk=article_pk)

    def get(self, request, article_pk):
        """댓글 목록 조회"""
        article = self.get_article(article_pk) # 특정 게시글 가져오기
        comments = article.comments.all() # 해당 게시글의 댓글 목록 가져오기
        serializer = CommentSerializer(comments, many=True) # 목록용 Serializer
        return Response(serializer.data)

    def post(self, request, article_pk):
        """댓글 생성"""
        article = self.get_article(article_pk)
        serializer = CommentSerializer(data=request.data) # 댓글 생성용 Serializer
        if serializer.is_valid():
            serializer.save(author=request.user, article=article) # 작성자와 게시글 정보 저장
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

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


class CommentListDelete(APIView):
    # 로그인 사용자만 수정/삭제 권한 부여
    permission_classes = [IsAuthenticatedOrReadOnly]
    def get_article(self, article_pk):
        # 게시글 ID를 통해 게시글 객체 가져오기
        return get_object_or_404(Article, pk=article_pk)
    
    def get_comment(self, article, comment_pk):
        # 게시글과 댓글 ID를 통해 특정 댓글 객체 가져오기
        return get_object_or_404(Comment, pk=comment_pk, article=article)

    def put(self, request, article_pk, comment_pk):
        """댓글 수정"""
        article = self.get_article(article_pk)
        comment = self.get_comment(article, comment_pk)
        if request.user != comment.author: # 작성자만 수정 가능
            return Response({'detail': '수정 권한이 없습니다.'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = CommentSerializer(comment, data=request.data) # 수정용 Serializer
        if serializer.is_valid():
            serializer.save() # 댓글 내용 수정 저장
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self,request, article_pk, comment_pk):
        """댓글 삭제"""
        article = self.get_article(article_pk)
        comment = self.get_comment(article, comment_pk)

        if request.user != comment.author:  # 작성자만 삭제 가능
            return Response({'detail': '삭제 권한이 없습니다.'}, status=status.HTTP_403_FORBIDDEN)
        
        comment.delete()  # 댓글 삭제
        return Response(status=status.HTTP_204_NO_CONTENT)  # 성공적으로 삭제됨

