import socket

class URL: 
    def __init__(self, url):
        self.scheme, url = url.split("://", 1)
        assert self.scheme == "http"

        if '/' not in url:
            self += "/"
        self.host, url = url.split("/", 1)
        self.path = "/" + url
    # Method won't work if you're offline / behing a proxy / cmoplex environment
    def request(self):
        # Socket for communicating with server
        s = socket.socket(
            family=socket.AF_INET,
            type=socket.SOCK_STREAM,
            proto=socket.IPPROTO_TCP,
        )
        s.connect((self.host, 80))

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


