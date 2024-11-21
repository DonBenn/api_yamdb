from django.urls import include, path  # type: ignore
from rest_framework.routers import DefaultRouter  # type: ignore

from api.views import (
    APIGetToken,
    APISignup,
    CategoryViewSet,
    CommentsViewSet,
    GenreViewSet,
    ReviewViewSet,
    TitleViewSet,
    UserViewSet,
)

router_v1 = DefaultRouter()
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews', ReviewViewSet, basename='review'
)
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentsViewSet,
    basename='comment',
)
router_v1.register('titles', TitleViewSet, basename='title')
router_v1.register('categories', CategoryViewSet, basename='category')
router_v1.register('genres', GenreViewSet, basename='genre')
router_v1.register('users', UserViewSet, basename='users')

auth_urls = [
    path('signup/', APISignup.as_view(), name='signup'),
    path('token/', APIGetToken.as_view(), name='get_token'),
]
urlpatterns = [
    path(
        'v1/',
        include(
            [
                path('auth/', include(auth_urls)),
                path('', include(router_v1.urls)),
            ]
        ),
    )
]
