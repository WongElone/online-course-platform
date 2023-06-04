from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage
from django.core.files.storage import FileSystemStorage


# class StaticStorage(S3Boto3Storage):
#     location = 'static'
#     default_acl = 'public-read'

# class PublicMediaStorage(S3Boto3Storage):
#     location = 'media'
#     default_acl = 'public-read'
#     file_overwrite = False

# class PrivateMediaStorage(S3Boto3Storage):
#     location = 'private'
#     default_acl = 'private'
#     file_overwrite = False
#     custom_domain = False

class LocalMediaStorage(FileSystemStorage):
    location=settings.MEDIA_ROOT

class S3MediaStorage(S3Boto3Storage):
    location = 'media'
    default_acl = 'private' # set private then the public cannot view the resource through s3 url, need signed s3 url
    file_overwrite = False

MediaStorage = S3MediaStorage if settings.USE_S3 else LocalMediaStorage
