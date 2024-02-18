# Panorama Project

This project is initially intended to insert security post rules into Panorama via API.  
The project may then be expanded further. Depending on future requirements.

## Run


### Docker

```
docker run -it -p 8888:8888 bnstimo/panorama_tool
```

### Python

#### Create and change directory to the project:

````
cd /path/to/project
````

#### Check python version (The version should be 3.11, but you can try it with other versions):

```
python --version
# or
python3 --version
```

#### Create a python venv:

```
python -m venv venv
# or
python3 -m venv venv
```

#### Activate the venv:

##### macOS / Linux

```
source venv/bin/activate
```

##### Windows

```
# In cmd.exe
venv\Scripts\activate.bat

# In PowerShell
venv\Scripts\Activate.ps1
```

#### Install the tool

```
pip install panoramaTool
```

#### Start the tool

```
python -m panoramaTool
```

#### Use it

Start a browser and go to http://127.0.0.1:5000
