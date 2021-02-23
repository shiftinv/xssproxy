# xssproxy
Pseudo HTTP proxy for sending requests through a hooked web browser, using a cross-site-scripting/XSS vulnerability

---

## Install
```
pip install git+https://github.com/shiftinv/xssproxy
```


## Usage
1. Start `xssproxy`
2. Use an XSS vulnerability to make the targeted browser load `http://<ip>:8000/hook.js`
3. Send requests through the proxy on `127.0.0.1:4141` (e.g. `curl -v --proxy http://127.0.0.1:4141 http://example.com`)

```
usage: xssproxy [-h] [-wh WEB_HOST] [-wp WEB_PORT] [-ph PROXY_HOST]
                [-pp PROXY_PORT] [-d] [-t TIMEOUT] [-f HEADER]

optional arguments:
  -h, --help            show this help message and exit
  -wh WEB_HOST, --web_host WEB_HOST
                        webserver listen address (default: 0.0.0.0)
  -wp WEB_PORT, --web_port WEB_PORT
                        webserver listen port (default: 8000)
  -ph PROXY_HOST, --proxy_host PROXY_HOST
                        proxy listen address (default: 127.0.0.1)
  -pp PROXY_PORT, --proxy_port PROXY_PORT
                        proxy listen port (default: 4141)
  -d, --debug           set logging level to debug (default: False)
  -t TIMEOUT, --timeout TIMEOUT
                        proxy request timeout (set to 0 to disable) (default: 0)
  -f HEADER, --forward_header HEADER
                        names of request headers that will be forwarded by the
                        proxy (in addition to "Content-Type") (default: [])
```


## Credits
Inspired by
- [BeEF](https://github.com/beefproject/beef)'s tunneling proxy
- [raz-varren/xsshell](https://github.com/raz-varren/xsshell)
