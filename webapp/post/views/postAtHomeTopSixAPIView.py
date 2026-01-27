from rest_framework import status
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from post.models import Post
from post.serializers import PostSerializer


@permission_classes([AllowAny])
class PostAtHomeTopSixAPIView(APIView):
    def get(self, request):
        posts = Post.objects.select_related('user').prefetch_related(
            'image', 'posttag_set__tag'
        ).order_by('-created_at')[:6]
        serializer = PostSerializer(posts, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)