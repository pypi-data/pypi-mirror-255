# Created with the help of the ChatGPT (GPT-3.5)
# REF: https://chat.openai.com/share/4ab741e7-8059-4be1-b3da-46b8e78d98cc
# REF: https://gealber.com/gzip-middleware-fastapi
import os
import gzip
from starlette.types import Message
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

verbose = bool(os.environ.get('VERBOSE', ''))


class GZipRequestMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        content_encoding = request.headers.get('Content-Encoding', '').lower()
        if (verbose):
            print("content_encoding", content_encoding)
        if 'gzip' in content_encoding:
            try:
                body = await request.body()
                content_length = int(
                    request.headers.get('Content-Length', '0'))
                if len(body) != content_length:
                    return JSONResponse(
                        content={"error": "Invalid Content-Length header"},
                        status_code=400,
                    )
                body = gzip.decompress(body)
                request._body = body
                if (verbose):
                    print("content_length", content_length)
                    print("gzip decompressed body:", body)
            except ValueError:
                return JSONResponse(
                    content={"error": "Invalid Content-Length header"},
                    status_code=400,
                )
            except Exception as e:
                print(e)
                return JSONResponse(
                    content={"error": "Failed to decompress gzip content"},
                    status_code=400,
                )

        response = await call_next(request)
        return response
