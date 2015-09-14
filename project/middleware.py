from django.http import HttpResponsePermanentRedirect
from django.conf import settings

class SecureRequiredMiddleware(object):
    def __init__(self):
        self.paths = getattr(settings, 'SECURE_REQUIRED_PATHS')
        self.enabled = self.paths and getattr(settings, 'HTTPS_SUPPORT')

    def process_request(self, request):
        print("checking if enabled:",self.enabled)
        if self.enabled and not request.is_secure():
            print("passed the tests")
            for path in self.paths:
                print("this is the path:", path)
                if request.get_full_path().startswith(path):
                    request_url = request.build_absolute_uri(request.get_full_path())
                    secure_url = request_url.replace('http://', 'https://')
                    print("request and secure urls:",request_url," : ",secure_url)
                    print("Request headers: ", request.META)
                    return HttpResponsePermanentRedirect(secure_url)
        print("returning nothing :(")
        return None
