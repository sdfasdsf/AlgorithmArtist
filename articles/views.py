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
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        """게시글 목록 조회"""
        articles = Article.objects.all()
        serializer = ArticleListSerializer(
            articles, many=True
        )  # 목록용 Serializer 사용
        return Response(serializer.data)

    def post(self, request):
        """게시글 생성"""
        serializer = ArticleDetailSerializer(data=request.data)  # 상세 Serializer 사용
        if serializer.is_valid():
            serializer.save(author=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ArticleDetail(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

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
    
    def post(self,request,article_pk): # 게시글 좋아요 기능 추가
        article = self.get_object(article_pk)
        serializer = ArticleDetailSerializer(article, data=request.data, partial=True)  # 상세 Serializer 사용
        me = request.user
        if me == article.author:
            return Response(
                {"error": "자신의 글은 좋아요 할 수 없습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        if article.article_like.filter(id=me.id).exists():
            article.article_like.remove(me)
            is_liked = False
            message = f"{article.Article_title}을 좋아요를 취소했습니다."
            article.total_likes_count = article.article_like.count()  # 게시글 좋아요 수 갱신

        else :
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
        article = self.get_object(article_pk)
        if request.user != article.author:
            return Response({'detail': '수정 권한이 없습니다.'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = ArticleDetailSerializer(article, data=request.data, partial=True)  # 상세 Serializer 사용
        if serializer.is_valid():
            serializer.save(author = article.author)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, article_pk):
        article = self.get_object(article_pk)
        if request.user != article.author:
            return Response({'detail': '삭제 권한이 없습니다.'}, status=status.HTTP_403_FORBIDDEN)
        
        file_path = os.path.join(settings.MEDIA_ROOT, article.image.name)

        
        if os.path.exists(file_path):
            os.remove(file_path)
        article.delete()  # 게시글 삭제
        return Response(status=status.HTTP_204_NO_CONTENT)  # 204 No Content 응답
    


        


class CommentListCreate(APIView):

    def get_article(self, article_pk):
        return get_object_or_404(Article, pk=article_pk)

    def get(self, request, article_pk):
        """댓글 목록 조회"""
        article = self.get_article(article_pk)
        comments = article.comments.all()
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    def post(self, request, article_pk):
        """댓글 생성"""
        article = self.get_article(article_pk)
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user, article=article)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class CommentLike(APIView):

    def get_article(self, comment_pk):
        return get_object_or_404(Article, pk=comment_pk)
    
    def post(self, request, article_pk, comment_pk):
        comment = Comment.objects.get(id=comment_pk, article_id=article_pk)
        me = request.user

        if me == comment.author:
            return Response(
                {"error": "자신의 댓글은 좋아요 할 수 없습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        if comment.comment_like.filter(id=me.id).exists():
            comment.comment_like.remove(me)
            is_liked = False
            message = "댓글 좋아요를 취소했습니다."
            comment.total_commentlikes_count = comment.comment_like.count()  # 댓글 좋아요 수 갱신
        
        else :
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

    def get_article(self, article_pk):
        return get_object_or_404(Article, pk=article_pk)
    
    def get_comment(self, article, comment_pk):
        return get_object_or_404(Comment, pk=comment_pk, article=article)

    def put(self, request, article_pk, comment_pk):
        article = self.get_article(article_pk)
        comment = self.get_comment(article, comment_pk)
        print("request",request.user)
        print("article", comment.author)
        if request.user != comment.author:
            return Response({'detail': '수정 권한이 없습니다.'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = CommentSerializer(comment, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self,request, article_pk, comment_pk):
        article = self.get_article(article_pk)
        comment = self.get_comment(article, comment_pk)

        if request.user != comment.author:
            return Response({'detail': '삭제 권한이 없습니다.'}, status=status.HTTP_403_FORBIDDEN)
        
        comment.delete()  # 게시글 삭제
        return Response(status=status.HTTP_204_NO_CONTENT)  # 204 No Content 응답

