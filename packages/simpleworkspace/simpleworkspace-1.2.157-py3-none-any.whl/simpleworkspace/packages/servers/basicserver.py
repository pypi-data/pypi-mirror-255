from base64 import b64encode
from http import HTTPStatus
from http.client import HTTPMessage
from logging import Logger
import http.server
import socketserver
from socketserver import BaseRequestHandler
from urllib.parse import urlparse, parse_qs
from simpleworkspace.logproviders import DummyLogger
import ssl
import subprocess
from functools import cached_property
from io import BytesIO

class _RequestDetails:
    Headers: HTTPMessage
    '''Dict like object containing the headers of the incoming request'''
    Method: str
    ''' The method used in the request, such as "GET", "POST"... '''
    Path: str = ''
    ''' The path part of url, example: "https://example.com/pages/index.html?key1=val1" -> "/pages/index.html" '''
    Query_GET: dict[str,str] = {}
    ''' Query params in url, example: "https://example.com/pages/index.html?key1=val1" -> {'key1': 'val1'} '''
    Query_POST: dict[str,str] = {}
    ''' Query params in request body '''
    Body: bytes = None
    ''' The raw request body '''

    @cached_property
    def Query_ANY(self):
        ''' 
        A combined dictionary consisting of both POST and GET parameters.
        If a param exists in both POST and GET query, then GET will be preffered
        '''
        return {**self.Query_POST, **self.Query_GET}

class _ResponseDetails:
    Headers: dict[str, str] = {'Content-Type': 'text/html'}
    ''' Specify headers that will be sent to client. Note: server might additionally add some extra standard headers by default '''
    StatusCode = HTTPStatus.OK
    ''' Specifies the status code client will recieve '''
    Data: BytesIO|bytes|str = BytesIO()
    ''' The data client will recieve. By default is an BytesIO which can efficently be written to, otherwise you can also directly set Data to be a str or bytes like object '''

    def _GetDataBytes(self):
        dataType = type(self.Data)
        if(dataType is str):
            return self.Data.encode('utf-8')
        elif(dataType is bytes):
            return self.Data
        elif(dataType is BytesIO):
            return self.Data.getvalue()
        else:
            raise TypeError(f'Invalid type supplied in ResponseDetails.Data... Got: {dataType}')

class BasicRequestHandler(http.server.SimpleHTTPRequestHandler):
    """
    Class should always be derived and supplied into BasicServer

    Properties for implementer:
    - RequestDetails    , contains all necessary request info in one place
    - ResponseDetails   , set the properties here to alter the final response to the client
    
    Methods for implementer that may be overridden:
    - BeforeRequest()   , Runs before OnRequest can be overriden to perform routines before processing the request
    - OnRequest()       , this is the main entry point to start processing the request and preparing the response, implementer can override this to suite api needs.
    - GetPage_Index()   , placeholder/boilerplate function runs on entry path '/' with empty query      (if OnRequest is not overriden)
    - OnRequest_Action(), placeholder/boilerplate function that triggers when action param is specified (if OnRequest is not overriden)
    """

    server:'BasicServer' = None # just to update intellisense
    RequestDetails: _RequestDetails
    ResponseDetails: _ResponseDetails

    class Signals:
        class StopRequest(Exception):
            '''
            Can be used to stop processing of a request in a graceful way by calling
            >>> raise self.Signals.StopRequest()
            '''



    #region Routines
    def _Routine_Authentication_Basic(self):
        if self.server.Config.Authentication._BasicKey is None:
            return # no auth configured

        if(self.RequestDetails.Headers.get('Authorization') == self.server.Config.Authentication._BasicKey):
            return

        self.ResponseDetails.Headers['WWW-Authenticate'] = 'Basic realm="Login Required"'
        self.ResponseDetails.Data = 'Authorization required.'
        self.ResponseDetails.StatusCode = HTTPStatus.UNAUTHORIZED
        raise self.Signals.StopRequest()
    
    #endregion Routines

    def _Default_BeforeRequest(self):
        '''Default Hook before OnRequest has been processed'''
        # when basic auth is enabled, checks if current client is authorized
        self._Routine_Authentication_Basic()

    def OnRequest(self):
        '''This can be overriden freely, below is simply implementing boilerplate code'''
        if(self.RequestDetails.Method == 'GET') and (self.RequestDetails.Path == '/') and len(self.RequestDetails.Query_ANY) == 0:
            self.GetPage_Index()
        elif('action' in self.RequestDetails.Query_ANY):
            data = self.RequestDetails.Query_ANY.get('data', None)
            self.OnRequest_Action(self.RequestDetails.Query_ANY['action'], data)
        
    def GetPage_Index(self):
        '''boilerplate method'''
        #self.ResponseDetails.Data = sw.io.file.Read('./index.html')

    def OnRequest_Action(self, action: str, data: str=None):
        '''boilerplate method'''


    #region Overrides
    # override, original writes to standard outputs, which fails if app is pyw
    def log_message(self, format, *args):
        self.server.logger.debug(f"{self.address_string()} - {format % args}")
    
    def handle_one_request(self):
        """Handle a single HTTP request.

        You normally don't need to override this method; see the class
        __doc__ string for information on how to handle specific HTTP
        commands such as GET and POST.

        """
        try:
            self.raw_requestline = self.rfile.readline(65537)
            if len(self.raw_requestline) > 65536:
                self.requestline = ""
                self.request_version = ""
                self.command = ""
                self.send_error(HTTPStatus.REQUEST_URI_TOO_LONG)
                return
            if not self.raw_requestline:
                self.close_connection = True
                return
            if not self.parse_request():
                return # An error code has been sent, just exit
            
            parsedUrl = urlparse(self.path)
            self.RequestDetails = _RequestDetails()
            self.RequestDetails.Headers = self.headers
            self.RequestDetails.Method = self.command
            self.RequestDetails.Path = parsedUrl.path

            def ParseUrlEncodedQuery(query:str):
                parsedQuery = parse_qs(query)
                #only keep the first matching query key, discard duplicates for simplicity
                for key in parsedQuery.keys():
                    parsedQuery[key] = parsedQuery[key][0]
                return parsedQuery
            
            self.RequestDetails.Query_GET = ParseUrlEncodedQuery(parsedUrl.query)
            if('Content-Length' in self.headers):
                self.RequestDetails.Body = self.rfile.read(int(self.headers['Content-Length']))
                if(self.headers.get('Content-Type') == 'application/x-www-form-urlencoded'):
                    self.RequestDetails.Query_POST = ParseUrlEncodedQuery(self.RequestDetails.Body.decode('utf-8'))
            
            self.ResponseDetails = _ResponseDetails()
            try:
                self._Default_BeforeRequest()
                self.OnRequest()
            except self.Signals.StopRequest:
                pass  # a graceful request cancellation
            finally:
                self.send_response(self.ResponseDetails.StatusCode)
                for key, value in self.ResponseDetails.Headers.items():
                    self.send_header(key, value)
                self.end_headers()
                self.wfile.write(self.ResponseDetails._GetDataBytes())
        except TimeoutError as e:
            # a read or a write timed out.  Discard this connection
            self.server.logger.exception("Request timed out")
            self.close_connection = True
            return
    #endregion Overrides
        


class _BasicServerConfiguration:
    class _Authentication:
        _BasicKey:str = None
    class _SSL:
        _Filepath_Certificate:str = None
        _Filepath_Privatekey:str = None
    
    def __init__(self):
        self.Port: int = None
        self.Host:str = ''
        self.Authentication = self._Authentication()
        self.SSL = self._SSL()


class BasicServer(socketserver.ThreadingTCPServer):
    def __init__(self, port: int, requestHandler: BaseRequestHandler):
        self.Config = _BasicServerConfiguration()
        self.logger = DummyLogger.GetLogger()

        super().__init__(("", port), requestHandler, bind_and_activate=False)

    def UseLogger(self, logger: Logger):
        self.logger = logger
        return self

    def UseAuthorization_Basic(self, username: str, password: str):
        """Uses http basic auth before any request is accepted, one of username or password can be left empty"""
        self.Config.Authentication._BasicKey = "Basic " + b64encode(f"{username}:{password}".encode()).decode()
        return self

    def GenerateSelfSignedSSLCertificates(self, certificateOutPath = 'cert.crt', PrivateKeyOutPath = 'cert.key'):
        if(not certificateOutPath.endswith(".crt")) or (not PrivateKeyOutPath.endswith('.key')):
            raise Exception("wrong file extensions used for certs")
        result = subprocess.run(
            ["openssl", 
                "req", "-x509", ""
                "-newkey", "rsa:4096", 
                "-keyout", PrivateKeyOutPath, "-out", certificateOutPath, 
                "-days", str(365 * 10), 
                "-nodes",
                "-subj", "/C=US/CN=*"
            ],text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        if result.returncode != 0:  # something went bad
            raise Exception(result.stderr, result.stdout)
        return self

    def UseSSL(self, certificatePath: str, PrivateKeyPath: str):
        self.Config.SSL._Filepath_Certificate = certificatePath
        self.Config.SSL._Filepath_Privatekey = PrivateKeyPath
        return self

    def serve_forever(self, poll_interval: float = 0.5) -> None:
        if self.Config.SSL._Filepath_Certificate is not None:
            self.socket = ssl.wrap_socket(self.socket,certfile=self.Config.SSL._Filepath_Certificate, keyfile=self.Config.SSL._Filepath_Privatekey, server_side=True)
        try:
            self.server_bind()
            self.server_activate()
        except:
            self.server_close()
            raise

        self.logger.info(f"Server started at port {self.server_address[1]}")
        super().serve_forever(poll_interval)

#BasicRequestHandler would be overriden for implementer
# server = BasicServer(1234, BasicRequestHandler)
# server.UseLogger(StdoutLogger.GetLogger())
# server.UseAuthorization_Basic("admin", "123")
# server.serve_forever()
