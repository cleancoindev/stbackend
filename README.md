# Showtime Django Backend

This Django app serves up crypto goodness to the React frontend. The production endpoint can be found at `https://showtimenft.wl.r.appspot.com/`

## Usage examples

**Token**

GET: `/api/v1/token/0x0000000000001b84b1cb32787b0d64758d019317/3259539015542658014133428223780909702996875844353040978646893663363117613056`

POST: `/api/v1/token/0x0000000000001b84b1cb32787b0d64758d019317/3259539015542658014133428223780909702996875844353040978646893663363117613056` // json body: { "action": "like", "user_email": "test@gmail.com" }

**Search**

GET: `/api/v1/search?q=Lil+Miquela`

**Homepage**

GET: `/api/v1/featured`

GET: `/api/v1/leaderboard`

**Profile**

GET: `/api/v1/profile/0xd3e9d60e4e4de615124d5239219f32946d10151d`

**Contract**

GET: `/api/v1/contract/0xd1e5b0ff1287aa9f9a268759062e4ab08b9dacbe`


## Running locally

This app was designed to run on `Python 3.8`, which is the highest version supported by Google App Engine as of writing. 

After installing the dependencies in `requirements.txt`, run the following command to kick off the server:

```sh
$ python manage.py runserver
```

Then visit `http://localhost:8000/api/` to view the app. Note the `/api/` on the end - there is nothing at the root path.

## Syncing database changes

These commands may need to be run if your test database has never been set up or is outdated:

```sh
$ python manage.py makemigrations
$ python manage.py migrate
```

## Making static files work

To make static files work in production, you have to run this command. It collects static files from each of the modules and puts them into a dedicated `/static/` folder at the root of the project.

```sh
$ python manage.py collectstatic
```

**Do not edit files in the root `/static/` folder directly. Changes need to be made in the `/<module_name>/static/` folders instead**
