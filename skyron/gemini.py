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
    def status(self):
        return self._status

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
    
    def __init__(self, code, meta=None):
        self.code = code
        self.meta = meta

    def __str__(self):
        return f"<GeminiException: {self.code} {STATUSES[self.code]}>"        

    def response(self):
        if self.meta is not None:
            response_meta = self.meta
        else:
            response_meta = STATUSES[self.code]
        return GeminiResponse(self.code, meta=response_meta)
        

class GeminiRequest:

    url = None
    host = None
    path = None
    is_index = False

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

    def _get_index(self, index_path):
        """
        Builds Gemini markup listing and linking to all of the files in the given path.
        """
        files = os.listdir(index_path)  
        index = [f"# Index of {self.path}\r\n"]              
        for f in files:
            index.append(f"=> {self.path}{f} {f}")
        index = "\r\n".join(index) + "\r\n" 
        return index

    def _get_body(self, resource_path):
        """
        Load requested content or build file listings
        """
        try:
            # If resource_path is a file, load its contents and return it
            with open(self.resource_path, 'rb') as f:
                data = f.read()
                return data, self.resource_mime_type
        except IsADirectoryError as e:
            # If the result is a directory, check whether there's an index file
            index_path = f"{resource_path}{os.path.sep}{settings['INDEX_FILE']}"
            if os.path.exists(index_path):
                with open(index_path, 'rb') as f:
                    data = f.read()
                    return data, 'text/gemini'
            elif settings['AUTO_INDEX']:
            # If there's no index file and AUTO_INDEX is enabled, get a file list, build index markup, and return it         
                index = self._get_index(resource_path)
                return index.encode("UTF-8"), 'text/gemini'
            else:
                # If there's no index file and AUTO_INDEX is NOT enabled, raise a not found exception.
                raise GeminiException(51, f"No index found")

    def dispatch(self):
        """
        Handle the request. Attempts to load the requested resource and return a GeminiResponse object.
        """
        # TODO resolve document root based on host

        if not os.path.exists(self.resource_path):
            raise GeminiException(51, meta=f"`{self.path}` Not Found")
        
        data, mime_type = self._get_body(self.resource_path)
        
        return GeminiResponse(20, data, meta=mime_type)       
