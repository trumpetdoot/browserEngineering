import socket
import ssl

class URL: 
    def __init__(self, url):
        self.scheme, url = url.split("://", 1)
        assert self.scheme in [ "http", "https" ]

        if self.scheme == "http":
            self.port = 80
        elif self.scheme == "https":
            self.port = 443

        if '/' not in url:
            self += "/"
        self.host, url = url.split("/", 1)
        self.path = "/" + url

        # Custom port support
        if ":" in self.host:
            self.host, port = self.host.split(":", 1)
            self.port = int(port)
        
    # Method won't work if you're offline / behing a proxy / cmoplex environment
    def request(self):
        # Socket for communicating with server
        ctx = ssl.create_default_context()
        s = socket.socket(
            family=socket.AF_INET,
            type=socket.SOCK_STREAM,
            proto=socket.IPPROTO_TCP,
        )
        s.connect((self.host, self.port))
        if self.scheme == "https":
            ctx = ssl.create_default_context()
            s = ctx.wrap_socket(s, server_hostname=self.host)

        request = "GET {} HTTP/1.0\r\n".format(self.path)
        request += "Host: {}\r\n".format(self.host)
        request += "\r\n"
        s.send(request.encode("utf8")) # Converts python strin got byteso
        response = s.makefile("r", encoding="utf8", newline="\r\n")

        statusline = response.readline()
        version, status, explanation = statusline.split(" ", 2)

        response_header = {}
        while True:
            line = response.readline()
            if line == "\r\n": break
            header, value = line.split(" ", 1)
            response_header[header.casefold()] = value.strip()

        assert "transfer-encoding" not in response_header
        assert "content-encoding" not in response_header

        content = response.read()
        s.close()
        return content

def show(body): 
        in_tag = False
        for c in body: 
            if c == '<': 
                in_tag = True
            elif c == '>':
                in_tag = False
            elif not in_tag:
                print(c, end="")

def load(url):
        body = url.request()
        show(body)

if __name__ == "__main__":
    import sys
    load(URL(sys.argv[1]))


