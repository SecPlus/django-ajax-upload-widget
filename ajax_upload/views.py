from django.http import HttpResponse, HttpResponseBadRequest
from django.utils import simplejson
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .forms import UploadedFileForm


@csrf_exempt
@require_POST
def upload(request):
    form = UploadedFileForm(data=request.POST, files=request.FILES)
    '''
        jquery.iframe-transport.js requires special response structure to work properly. The response must by a json surrounded with <textarea></textarea>
        For more information read comments in jquery.iframe-transport.js
        
        DO NOT:
            - return HttpResponseBadRequest() when submitted data is not from ajax because IE's iframe crashes with error "Access is Denied".
              For better support, all responses must be with code=200, and if any errors in form validation or somewhere else,
              pass them in data={"errors":}
        
        ALWAYS:
            - return properly configured attributes data-type, data-status, data-statusText otherwise the iframe may crash
            
        !!! The above rules are MENDATORY if the submission method is by using iframe. !!!
    '''
    
    response_form_submission = '<textarea data-type="%(data_type)s" data-status="%(status_code)s" data-statusText="%(status_text)s">%(response_body)s</textarea>';
    data = {}
    
    
    if form.is_valid():
        uploaded_file = form.save()
        if request.is_ajax():
            data = simplejson.dumps({
                'path': uploaded_file.file.url,
            })
        else:
            res_body = simplejson.dumps({
                "ok": True,
                "errors": None,
                "path": uploaded_file.file.url,
                "message": None,
            })
            data = response_form_submission % ({'status_code': '200', 'data_type':'application/json', 'status_text': 'OK', 'response_body': res_body})
    else:
        if request.is_ajax():
            data = simplejson.dumps({'errors': form.errors})
        else:
            res_body = simplejson.dumps({
                "ok": True,
                "errors": form.errors,
                "path": None,
                "message": None,
            })
            data = response_form_submission % ({'status_code': '200', 'data_type':'application/json', 'status_text': 'OK', 'response_body': res_body})
    
    return HttpResponse(data)

def preview(request, param):
    #TODO
    # Implement x-accel-redirect with protected files
    return HttpResponse(content=param, status="200")
