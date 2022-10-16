# Asynchronous download microservice

Microservice serves requests for downloading archives with files. Files are uploaded to the server via FTP or CMS admin panel.
The archive is created at the request of the user. The archive is not saved to disk, it is immediately sent to the user for download.
The archive is protected from unauthorized access by a hash in the address of the download link, for example: `http://host.ru/archive/7kna/`. The hash is set by the name of the directory with files.

## Prerequisites

- Linux operating system;
- Python 3.10.

## Installing

- Download the project files;
- It is recommended to use [venv](https://docs.python.org/3/library/venv.html?highlight=venv#module-venv) for project isolation.
- Set up packages:

```bash
pip install -r requirements.txt
```

## Running

```bash
python server.py
```

The server will start on port 8080, to check its operation, go to [http://127.0.0.1:8080/](http://127.0.0.1:8080/).

## Deploying on the server

```bash
python server.py
```

Redirect requests starting with `/archive/` to the microservice, e.g.:

```bash
GET http://host.ru/archive/3bea29ccabbbf64bdebcc055319c5745/
GET http://host.ru/archive/af1ad8c76fda2e48ea9aed2937e972ea/
```

## Settings

- Set up environmental variables in your operating system or in the .env file. The variables are:
  - `DEBUG_MODE` is used to output logs, False by default;
  - `RESPONSE_DELAY` is a pause for sending every chunk of the archive, 0 by default;
  - `FOLDER_PATH` is a path to photos folder, test_photos by default

To set up variables in .env file, create it in the root directory of the project and fill it up like this:

```bash
DEBUG_MODE=True
RESPONSE_DELAY=2
FOLDER_PATH=my_folder
```

- You can use command line arguments to specify debug mode, response delay and folder path, e.g.:

```bash
python server.py --debug_mode --response_delay 1 --folder_path my_photos
```

To find out more, run:

```bash
python server.py -h
```

## Project goals

The project was created for educational purposes.
It's a lesson for python and web developers at [Devman](https://dvmn.org).
