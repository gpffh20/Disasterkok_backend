from django.db.models import F
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from post.models import Post, PostLike


class PostLikeAPIView(APIView):
    def post(self, request, *args, **kwargs):
        post_id = kwargs.get('post_id')
        user = self.request.user

        post_liked = PostLike.objects.filter(user=user, post_id=post_id).first()
        if post_liked:
            post_liked.delete()
            Post.objects.filter(id=post_id).update(like=F('like') - 1)
            return Response({'message': '좋아요 취소'}, status=status.HTTP_200_OK)
        else:
            PostLike.objects.create(user=user, post_id=post_id)
            Post.objects.filter(id=post_id).update(like=F('like') + 1)

        return Response({'message': '좋아요'}, status=status.HTTP_201_CREATED)