"""
A library to convert any data to a data: URI.
"""
from __future__ import annotations
import mimetypes
import base64 as _b64
# importing io for the type read by the open() function
import io

mimetypes.init()

def plainURI(string: str):
    """
    Create a plain text URI.
    """
    return f"data:text/plain;base64,{_b64.b64encode(bytes(string, encoding='utf-8')).decode()}"

def readURI(uri: str):
    """
    Reads a data: URI that is encoded in Base64.
    """
    urisep = uri.split(",")
    urisep.pop(0)
    uri = ",".join(urisep)
    return _b64.b64decode(uri).decode()

def fileToURI(file: io.TextIOWrapper | str, mimeType: str | None = None):
    """
    Converts a file to a URI. The file paramater can be a filename.
    """
    if mimeType == None:
        if type(file) == io.TextIOWrapper:
            mimeType = mimetypes.guess_type(file.name)[0]
        else:
            print(mimetypes.guess_extension(file))
            mimeType = mimetypes.guess_extension(file)[0]
    if type(file) == str:
        file = open(file)
    return f"data:{mimeType};base64,{_b64.b64encode(bytes(file.read(), encoding='utf-8')).decode()}"

def downloadFromURI(uri: str, filename: str):
    with open(filename) as f:
        f.write(readURI(uri))