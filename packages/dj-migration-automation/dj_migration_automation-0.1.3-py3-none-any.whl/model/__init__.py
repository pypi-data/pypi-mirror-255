import pkgutil

# __path__ = pkgutil.extend_path(__path__, __name__)
for importer, modname, ispkg in pkgutil.iter_modules(path=__path__, prefix=__name__+'.'):
    __import__(modname)

__author__ = 'mediatb'
