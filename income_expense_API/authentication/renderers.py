from rest_framework import renderers
import pdb
import json


class UserRenderer(renderers.JSONRenderer):
    charset = 'utf-8'
    
    def render(self, data, accepted_media_type = None, render_content = None):

        # pdb.set_trace()
        if 'ErrorDetail' in str(data):
            response = json.dumps({'errors': data})
            
        else:
            response = json.dumps({'data': data})
            
        return response