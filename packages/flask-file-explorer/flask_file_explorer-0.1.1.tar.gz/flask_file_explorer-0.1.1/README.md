# flask-file-explorer
- [flask-file-explorer](#flask-file-explorer)
  - [Why](#why)
  - [Features](#features)
  - [A quick and easy web based file explorer](#a-quick-and-easy-web-based-file-explorer)
  - [Installation](#installation)
  - [Security](#security)
    - [Flask-Login with a blueprint](#flask-login-with-a-blueprint)


## Why
This tool is just a simple flask tool to view a configurable file system in flask.
Handy for docker deployments, debugging, validating something is in the right place etc...

There is no security built into it, so you have to bring your own.
See [Flask-Login with a blueprint](#flask-login-with-a-blueprint) as an example.



## Features
~~Todos~~ ToDones: 
- [X] Upload forms aware of current directory
- [X] Drag & Drop Upload
- [X] Visual treatment of current directory
- [X] Folder and File listing
- [X] Blueprint
- [X] Dynamic data retrieval
- [X] Collapsing tree structure
- [X] Remove closed directory tree
- [X] Secure file browsing and uploads
- [ ] Custom theming and embedding 

## A quick and easy web based file explorer

Flask-file-explorer supports navigating through directories, viewing files, downloading / uploading files

* File System Explorer

<img src="https://raw.githubusercontent.com/thevgergroup/flask-file-explorer/main/docs/images/flask_file_explorer.png" width="400px" height="300px" alt="Flask File Explorer">


* File Viewer
 
<img src="https://raw.githubusercontent.com/thevgergroup/flask-file-explorer/main/docs/images/flask_file_view.png" alt="Flask File Viewer" width="400px" height="300px">

## Installation 
Standard install

```sh
poetry add flask-file-explorer
# or
pip install flask-file-explorer
# or 
poetry add git+https://github.com/thevgergroup/flask-file-explorer
```

Within your flask app, simply add the file explorer blueprint and specify the directory to limit access to

```python
'''
This is the main file of the Flask application.
It registers the file_explorer blueprint and starts the server.
'''
from flask import Flask

from flask_file_explorer.file_explorer import file_explorer_bp  # The blueprint code
from flask_file_explorer.filters import register_filters        # Filters used in the viewer

app = Flask(__name__)

app.config["FFE_BASE_DIRECTORY"] = 'flask_file_explorer/static'         # The directory the explorer is limited to
app.register_blueprint(file_explorer_bp, url_prefix='/file-explorer')   # Add the blueprint to the flask app
register_filters(app)                                                   # Register the filter



if __name__ == '__main__':
    app.run()

```

Once your start your app, you should be able to go to http://..../file-explorer/browse


## Security

There are a couple of security items
1. All file paths are verified as being in the FFE_BASE_DIRECTORY 
   * The absolute path is used to verify the file and it's relativity to the FFE_BASE_DIRECTORY 
2. Authentication and Authorization are a bring your own model
   * Example provided below


### Flask-Login with a blueprint


```python
from flask import Flask, Response, redirect, url_for, request, session, abort
from flask_login import LoginManager, UserMixin, current_user, \
                                login_required, login_url, login_user, logout_user 
                                
from flask_file_explorer.file_explorer import file_explorer_bp  # The blueprint code
from flask_file_explorer.filters import register_filters        # Filters used in the viewer


app = Flask(__name__)


app.config["FFE_BASE_DIRECTORY"] = 'templates'         # The directory the explorer is limited to
app.register_blueprint(file_explorer_bp, url_prefix='/file-explorer')   # Add the blueprint to the flask app
register_filters(app)                                                   # Register the filter

@app.before_request
def check_for_login():
    # Define a list of protected routes within the third-party blueprint
    protected_routes = '/file-explorer'
    if request.path.startswith(protected_routes):
        if not current_user.is_authenticated:
            # Redirect to login page if the user is not authenticated
            return redirect(login_url('login', request.url))



```


