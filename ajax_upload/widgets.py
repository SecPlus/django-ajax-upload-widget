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

#class AjaxClearableProtectedFileInput(forms.FileInput):
#    initial_text = ugettext_lazy('Currently')
#    input_text = ugettext_lazy('Change')
#    clear_checkbox_label = ugettext_lazy('Clear')
#
#    template_with_initial = u'%(input)s'
#    template_with_clear = ''
#    
##    template_with_initial = u'%(initial_text)s: %(initial)s %(clear_template)s<br />%(input_text)s: %(input)s'
##    template_with_clear = u'%(clear)s <label for="%(clear_checkbox_id)s">%(clear_checkbox_label)s</label>'
#
#
#    def __init__(self, attrs=None):
#        
#        self.protected_files = attrs.pop('protected_files', False)
#        self.protected_files_url = attrs.pop('protected_files_url', None)
#        
#        result = super(AjaxClearableProtectedFileInput, self).__init__(attrs=attrs)
#        return result
#    
#    
#    def clear_checkbox_name(self, name):
#        """
#        Given the name of the file input, return the name of the clear checkbox
#        input.
#        """
#        return name + '-clear'
#
#    def clear_checkbox_id(self, name):
#        """
#        Given the name of the clear checkbox input, return the HTML id for it.
#        """
#        return name + '_id'
#
#    def render(self, name, value, attrs=None):
#        substitutions = {
#            'initial_text': self.initial_text,
#            'input_text': self.input_text,
#            'clear_template': '',
#            'clear_checkbox_label': self.clear_checkbox_label,
#        }
#        template = u'%(input)s'
#        
#        template_span = u'<span>%s</span>'
#        template_link = u'<a href="%s">%s</a>'
#        
#
#        if value:
#            try:
#                uploaded_file = UploadedFile.objects.get(file=value)
#                filename = u'%s%s' % (settings.MEDIA_URL, value)
#            except UploadedFile.DoesNotExist:
#                filename = value
#        else:
#            filename = ''
#            
#        if value and hasattr(value, "url"):
#            
#            template = self.template_with_initial
#            substitutions['initial'] = (u'<a href="%s">%s</a>' % (escape(value.url), escape(force_unicode(value))))
#            
#            if not self.is_required:
#                checkbox_name = self.clear_checkbox_name(name)
#                checkbox_id = self.clear_checkbox_id(checkbox_name)
#                substitutions['clear_checkbox_name'] = conditional_escape(checkbox_name)
#                substitutions['clear_checkbox_id'] = conditional_escape(checkbox_id)
#                substitutions['clear'] = CheckboxInput().render(checkbox_name, False, attrs={'id': checkbox_id})
#                substitutions['clear_template'] = self.template_with_clear % substitutions
#                substitutions['input'] = super(AjaxClearableProtectedFileInput, self).render(name, value, attrs)
#        
#        attrs.update({
#            'class': attrs.get('class', '') + 'ajax-upload',
#            'data-filename': filename,  # This is so the javascript can get the actual value
#            'data-required': self.is_required or '',
#            'data-upload-url': reverse('ajax-upload')
#        })
#
#        substitutions['input'] = super(AjaxClearableProtectedFileInput, self).render(name, value, attrs)
#
#                
#
#        return mark_safe(template % substitutions)
#
#    def value_from_datadict(self, data, files, name):
#        upload = super(AjaxClearableProtectedFileInput, self).value_from_datadict(data, files, name)
#        if not self.is_required and CheckboxInput().value_from_datadict(
#            data, files, self.clear_checkbox_name(name)):
#            if upload:
#                # If the user contradicts themselves (uploads a new file AND
#                # checks the "clear" checkbox), we return a unique marker
#                # object that FileField will turn into a ValidationError.
#                file = FILE_INPUT_CONTRADICTION
#            # False signals to clear any existing value, as opposed to just None
#            file = False
#        file = upload
#        
#        if file is not None:  # super class may return a file object, False, or None
#            return file  # Default behaviour
#        elif name in data:  # This means a file path was specified in the POST field
#            file_path = data.get(name)
#            if not file_path:
#                return False  # False means clear the existing file
#            elif file_path.startswith(settings.MEDIA_URL):
#                # Strip and media url to determine the path relative to media root
#                relative_path = file_path[len(settings.MEDIA_URL):]
#                try:
#                    uploaded_file = UploadedFile.objects.get(file=relative_path)
#                except UploadedFile.DoesNotExist:
#                    raise AjaxUploadException(u'%s %s' % (_('Invalid file path:'), relative_path))
#                else:
#                    return File(uploaded_file.file)
#            else:
#                # file might be in different location with different storage.
#                pass 
#                #raise AjaxUploadException(u'%s %s' % (_('File path not allowed:'), file_path))
#        return None
    
    
class AjaxClearableFileInput(forms.ClearableFileInput):
    template_with_clear = ''  # We don't need this
    template_with_initial = '%(input)s'
    
    def __init__(self, protected_files=None, preview_url=None, attrs=None):
        
        self.protected_files = protected_files
        self.preview_url = preview_url
        
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
        
        if (self.protected_files and self.preview_url) or not self.protected_files:
            downloadable=True
        
        if not file.startswith(settings.MEDIA_URL):
            if self.protected_files and self.preview_url:
                if hasattr(self.preview_url, '__call__'):
                    filename = self.preview_url(filename=filename)
                elif isinstance(self.preview_url, str):
                    filename = u"%s%s" % (self.preview_url, file)
                else:
                    #TODO: else?!?!?
                    pass
                
        attrs.update({
            'class': attrs.get('class', '') + 'ajax-upload',
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
