from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.routers import SimpleRouter
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView


from .views import *


router = SimpleRouter()
router.register(r'managers', ManagerViewSet)
router.register(r'workers', WorkerViewSet)
router.register(r'clients', ClientViewSet)
router.register(r'comments', CommentViewSet)
router.register(r'deposits', DepositViewSet)
router.register(r'withdraws', WithdrawViewSet)

urlpatterns = [
    # Auth
    path('auth/', TokenObtainPairView.as_view(), name='login'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='refresh-token'),

    # Documentation
    path('documentation/', SpectacularSwaggerView.as_view(url_name='documentation'), name='documentation-ui'),
    path('documentation/schema/', SpectacularAPIView.as_view(), name='documentation'),
    path('documentation/redoc/', SpectacularRedocView.as_view(url_name='documentation'), name='documentation-redoc'),

    # General
    path('', include(router.urls)),


    # --- TEMPORARY --- #
    path('random/create/<str:mode>/', CreateRandomObject.as_view(), name='create-random-object'),


]


