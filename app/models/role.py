# We have defined `Role` in `app.models.user` to avoid circular imports, 
# but it's cleaner to separate them or have an __init__.py that imports all.
# Since we put both in user.py for the secondary table to work easily, 
# we'll just expose them in `app/models/__init__.py`.
