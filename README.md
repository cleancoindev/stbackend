# Showtime Django Backend

This Django app serves up crypto goodness to the React frontend.


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