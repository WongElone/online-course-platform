from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible

@deconstructible # need this decorator such that the validator is serializable in migration file
class FileSizeValidator(object):
    def __init__(self, max_mb=None):
        if not max_mb:
            raise Exception('max_mb not provided')
        self.max_mb = max_mb

    def __call__(self, file):
        if file.size > self.max_mb * 1024 * 1024:
            raise ValidationError(f'Files cannot be larger than {self.max_mb}mb.')
    
    # need this such that the validator is serializable in migration file
    def __eq__(self, other):
        return (
            isinstance(other, self.__class__)
            and self.max_mb == other.max_mb
        )
