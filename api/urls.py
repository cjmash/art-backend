from django.views.generic import TemplateView
from rest_framework.routers import SimpleRouter
from django.conf.urls import include
from django.urls import path
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


from .views import UserViewSet, AssetViewSet, SecurityUserEmailsViewSet, \
    AssetLogViewSet, UserFeedbackViewSet, AssetStatusViewSet, \
    AllocationsViewSet, AssetCategoryViewSet, AssetSubCategoryViewSet, \
    AssetTypeViewSet, AssetModelNumberViewSet, AssetConditionViewSet, \
    AssetMakeViewSet, AssetIncidentReportViewSet, AssetHealthCountViewSet, \
    ManageAssetViewSet, SecurityUserViewSet, AssetSpecsViewSet,\
    OfficeBlockViewSet, OfficeFloorViewSet, OfficeFloorSectionViewSet, \
    GroupViewSet

schema_view = get_schema_view(
    openapi.Info(
        title='ART API',
        default_version='v1',
        description='Assset tracking',
        license=openapi.License(name='BSD License'),
    ),
    public=True,
)


class OptionalSlashRouter(SimpleRouter):
    def __init__(self, trailing_slash='/?'):
        self.trailing_slash = trailing_slash
        super(SimpleRouter, self).__init__()


router = OptionalSlashRouter()
router.register('users', UserViewSet)
router.register('assets', AssetViewSet, 'assets')
router.register('manage-assets', ManageAssetViewSet, 'manage-assets')
router.register('allocations', AllocationsViewSet, 'allocations')
router.register('security-user-emails',
                SecurityUserEmailsViewSet, 'security-user-emails')
router.register('asset-logs', AssetLogViewSet, 'asset-logs')
router.register('user-feedback', UserFeedbackViewSet, 'user-feedback')
router.register('asset-status', AssetStatusViewSet, 'asset-status')
router.register('asset-categories', AssetCategoryViewSet, 'asset-categories')
router.register('asset-sub-categories', AssetSubCategoryViewSet,
                'asset-sub-categories')
router.register('asset-types', AssetTypeViewSet,
                'asset-types')
router.register('asset-models', AssetModelNumberViewSet,
                'asset-models')
router.register('asset-condition', AssetConditionViewSet,
                'asset-condition')
router.register('asset-makes', AssetMakeViewSet, 'asset-makes')
router.register('incidence-reports', AssetIncidentReportViewSet,
                'incidence-reports')
router.register('asset-health', AssetHealthCountViewSet, 'asset-health')
router.register('security-users', SecurityUserViewSet,
                'security-users')
router.register('asset-specs', AssetSpecsViewSet, 'asset-specs')
router.register('user-groups', GroupViewSet, 'user-groups')
router.register('office-blocks', OfficeBlockViewSet, 'office-blocks')
router.register('office-floors', OfficeFloorViewSet, 'office-floors')
router.register('office-sections', OfficeFloorSectionViewSet, 'floor-sections')

urlpatterns = [
    path('api-auth/', include('rest_framework.urls')),
    path('o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    path('docs/', schema_view.with_ui(
        'redoc', cache_timeout=None), name='schema-redoc'),
    path('docs/live/', schema_view.with_ui(
        'swagger', cache_timeout=None), name='schema-swagger'),
    path('', TemplateView.as_view(
        template_name='api/api-index.html',
        extra_context={'api_version': 'V1'}),
        name='api-version-index'
    )
]

urlpatterns += router.urls
