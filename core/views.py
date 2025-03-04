from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from .models import Testimonial
from .serializers import TestimonialSerializer
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.parsers import MultiPartParser, FormParser
from .models import HomeBanner
from .serializers import HomeBannerSerializer
from django.core.files.storage import default_storage
from .models import Blog, VideoBanner
from .serializers import BlogSerializer, VideoBannerSerializer
class TestimonialListCreateAPIView(generics.ListCreateAPIView):
    queryset = Testimonial.objects.all()
    serializer_class = TestimonialSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    parser_classes = [MultiPartParser, FormParser]

    def perform_create(self, serializer):
        """Override create to handle file uploads properly."""
        serializer.save()


class TestimonialRetrieveUpdateDeleteAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Testimonial.objects.all()
    serializer_class = TestimonialSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    parser_classes = [MultiPartParser, FormParser]

    def perform_update(self, serializer):
        """Ensure existing image is preserved if no new one is uploaded."""
        testimonial = self.get_object()

        if not self.request.FILES.get("image"):  # If no new image, preserve the old one
            serializer.validated_data["image"] = testimonial.image

        serializer.save()

    def delete(self, request, *args, **kwargs):
        """Override delete to return a custom message."""
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"message": "Deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
class HomeBannerView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def get(self, request):
        latest_banner = HomeBanner.objects.order_by('-uploaded_at').first()
        if latest_banner:
            serializer = HomeBannerSerializer(latest_banner)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({"message": "No banner found"}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        serializer = HomeBannerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        latest_banner = HomeBanner.objects.order_by('-uploaded_at').first()
        if latest_banner:
            if latest_banner.image:
                default_storage.delete(latest_banner.image.path)  # Delete the image file
            latest_banner.delete()
            return Response({"message": "Banner deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        return Response({"message": "No banner found"}, status=status.HTTP_404_NOT_FOUND)
   
class BlogListCreateAPIView(generics.ListCreateAPIView):
    queryset = Blog.objects.all().order_by('-created_at')
    serializer_class = BlogSerializer
    # permission_classes = [IsAuthenticatedOrReadOnly]
    parser_classes = [MultiPartParser, FormParser]

    def perform_create(self, serializer):
        serializer.save()

class BlogRetrieveUpdateDeleteAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Blog.objects.all()
    serializer_class = BlogSerializer
    # permission_classes = [IsAuthenticatedOrReadOnly]
    parser_classes = [MultiPartParser, FormParser]

    def perform_update(self, serializer):
        blog = self.get_object()
        if not self.request.FILES.get("image"):
            serializer.validated_data["image"] = blog.image
        serializer.save()

class LatestVideoBannerView(APIView):
    def get(self, request):
        latest_video = VideoBanner.objects.order_by('-uploaded_at').first()
        if latest_video:
            serializer = VideoBannerSerializer(latest_video)
            return Response(serializer.data)
        return Response({'youtube_url': None})

    def post(self, request):
        serializer = VideoBannerSerializer(data=request.data)
        if serializer.is_valid():
            VideoBanner.objects.all().delete()  # Keep only the latest video
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        VideoBanner.objects.all().delete()  # Delete all videos
        return Response({'message': 'Video deleted successfully'}, status=status.HTTP_204_NO_CONTENT)