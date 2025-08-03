""" Controller for the app using FastAPI.

This module sets up the FastAPI application and defines endpoints for rendering 
views uppon models (MVC design).

import fastapi
fastapi_version = fastapi.__version__
isinstance(fastapi_version, str)
True

"""
from fastapi import FastAPI
from Scrapper import models, views # MVC Design

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

@app.get("/")
def index():
    return "Hello World"