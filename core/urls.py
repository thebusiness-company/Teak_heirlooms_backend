from django.urls import path,include
from .views import *
from drf_social_oauth2 import urls as drf_urls
urlpatterns = [
    path('profile/', UserProfileUpdateView.as_view(), name='user-profile'),
    path("user/register/", RegisterView.as_view(), name="register"),
    path('change-password/', ChangePasswordView.as_view()),
    #  path('create-superuser/', CreateSuperUserAPIView.as_view(), name='create-superuser'),
    path('testimonials/', TestimonialListCreateAPIView.as_view(), name='testimonial-list-create'),
    path('testimonials/<int:pk>/', TestimonialRetrieveUpdateDeleteAPIView.as_view(), name='testimonial-detail'),
    path('homebanner/', HomeBannerView.as_view(), name='homebanner'),
    path('blogs/', BlogListCreateAPIView.as_view(), name='blog-list-create'),
    path('blogs/<int:pk>/', BlogRetrieveUpdateDeleteAPIView.as_view(), name='blog-detail'),
    path('latest-video/', LatestVideoBannerView.as_view(), name='latest-video'),
    path("banners/", BannerListView.as_view(), name="banner-list"),  # GET & POST
    path("banners/<int:pk>/", BannerDetailView.as_view(), name="banner-detail"),  # GET, PUT, DELETE
    path("latest/", LatestBannerView.as_view(), name="latest-banner"),
    path('auth/', include(drf_urls)),
    path('auth/google-login/', GoogleLoginView.as_view(), name='google-login'),
]
