
import os
import os.path
import sys
import importlib
import json
import socket
from contextlib import closing

class Args:
    """
      Arg-Parser der eine Überprüfung der Argument vornimmt. 
      Wenn man beim aufruf noch nicht weiß welche Argument abgefragt werden sollen
    """
    argv = []
    i = 0
    cfg = None
    def __init__(self, argv = None):
        if argv is None:
            self.argv = sys.argv
        else:    
            self.argv = argv

    def help_requested(self):
        return self.hasFlag('help') or self.hasShortFlag('h') or '?' in self.argv
    def hasFlag(self, name):
        return '--'+name in self.argv

    def shift(self):
        res = self.argv[self.i]
        self.i += 1
        return res

    def first(self):
        return self.argv[self.i]

    def hasName(self, name):
        return name in self.argv

    def hasShortFlag(self, name):
        return '-'+name in self.argv
    def getValue(self, name, default=None):
        """
            liest --name value Parameter
        """
        for i in range(len(self.argv)-1):
            if self.argv[i]=='--'+name:
                return self.argv[i+1]
        return default
    def val(self, name, default=None):
        if self.hasFlag(name):
            return self.getValue(name, default)
        else:
            return self.env(name, default)
    def getValues(self, name):

        res = []
        for i in range(len(self.argv)-1):
            if self.argv[i] == '--'+name:
                res.append(self.argv[i+1])
        return res
    def __read_cfg(self):
        if os.path.isfile('nweb.json'):
            with open('nweb.json') as f:
                self.cfg = json.load(f)
        elif os.path.isfile('/etc/nweb.json'):
            with open('/etc/nweb.json') as f:
                self.cfg = json.load(f)
        else:
            self.cfg = {}
    def env(self, name, default=None):
        self.__read_cfg();
        if name in self.cfg:
            return self.cfg[name]
        return os.getenv(name, default)

    def __contains__(self, item):
        return (self.cfg is not None and item in self.cfg) or self.hasFlag(item)
    def __getitem__(self, name):
        if isinstance(name, int):
            return self.argv[name]
        elif self.hasFlag(name):
            return self.getValue(name)
        else:
            return self.env(name)
    def __get__(self, i):
        return self.argv[i]
    def dispatch(self, **kwargs):
        arg = self.shift()
        if arg == sys.argv[0]:
            arg = self.shift()
        arg = arg.replace('-', '_')
        if arg in kwargs:
            kwargs[arg](self)
        else:
            print("Unknown Argument. " + arg)
            print("Valid Options: " + ", ".join(kwargs.keys()))
            if 'help' in kwargs:
                kwargs['help']()
    
def load_class(spec, create=False, args={}):
    """ spec = 'module:ClassName' """
    if args is None:
        args = {}
    if not isinstance(spec, str):
        return spec
    try:
        a = spec.split(':')
        m = importlib.import_module(a[0])
        c = getattr(m, a[1])
        if create:
            return c(**args)
        else:
            return c
    except ModuleNotFoundError as e:
        print("[nwebclient.util.load_class] ModuleNotFoundError Spec: " + str(spec), file=sys.stderr)
        print("[nwebclient.util.load_class] PWD: " + str(os.getcwd()), file=sys.stderr)
        raise e
       
def load_resource(module, filename):
    # https://stackoverflow.com/questions/6028000/how-to-read-a-static-file-from-inside-a-python-package
    import importlib.resources as pkg_resources
    #try:
    #    inp_file = (pkg_resources.files(module) / filename)
    #    with inp_file.open("rb") as f:  # or "rt" as text file with universal newlines
    #        return f.read()
    #except AttributeError:
    #    # Python < PY3.9, fall back to method deprecated in PY3.11.
    return pkg_resources.read_text(module, filename)

def exists_module(module_name):
    """
      itertools = importlib.import_module('itertools')
      import pkg_resources
      pkg_resources.get_distribution('requests').version
    """
    import importlib.util
    module_spec = importlib.util.find_spec(module_name)
    found = module_spec is not None
    return found

def download(url, filename, ssl_verify=True):
    import requests
    r = requests.get(url, stream=True, verify=ssl_verify) 
    if r.status_code == 200:
        with open(filename, 'wb') as f:
            for chunk in r:
                f.write(chunk)
                
def file_get_contents(filename):
    with open(filename, 'rb') as f:
        return f.read()

def file_get_lines(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return f.readlines()
    
def file_put_contents(filename, contents):
    if isinstance(contents, bytes):
        with open(filename, "wb") as f:
            f.write(contents)
    else:
        f = open(filename, "w")
        f.write(contents)
        f.close()

def load_json_file(filename):
    with open(filename, 'r') as f:
        return json.load(f)

def find_free_port():
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(('', 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]
