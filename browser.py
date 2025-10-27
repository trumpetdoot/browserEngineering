import socket
import ssl

class URL: 
    def __init__(self, url):
        if '://' not in url:
            self.scheme, content = url.split(':', 1)
            assert self.scheme in 'data'
        else:
            self.scheme, url = url.split("://", 1)
            assert self.scheme in [ "http", "https", "file" ]

        if self.scheme == "http":
            self.port = 80
        elif self.scheme == "https":
            self.port = 443
        elif self.scheme == "file": 
            self.path = url
            return
        elif self.scheme == "data":
            self.media, self.data = content.split(',', 1)
            return


        if '/' not in url:
            self += "/"
        self.host, url = url.split("/", 1)
        self.path = "/" + url

        # Custom port support
        if ":" in self.host:
            self.host, port = self.host.split(":", 1)
            self.port = int(port)

    # Method won't work if you're offline / behing a proxy / complex environment
    def request(self):
        if self.scheme == "file":
            with open(self.path, 'rb') as f: 
                content = f.read()
            return b"HTTP/1.1 200 OK\r\n\r\n" + content
        elif self.scheme == "data":
            if self.media.split("/", 1)[0] == 'text':
                return "HTTP/1.1 200 OK \r\nContent-Type: {}\r\n\r\n{}".format(self.media, self.data + '\r\n')

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

        request = "GET {} HTTP/1.1\r\n".format(self.path)
        request += "Connection: {}\r\n".format("close")
        request += "User-Agent: {}\r\n".format("Andy")
        request += "Host: {}\r\n".format(self.host)
        request += "\r\n"
        s.send(request.encode("utf8")) # Converts python string to bytes
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
    i = 0
    while i < len(body):
        if body[i] == '<':
            in_tag = True
        elif body[i] == '>':
            in_tag = False
        
        if not in_tag and body[i] == '&':
            # Check for HTML entities
            if i + 4 <= len(body) and body[i:i+4] == "&lt;":
                print('<', end="")
                i += 3  # Skip the remaining "lt;"
            elif i + 4 <= len(body) and body[i:i+4] == "&gt;":
                print('>', end="")
                i += 3  # Skip the remaining "gt;"
            elif i + 5 <= len(body) and body[i:i+5] == "&amp;":
                print('&', end="")
                i += 4  # Skip the remaining "amp;"
            else:
                # Not a recognized entity, print the '&' normally
                print(body[i], end="")
        elif not in_tag:
            print(body[i], end="")
        i += 1


def load(url):
        body = url.request()
        show(body)

if __name__ == "__main__":
    import sys
    load(URL(sys.argv[1]))
