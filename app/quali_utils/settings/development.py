from quali_utils.settings.default import *

SECRET_KEY = 'u&^!+yvf$qf#8xugt*o8*!g!5$!gdi3-t3mjjfe0s!*7n_k*%*'

DEBUG = True

ALLOWED_HOSTS = ['*']

CORS_ORIGIN_ALLOW_ALL = True

REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
    ]
}
