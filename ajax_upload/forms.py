import os
import uuid
import unidecode

from django import forms

from .settings import UPLOADER_MAX_FILENAME_CHARS_LEN
from .models import UploadedFile


class UploadedFileForm(forms.ModelForm):

    class Meta:
        model = UploadedFile
        fields = ('file',)

    def clean_file(self):
        data = self.cleaned_data['file']
        # Change the name of the file to something unguessable
        # Construct the new name as <unique-hex>-<original>.<ext>
        data.name = unidecode.unidecode(u'%s-%s' % (uuid.uuid4().hex, data.name))

        #
        # This snippet of code truncates the total file name to the field's max_length
        #
        model_field_file = UploadedFile._meta.get_field('file')
        upload_to = model_field_file.upload_to if not callable(model_field_file.upload_to) else model_field_file.upload_to(self.instance, data.name)

        if (len(data.name) + len(upload_to)) > UPLOADER_MAX_FILENAME_CHARS_LEN:
            file_name, file_ext = os.path.splitext(data.name)
            file_name = file_name[:(UPLOADER_MAX_FILENAME_CHARS_LEN - len(file_ext) - len(upload_to))]
            data.name = '%s%s' % (file_name, file_ext)

        return data
