"""
This module runs the FastAPI application for the Scrapper project.

It uses Uvicorn as the ASGI server to serve the application 
on host localhost and port 8008 with default log configuration.

"""
import uvicorn
from Scrapper.controller import app # Gets FastAPI object from the controller

if __name__ == "__main__":
    uvicorn.run(app, host = "localhost", port = 8008)
