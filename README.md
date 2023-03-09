# Pirouz Web Framework

A web framework built with Python.

# Developing ...

gunicorn -w 4 wsgi:app
gunicorn -w 4 wsgi:app --reload
pytest pirouz/test/ -v