# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'UploadedFile.file'
        db.alter_column('ajax_upload_uploadedfile', 'file', self.gf('django.db.models.fields.files.FileField')(max_length=1024))

    def backwards(self, orm):

        # Changing field 'UploadedFile.file'
        db.alter_column('ajax_upload_uploadedfile', 'file', self.gf('django.db.models.fields.files.FileField')(max_length=100))

    models = {
        'ajax_upload.uploadedfile': {
            'Meta': {'ordering': "('id',)", 'object_name': 'UploadedFile'},
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '1024'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        }
    }

    complete_apps = ['ajax_upload']