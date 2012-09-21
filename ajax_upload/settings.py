from django.conf import settings


# Number of seconds to keep uploaded files. The clean_uploaded command will
# delete them after this has expired.
UPLOADER_DELETE_AFTER = getattr(settings, 'UPLOADER_DELETE_AFTER', 60 * 60)

# The max length of file name;
UPLOADER_MAX_FILENAME_CHARS_LEN = getattr(settings, 'UPLOADER_MAX_FILENAME_CHARS_LEN', 100)