from . import settings
import mimetypes
import os
from urllib import parse

STATUSES = {
    10: "INPUT",
    11: "SENSITIVE INPUT",
    20: "SUCCESS",
    30: "REDIRECT - TEMPORARY",
    31: "REDIRECT - PERMANENT",
    40: "TEMPORARY FAILURE",
    41: "SERVER UNAVAILABLE",
    42: "CGI ERROR",
    43: "PROXY ERROR",
    44: "SLOW DOWN",
    50: "PERMANENT FAILURE",
    51: "NOT FOUND",
    52: "GONE",
    53: "PROXY REQUEST REFUSED",
    59: "BAD REQUEST",
    60: "CLIENT CERTIFICATE REQUIRED",
    61: "CERTIFICATE NOT AUTHORISED",
    62: "CERTIFICATE NOT VALID"
}

mimetypes.init()

for mime_type in settings['MIME_TYPES']:
    for extension in settings['MIME_TYPES'][mime_type]:
        mimetypes.add_type(mime_type, extension)


class GeminiResponse:

    def __init__(self, status, body=None, meta=None):
        # print(body)
        self._status = status
        self._body = body
        self._meta = meta

    @property
    def header(self):
        response_header = self._status
        if self._meta is not None:
            response_header = f"{self._status} {self._meta}"
        return f"{response_header}\r\n".encode('UTF-8')

    @property
    def body(self):
        return self._body        


class GeminiException(Exception):
    
    def __init__(self, code, meta="No further information provided."):
        self.code = code
        self.meta = meta

    def __str__(self):
        return f"<GeminiException: {self.code} {STATUSES[self.code]}>"        

    def response(self):
        return GeminiResponse(self.code, STATUSES[self.code])
        

class GeminiRequest:

    url = None
    host = None
    path = None

    def __init__(self, *args):
        self.url = args[0]
        url_info = parse.urlparse(args[0])
        if url_info.scheme != 'gemini':
            raise GeminiException(59, f"URL schema `{url_info.scheme}` is not supported")
        # TODO use netloc to determine document root as configured in settings.yaml; try default first, then virtual_hosts, then raise exception if it host is not defined
        # TODO if user directories are enabled, expand the '/~username' portion of the path to the system $HOME/username
        self.host = url_info.netloc
        self.path = url_info.path

    @property
    def resource_path(self):
        return f"{settings['DOCUMENT_ROOT']}{self.path}"

    @property
    def resource_filename(self):
        return os.path.split(self.resource_path)[-1]

    @property
    def resource_mime_type(self):
        """
        Attempts to determine the MIME type of the requested resource
        """
        mime_type = mimetypes.guess_type(self.resource_filename)
        return mime_type[0]

    def handle(self):
        """
        Handle the request. Attempts to load the requested resource and return a GeminiResponse object.
        """
        if not os.path.exists(self.resource_path):
            raise GeminiException(51, meta=f"`{self.path}` Not Found")
        try:
            with open(self.resource_path, 'rb') as f:
                data = f.read()
            return GeminiResponse(20, data, meta=self.resource_mime_type)
        except PermissionError as e:
            raise GeminiException(50, meta="Permission Denied")
