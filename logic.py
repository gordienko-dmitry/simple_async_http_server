import logging
import re
from datetime import datetime
import os
from httpd import OK, NOT_FOUND, FORBIDDEN, BAD_METHOD
from collections import namedtuple
from urllib.parse import unquote

SERVER_NAME = "genZ"

CONTENT_TYPE = {
    ".html": "text/html",    
    ".txt": "text/plain",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
    ".png": "image/png",
    ".js": "application/javascript",
    "css": "text/css",
    ".swf": "application/x-shockwave-flash"
}


def get_headers(length=0, c_type=""):
    """make headers for response"""
    headers = {}
    headers["Date"] = datetime.strftime(datetime.utcnow(), "%a, %d %b %Y %H:%M:%S GMT")
    headers["Server"] = SERVER_NAME
    headers["Content-Length"] = length
    headers["Content-Type"] = c_type
    headers["Connection"] = "keep-alive"
    return headers


def get_response_with_body(url, r, method):
    """getting request with body"""
    if url.endswith("/"):
        url += "index.html"

    for key, value in CONTENT_TYPE.items():
        if url.endswith(key):
            c_type = value
            break
    else:
        return NOT_FOUND, method, get_headers(), b""

    try:
        with open(os.path.join(r, url), "rb") as f:
            body = f.read()
        return OK, method, get_headers(len(body), c_type), body
    except IOError:
        logging.error("error in reading file {}".format(os.path.join(r, url)))
        return NOT_FOUND, method, get_headers(), b""


def get_response(data_b, document_root):
    """getting response in namedtuple for request"""
    ResponseTuple = namedtuple("response_params", ["status", "method", "headers", "body"])

    data = data_b.decode("UTF-8")
    head, _ = re.split("\r\n\r\n", data, 1)

    headers_list = head.split("\r\n")
    matches = re.match("(GET|HEAD)\s*\/?([^\s\?]+)", headers_list.pop(0))

    if matches is None:
        return ResponseTuple(BAD_METHOD, "", get_headers(), b"")

    method, url = matches.groups()

    # Now headers not used, but who know
    #headers = {}
    #for v in headers_list:
    #    (name, value) = re.split('\s*:\s*', v, 1)
    #    headers[name] = value

    url = unquote(url)
    if re. match("../", url):
        return ResponseTuple(FORBIDDEN, method, get_headers(), b"")

    return ResponseTuple(*get_response_with_body(url, document_root, method))
