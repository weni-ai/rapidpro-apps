from django.conf import settings
from storages.backends.s3boto import S3BotoStorage

__author__ = 'teehamaral'


class StaticStorage(S3BotoStorage):
    location = settings.STATICFILES_LOCATION
    bucket_name = settings.AWS_STORAGE_BUCKET_NAME


class MediaStorage(S3BotoStorage):
    default_acl = 'private'
    querystring_auth = True
    bucket_name = settings.AWS_STORAGE_BUCKET_NAME_MEDIA
