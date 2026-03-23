from post.models import Post, Tag, PostTag, PostImage
from post.serializers import PostSerializer

from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework import status, pagination

from django.db import IntegrityError, transaction
from django.db.models import Q
from rest_framework.filters import BaseFilterBackend


class CustomSearchFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        search_title = request.query_params.get('search_title', None)
        search_content = request.query_params.get('search_content', None)
        search_all = request.query_params.get('search_all', None)

        if search_title is not None:
            queryset = queryset.filter(title__icontains=search_title)

        if search_content is not None:
            queryset = queryset.filter(content__icontains=search_content)

        if search_all is not None:
            queryset = queryset.filter(Q(title__icontains=search_all) | Q(content__icontains=search_all))

        return queryset

class PostListAPIView(ListAPIView):
    queryset = Post.objects.select_related('user').prefetch_related(
        'image', 'posttag_set__tag'
    ).order_by('-created_at')
    serializer_class = PostSerializer
    pagination_class = pagination.PageNumberPagination
    filter_backends = [CustomSearchFilter]
    # ordering_fields = ['created_at']

    # 게시글 작성
    def post(self, request):
        serializer = PostSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            try:
                with transaction.atomic():
                    post = serializer.save()

                    # 이미지 생성
                    img_set = request.FILES.getlist('image')

                    for img in img_set:
                        PostImage.objects.create(post=post, image=img)

                    # 태그 생성
                    tag_set = request.data.getlist('write_tags', [])
                    for tag in tag_set:
                        tag_instance, _ = Tag.objects.get_or_create(name=tag)
                        PostTag.objects.create(post=post, tag=tag_instance)

                return Response(serializer.data, status=status.HTTP_201_CREATED)

            except IntegrityError:
                return Response({"error" : "fail to create tag"}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)