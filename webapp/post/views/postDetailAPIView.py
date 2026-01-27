import datetime

from django.db.models import F
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from post.models import Post, PostTag
from post.serializers import PostSerializer


class PostDetailAPIView(APIView):
    def get_object(self, post_id):
        return get_object_or_404(
            Post.objects.select_related('user').prefetch_related('image', 'posttag_set__tag'),
            id=post_id
        )

    # 게시글 상세 조회
    def get(self, request, post_id):
        post = self.get_object(post_id)
        serializer = PostSerializer(post)
        data = serializer.data
        response = Response(data, status=status.HTTP_200_OK)

        # 유효기간 하루
        expires = timezone.now() + datetime.timedelta(days=1)

        # 기존 쿠키에 view 있나 확인
        if 'view' in request.COOKIES:
            cookies = request.COOKIES['view']
            cookies_list = cookies.split('|')

            # 기존 쿠키 리스트에 정보가 없으면 조회수 1 증가
            if str(post_id) not in cookies_list:
                response.set_cookie('view', cookies + f'|{post_id}', expires=expires)
                Post.objects.filter(id=post_id).update(view=F('view') + 1)
        else:
            response.set_cookie('view', str(post_id), expires=expires)
            Post.objects.filter(id=post_id).update(view=F('view') + 1)

        return response

    # 게시글 삭제
    def delete(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
