import logging
import socket
import sys

def retrieve_url(url):
    """
    return bytes of the body of the document at url
    """
    try:
        chunk = bytes()
        head=bytes()
        status=""
        type=""
        location=""
        buf=1
        chnk=b''
        chnklen=0
        data=b''
        url= url.split('/',3)
        host= url[2]
        print(host)
        port = 80
        if ":" in host:
            port=int(host.split(":")[1])
            host=host.split(":")[0]
        if len(url)<=3:
            request = f"GET / HTTP/1.1\r\nHost: {host}:{port}\r\nConnectiopn: close\r\n\r\n".encode()
        else:
            dir_path = url[3]
            request = f"GET /{dir_path} HTTP/1.1\r\nHost: {host}:{port}\r\nConnectiopn: close\r\n\r\n".encode()
        s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.connect((host,port))
        s.sendall(request)
        while b'\r\n\r\n' not in head:
            chunk = s.recv(buf)
            if not chunk:
                break
            else:
                head+=chunk
        head = head.split(b'\r\n')
        for l in head:
            if b'HTTP/1.1 ' in l:
                status=l[len(b'HTTP/1.1 '):].decode()
            if b'Location:' in l:
                location=l[len(b'Location:'):].decode()
            if b'chunked' in l:
                type="chunked"
            if b'Content-Length:' in l:
                buf=int(l[len(b'Content-Length:'):])
        if status == "200 OK":
            if type=="chunked":    
                while buf != 0:    
                    while b'\r\n' not in chnk:  
                        chnk+=s.recv(1)
                    buf=int(chnk.decode()[:-2],16)
                    chnk=b''  
                    data+=s.recv(buf)
                    s.recv(2)
                return data
            else:
                while len(data) < buf:
                    data+=s.recv(buf)
            return data
        if status == "301 Moved Permanently":
            if "/" in location[-1]:
                print("\nError 301:The page you are trying to load is moved permanently from this address \n")
                return None
            #return retrieve_url(location)
        if status == "404 Not Found":
            print("\nError 404: The page you are trying to load is not found \n")
            return None


    except Exception as e :
        if "Errno -5" in str(e):
            print("\nError: No address has been associated with the hostname\n")
        elif "Errno 111" in str(e):
            print("\nError: Non standard port number is specified. Provide a standard port number\n")
        else:
            print("Error occured ",e) 

    
if __name__ == "__main__":
    #sys.stdout.buffer.write(retrieve_url(sys.argv[1])) # pylint: disable=no-member
    retrieve_url(sys.argv[1])
    