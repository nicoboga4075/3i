""" Controller for the app using FastAPI.

This module sets up the FastAPI application and defines endpoints for rendering 
views uppon models (MVC design).

import fastapi
fastapi_version = fastapi.__version__
isinstance(fastapi_version, str)
True

"""
import json
import logging
import os.path

from time import time

from fastapi import FastAPI, Request, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware

from google.auth.transport.requests import Request as GoogleRequest
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from Scrapper import models, views # MVC Design

SCOPES = ["https://www.googleapis.com/auth/drive.metadata.readonly"]

class PrettyJSONResponse(JSONResponse):
    def render(self, content: any) -> bytes:
        return json.dumps(content, ensure_ascii=False, indent=2).encode("utf-8")

# FastAPI Setup
app = FastAPI(
    title="Google Drive Scrapper",
    description="This is a sample API to demonstrate Google Drive scrapping.",
    version="1.0",
    contact={
        "name": "API Support",
        "email": "nicolas.bogalheiro@gmail.com",
    }
)

# CORS Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins= ["http://localhost:8008"],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"],
    max_age= 24 * 60 * 60  # One day
)

logger = logging.getLogger("uvicorn")

# Basic Middleware Setup
async def dispatch(request: Request, call_next):
    """ Middleware function for logging request details in the FastAPI application.

    This function is executed for every incoming HTTP request. It records the start time,
    processes the request, and logs the HTTP method, request URL, and the time taken.

    """
    start_time = time()
    response = await call_next(request)
    process_time = time() - start_time
    log_dict = {
        "method": request.method,
        "url": request.url.path,
        "status_code": response.status_code,
        "process_time": process_time
    }
    if response.status_code == 200:
        logger.info("Request succeeded", extra=log_dict)
    else:
        logger.error("Request failed", extra=log_dict)
    return response

app.add_middleware(BaseHTTPMiddleware, dispatch = dispatch)

# Custom Open API Tags Setup
tags_metadata = [
    {
        "name": "Endpoints",
        "description": "",
    }
]
app.openapi_tags = tags_metadata

# Gives access to static directory at the beginning
@app.on_event("startup")
def startup_event():
    """ Mounts the static directory to serve static files on startup.
    
    >>> app = FastAPI()
    >>> startup_event()
    >>> import os
    >>> os.path.exists(os.path.join("Scrapper/static", "favicon.ico"))
    True
    
    """
    logger.info("Started API.")
    app.mount("/static", StaticFiles(directory="Scrapper/static"), name="static")
    logger.info("Mounted static files.")

@app.get("/", response_class=HTMLResponse, status_code=status.HTTP_200_OK,
description = "Renders the index page with a welcome message.", tags = ["Endpoints"])
def index(request: Request):
    message = "Welcome to Google Drive Scrapper !"
    icon = "info"
    response = views.IndexView().render(request, message = message, icon = icon)
    return response

@app.get("/home", response_class=HTMLResponse, status_code=status.HTTP_200_OK,
description = "Renders the home page (same as / but without welcome message).", tags = ["Endpoints"])
def home(request : Request):
    """
    >>> from unittest.mock import MagicMock
    >>> request = MagicMock()
    >>> response = home(request)
    >>> response.status_code == 200
    True
    """
    response = views.IndexView().render(request, message = None, icon = None)
    return response

@app.post("/scrap", response_class=PrettyJSONResponse, status_code=status.HTTP_200_OK,
description = ".", tags = ["Endpoints"])
def scrap():
    """Shows basic usage of the Drive v3 API.
    Prints the names and ids of the first 10 files the user has access to.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(GoogleRequest())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w", encoding="utf-8") as token:
            token.write(creds.to_json())
    try:
        service = build("drive", "v3", credentials=creds)
        # Call the Drive v3 API
        results = (service.files().list(pageSize=10, fields="nextPageToken, files(id, name)").execute()) # pylint: disable=no-member
        items = results.get("files", [])
        if not items:
            print("No files found.")
            return
        print("Files:")
        for item in items:
            print(f"{item['name']} ({item['id']})")
        return items
    except HttpError as error:
        # Handle errors from the Drive API
        logger.error(f"An error occurred while calling the Drive API: {error}")
        if error.resp.status == 403:
            print("Access denied: Please check your permissions or quota limits.")
        elif error.resp.status == 401:
            print("Unauthorized: Credentials are invalid or have expired.")
        else:
            print(f"HTTP error code: {error.resp.status}")
    except Exception as exception:
        # Handle other exceptions
        logger.error(f"An unexpected error occurred: {exception}")
