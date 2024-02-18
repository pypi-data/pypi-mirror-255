class DataDomeMetadata:
    """Metadata information
    to be sent inside the header object
    to the DataDome Fraud API

    Attributes:
        accept: Request Accept header
        acceptCharset:  Request Accept-Charset header
        acceptEncoding: Request Accept-Encoding header
        acceptLanguage: Request Accept-Language header
        addr: The IP address from which the user is viewing the request
        clientIp: IP address of the host originating the request,
        clientID: From Cookie name datadome - contains unique client ID
        connection: Check Keep-Alive, from request Header if present
        contentType: Request content-type
        from: HTTP from
        host: Request host
        port: Request port
        method: HTTP method
        origin: Request Origin header
        protocol: Scheme part of the Request-URI (http or https)
        referer: Request referer
        request: Path and query part of the Request-URI
        serverHostname: Virtual host
        userAgent: Request User-agent
        xForwardedForIp: List of client and intermediate proxies/load-balancers IPs
        xRealIP: Request X-Real-IP header


    """

    # Length of the name of the datadome cookie
    DATADOME_COOKIE_NAME_LEN = 9

    def __init__(self, request):
        headers = {header.lower(): value for header, value in request.headers.items()}
        # accept
        self.accept = self.truncate(headers.get("accept", ""), 512)
        # acceptCharset
        self.acceptCharset = self.truncate(headers.get("accept-charset", ""), 128)
        # acceptEncoding
        self.acceptEncoding = self.truncate(headers.get("accept-encoding", ""), 128)
        # acceptLanguage
        self.acceptLanguage = self.truncate(headers.get("accept-language", ""), 256)
        # addr
        if hasattr(request, "remote_addr"):
            self.addr = request.remote_addr
        else:
            self.addr = "127.0.0.1"  # default to localhost as this field is required
        # clientIp
        if hasattr(request, "environ") and "REMOTE_ADDR" in request.environ:
            self.clientIp = request.environ["REMOTE_ADDR"]
        # clientID
        if self.get_client_id(headers) is not None:
            self.clientID = self.truncate(self.get_client_id(headers), 128)
        # connection
        self.connection = self.truncate(headers.get("connection", ""), 128)
        # contentType
        self.contentType = self.truncate(headers.get("content-type", ""), 64)
        # from
        self.From = self.truncate(headers.get("from", ""), 128)
        # host and port
        if headers.get("host", "").find(":") > 0:
            self.port = int(headers.get("host")[headers.get("host").index(":") + 1 :])
            self.host = self.truncate(
                headers.get("host")[: headers.get("host").index(":")], 512
            )  # noqa: E501
        else:
            self.host = self.truncate(headers.get("host", ""), 512)
        # method
        if hasattr(request, "method"):
            self.method = request.method
        else:
            request.method = None
        # origin
        self.origin = self.truncate(headers.get("origin", ""), 512)
        # protocol
        if hasattr(request, "scheme"):
            self.protocol = request.scheme
        else:
            self.protocol = None
        # referer
        self.referer = self.truncate(headers.get("referer", ""), 1024)
        # request
        if hasattr(request, "full_path"):
            self.request = self.truncate(request.full_path, 2048)
        else:
            self.request = None
        # serverHostname
        if hasattr(request, "host_url"):
            self.serverHostname = self.truncate(request.host_url, 512)
        else:
            self.serverHostname = None
        # userAgent
        self.userAgent = self.truncate(headers.get("user-agent", ""), 768)
        # xForwardedForIp
        self.xForwardedForIp = self.truncate(headers.get("x-forwarded-for", ""), -512)
        # xRealIP
        self.xRealIp = self.truncate(headers.get("x-real-ip", ""), 128)

    def get_client_id(self, headers):
        """Gets the value of the datadome cookie"""
        cookies = headers.get("cookie", None)

        client_id = None

        if cookies:
            start = cookies.find("datadome=")
            if start >= 0:
                left_trim = cookies[start + self.DATADOME_COOKIE_NAME_LEN :]
                if len(left_trim) > 0:
                    end = left_trim.find(";")
                    if end > 0:
                        client_id = left_trim[:end]
                    else:
                        client_id = left_trim

        return client_id

    @staticmethod
    def truncate(value, max_length):
        if value is None or len(value) < max_length:
            return value
        else:
            if max_length < 0:
                return value[max_length:]
            else:
                return value[:max_length]
