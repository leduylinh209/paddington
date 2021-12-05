# paddington

> Backend server for paddington. This guy will serve the mobile apps and work with the supplier APIs.

## Setup local environment

I don't use virtual machine or docker for speed and simplicity. You should own
a mac or ubuntu for a convenient work.

### 1. Install virtualenv

```
pip install virtualenv
virtualenv -p python3 env
. env/bin/activate

pip install -r requirements/dev.txt
```

### 2. Fire up

```
bin/runserver.sh
```

This script will create a local sqlite3 db, run migrations and start a server
for you at http://localhost:8000.

Enjoy!


## Deploy to a server

I use docker-compose for now, if the app become big I will consider move it to
k8s later.

### 1. Install docker, docker-compose on your server

### 2. Clone the repository and build it

```
make
```

### 3. Start it up

You will need to change credentials in `docker-compose.yml` file before
starting the server, then fire it up

```
make run
```

## FAQ

### 1. I can't run "bin/runserver.sh", what should I do?

Make sure you are in the project folder, which contains this README file.


### 2. I own a Windows, now what?

Install Ubuntu on your machine then come back later.

### 3. `make` and `make run` sounds magic, what are they?

Read the `Makefile` then you will know, it just calls other longer commands
for you.
