# Bookshare 3-Legged OAuth2 Example
## Using Python 3 and web.py

### Prerequisites
* Python 3.6
* pipenv 
* An API key registered with Bookshare
* A list of redirect (callback) URIs registered with Bookshare
  * The address where you host this example + ```/callback``` needs to be one of the registered URIs to see the callback work in this app.
  * The address can be ```http://0.0.0.0:[port]/``` (which is what web.py defaults to) because your browser will be redirecting to it, and your browser knows where that is.

### Installation

web.py is giving me some difficulties with the standard pipenv installation so I recommend installing with skip-lock.

From the project root directory, run:

```
pipenv install --skip-lock
```

### Running the Example

From the project root directory, run:
```
pipenv run python 3legged.py 9777
```

where 9777 can be substituted for any free port on your machine.  Once it starts running, the address of the server will be displayed in the console like

```
 $ pipenv run python 3legged.py 9777
http://0.0.0.0:9777/
```

and you can go to that address to see the application.
