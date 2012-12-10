import os

from django import forms
from django.conf import settings
from django.core.files import File
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy, ugettext as _
from django.utils.html import escape, conditional_escape
from django.utils.encoding import StrAndUnicode, force_unicode
from django.forms.widgets import CheckboxInput

from .models import UploadedFile


class AjaxUploadException(Exception):
    pass
    
class AjaxClearableFileInput(forms.ClearableFileInput):
    template_with_clear = ''  # We don't need this
    template_with_initial = '%(input)s'
    
    def __init__(self, protected_file=None, full_download_url=None, preview_url=None, attrs=None):
        
        self.protected_file = protected_file
        self.preview_url = preview_url
        self.full_download_url = full_download_url
        
        result = super(AjaxClearableFileInput, self).__init__(attrs=attrs)
        return result

    def render(self, name, value, attrs=None):
        attrs = attrs or {}

        if value:
            try:
                uploaded_file = UploadedFile.objects.get(file=value)
                filename = u'%s%s' % (settings.MEDIA_URL, value)
            except UploadedFile.DoesNotExist:
                filename = value
        else:
            filename = ''
        
        file = unicode(filename)
        
        downloadable = False
        if not self.protected_file:
            downloadable = True

        # If we want to use custom url for private download - for ex.
        # /admin/documents/0/download/1/ we need additional field that contains
        # file label.
        # For standard download url - for ex:
        # /media/file/upload/document.txt ajax_upload js parses document.txt from the passed filename
        # as a default file label
        # That's why we should set filelabel as additional param if we want different file label

        filelabel = filename

        if filename:
            if hasattr(self.full_download_url, '__call__'):
                filename = self.full_download_url(filename=filename)
            elif isinstance(self.full_download_url, str):
                filename = self.full_download_url
            if hasattr(self.preview_url, '__call__'):
                filename = self.preview_url(filename=filename)
            elif isinstance(self.preview_url, str):
                filename = u"%s%s" % (self.preview_url, file)
            else:
                #TODO: else?!?!?
                pass



        attrs.update({
            'class': attrs.get('class', '') + 'ajax-upload',
            'data-filelabel': filelabel,
            'data-filename': filename,  # This is so the javascript can get the actual value
            'data-required': self.is_required or '',
            'data-upload-url': reverse('ajax-upload'),
            'data-downloadable': int(downloadable)
        })
        
        output = super(AjaxClearableFileInput, self).render(name, value, attrs)
        return mark_safe(output)

    def value_from_datadict(self, data, files, name):
        # If a file was uploaded or the clear checkbox was checked, use that.
        file = super(AjaxClearableFileInput, self).value_from_datadict(data, files, name)
        if file is not None:  # super class may return a file object, False, or None
            return file  # Default behaviour
        elif name in data:  # This means a file path was specified in the POST field
            file_path = data.get(name)
            if not file_path:
                return False  # False means clear the existing file
            elif file_path.startswith(settings.MEDIA_URL):
                # Strip and media url to determine the path relative to media root
                relative_path = file_path[len(settings.MEDIA_URL):]
                try:
                    uploaded_file = UploadedFile.objects.get(file=relative_path)
                except UploadedFile.DoesNotExist:
                    raise AjaxUploadException(u'%s %s' % (_('Invalid file path:'), relative_path))
                else:
                    return File(uploaded_file.file)
            else:
                # file might be in different location with different storage.
                pass 
                #raise AjaxUploadException(u'%s %s' % (_('File path not allowed:'), file_path))
        return None
