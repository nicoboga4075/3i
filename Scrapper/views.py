""" Views for the app using Jinja2. 

import jinja2
jinja2_version = jinja2.__version__
isinstance(jinja2_version, str)
True

"""
from fastapi import Request
from fastapi.templating import Jinja2Templates

class BaseView:
    """ Base class for views

    This class handles the initialization of Jinja2Templates and provides
    a method for rendering templates based on the class name.

    >>> view = BaseView()
    >>> isinstance(view.templates, Jinja2Templates)
    True
    >>> view.template_name
    'base.html'

    """
    def __init__(self):
        """ Initializes Jinja2Templates with the specified directory.

        """
        self.templates = Jinja2Templates(directory="Scrapper/static")

    @property
    def template_name(self):
        """ Dynamically derives the template name from the class name.

        """
        return f"{self.__class__.__name__.lower().replace('view', '')}.html"

    def render(self, request: Request, response : dict):
        """ Renders a template with the provided request and response.
        
        >>> class MockRequest:
        ...     pass
        ...
        >>> class MockResponse(dict):
        ...     pass
        ...
        >>> view = BaseView()
        >>> rendered = view.render(MockRequest(), MockResponse())
        >>> 'body' in rendered.body.decode()  # Checks if block content is included in response
        True

        """
        return self.templates.TemplateResponse(self.template_name, {"request": request, **response})

class IndexView(BaseView):
    """ View for the index/home page

    This view is responsible for rendering the main page, which includes
    a welcome message and computing operations.

    >>> view = IndexView()
    >>> view.template_name
    'index.html'

    """
    def render(self, request: Request, **response):
        """ Renders a template for home page (welcoming and computing).
        
        >>> class MockRequest:
        ...     pass
        ...
        >>> view = IndexView()
        >>> mock_response = {"message": "Hello", "icon": "success"}
        >>> rendered = view.render(MockRequest(), **mock_response)
        >>> 'Hello' in rendered.body.decode()  # Checks if welcome message is included
        True
        >>> 'success' in rendered.body.decode()  # Checks if icon type is included
        True

        """
        message = response.get('message')
        icon = response.get('icon')
        return super().render(request, {"message": message, "icon": icon})

class ResultsView(BaseView):
    """ View for displaying scrapped results

    This view is responsible for rendering the scrapped results.

    >>> view = ResultsView()
    >>> view.template_name
    'results.html'

    """
    def render(self, request: Request, **response):
        """ Renders a template for scrapping
        
        >>> class MockRequest:
        ...     pass
        ...
        >>> view = ResultsView()
        >>> mock_results = [{"id": "1", "name": "toto.mp4", "mimeType":"video/mp4"}]
        >>> mock_response = {"results": mock_results}
        >>> rendered = view.render(MockRequest(), **mock_response)
        >>> len(rendered.body.decode()) > 0 # Checks if response body is not empty
        True
        >>> any(str(result['result']) in rendered.body.decode() for result in mock_results)
        True

        """

        return super().render(request, {"results" : response.get('results',[])})
