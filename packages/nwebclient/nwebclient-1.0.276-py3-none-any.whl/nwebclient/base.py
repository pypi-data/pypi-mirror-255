
import json
from urllib.parse import urlparse
from urllib.parse import parse_qs
from functools import wraps


class Base:
    """
        Basisklasse
    """
    __childs = []
    __owner = None
    def __init__(self):
        self.__childs = []
    def owner(self):
        return self.__owner
    def addChild(self, child):
        if child is None:
            return None
        child.__owner = self
        self.__childs.append(child)
        if isinstance(child, Base):
            child.onOwnerChanged(self)
        return child
    def onOwnerChanged(self, newOnwer):
        pass
    def childs(self):
        return self.__childs
    def isRoot(self):
        return self.__owner is None
    def getParents(self):
        res = []        
        current = self.__owner
        while not current is None:
            res.append(current)
            current = current.__owner
        return res
    def getRoot(self):     
        current = self
        while not current.__owner is None:
            current = current.__owner
        return current
    def getParentClass(self, cls):
        for p in self.getParents():
            if isinstance(p, cls):
                return p
        return None
    def onParentClass(self, cls, action):
        p = self.getParentClass(cls)
        if not p is None:
            return action(p)
        else:
            print("Parents: " + str(self.getParents()))
            return "Error: ParentClass not found."
    def className(self):
        a = self
        return "{0}.{1}".format(a.__class__.__module__, a.__class__.__name__)

    def prn(self, msg):
        print(msg)

    def debug(self, msg):
        self.prn("DEBUG: [{0}] {1}".format(self.__class__.__name__, str(msg)))
    def info(self, msg):
        self.prn("INFO: [{0}] {1}".format(self.__class__.__name__, str(msg)))
    def error(self, msg):
        self.prn("ERROR: [{0}] {1}".format(self.__class__.__name__, str(msg)))
    def one_line_str(self):
        res = self.className()
        res = res + ' ' + str(getattr(self, 'name', ''))
        return res
    def printTree(self, indent=1, p = print):
        if indent > 10:
            return
        try:
            p(' '.rjust(indent*2, ' ') + self.one_line_str())
            for c in self.__childs:
                if isinstance(c, Base):
                    c.printTree(indent+1, p=p)
                else:
                    p(' '.rjust((indent+1)*2, ' ') + str(type(c)))
        except RecursionError:
            pass
    def getHtmlTree(self):
        s = '<pre class="Base getHtmlTree">'
        p = StrBuffer()
        self.printTree(p=p)
        s = s + str(p) + '</pre>'
        return s
    def hasName(self, name):
        return self.getChildByName(name) is not None
    def getChildByName(self, name):
        for c in self.childs():
            if getattr(c, 'name', None) == name:
                return c
        return None
    def findChild(self, **kwargs):
        for c in self.__childs:
            eq = True
            for k in kwargs.keys():
                if not getattr(c, k, None) == kwargs[k]:
                    eq = False
            if eq:
                return c
        return None
    def findChilds(self, **kwargs):
        res = []
        for c in self.__childs:
            eq = True
            for k in kwargs.keys():
                if not getattr(c, k, None) == kwargs[k]:
                    eq = False
            if eq:
                res.append(c)
        return res
    def getOrCreateChild(self, cls, search_dict, args):
        child = self.findChild(**search_dict)
        if child is None:
            child = self.addChild(cls(*args))
        return child

    
class Named:
    def getName(self):
        return self.name
    
    
class StrBuffer:
    s = ''
    line_break = "\n"
    def __init__(self, s=''):
        self.s = s
    def __call__(self, msg):
        self.s = self.s + str(msg) + self.line_break
    def __str__(self):
        return str(self.s)
    def toString(self):
        return self.s
    

class Plugins():
    """
       Add Plugins.register('nweb_web', 'mymodule.WebClass')
    """
    PLUGINS = {}
    points = []
    def __init__(self, group):
        from importlib.metadata import entry_points
        points = list(filter(lambda e: e[0].group == group, entry_points().values()))
        if len(points) > 0:
            self.points = points[0]
        if group in Plugins.PLUGINS:
            self.points.extend(Plugins.PLUGINS.get(group, []))

    @classmethod
    def register(cls, name, endpoint):
        if name in cls.PLUGINS:
            cls.PLUGINS[name].append(endpoint)
        else:
            cls.PLUGINS[name] = [endpoint]

    def __iter__(self):
        return iter(self.points)

    def __getitem__(self, name):
        """
          Return e.g. "module.submodule:ClassOrFunction"
        """
        for p in self:
            if p.name == name:
                return p
        return None
  

class Params:
    data = {}
    orginal = None
    def __init__(self, data):
        if isinstance(data, str):
            self.orginal =  data
            if len(data)>0:
                if data[0]=='?':
                    data = data[1:]
                self.data= self.parseQuery('http://domain.end'+data)
            else:
                self.data = {}
        else:
            self.data = data
    def parseQuery(self, url):
        res = {}
        parsed_url = urlparse(url)
        q = parse_qs(parsed_url.query)
        for k in q.keys():
            res[k] = q[k][0]
        return res
    def __contains__(self, element):
        return element in self.data
    def __getitem__(self, name):
        return self.data[name]
    def __str__(self):
        return str(self.orginal)
    def filterKeys(self, key_list):
        res = {}
        for k in key_list:
            if k in self.data:
                res[k] = self.data[k]
        return res
    
class Page(StrBuffer, Base):
    __style = ''
    __vars = {}
    def __init__(self, s='', owner=None):
        super().__init__(s)
        self.__style = ''
        self.__vars = {}
        if owner is not None:
            jsf = getattr(owner, 'js', None)
            if callable(jsf):
                self.script(jsf())
    def __iadd__(self, other):
        self(other)
        return self
    def __getitem__(self, name):
        return self.__vars[name]
    def __setitem__(self, name, value):
        self.__vars[name] = value
    def tag(self, tag_name, content='', **kw):
        a = ''
        if '_class' in kw:
            kw['class'] = kw['_class']
            kw.pop('_class', None)
        for k in kw.keys():
            a += ' ' + k + '="' + str(kw[k]) + '"'
        self('<'+tag_name+a+'>'+str(content)+'</'+tag_name+'>')
        return self
    def hr(self):
        self('<hr />')
        return self
    def ul(self, items):
        s = '<ul>'
        for item in items:
            s += '<li>'+str(item)+'</li>'
        self(s + '</ul>')
        return self
    def input(self, name, **attrs):
        attrs['name'] = name
        return self.tag('input', '', **attrs)
    def h1(self, text, **attrs):
        return self.tag('h1', text, **attrs)
    def h2(self, text, **attrs):
        return self.tag('h2', text, **attrs)
    def h3(self, text, **attrs):
        return self.tag('h3', text, **attrs)
    def p(self, text):
        return self.tag('p', text)
    def div(self, text='', **attr):
        return self.tag('div', text, **attr)
    def right(self, text='', **attr):
        attr['style'] = 'text-align: right;'
        return self.tag('div', text, **attr)
    def span(self, text):
        return self.tag('span', text)
    def ul(self, items):
        return self.tag('ul', "\n".join(map(lambda x: '<li>'+str(x)+'</li>', items)))
    def pre(self, text):
        return self.tag('pre', text)
    def script(self, js):
        if js is None:
            return self
        return self.tag('script', js)
    def js_ready(self, js):
        return self.script('document.addEventListener("DOMContentLoaded", function() { '+js+' }, false);')
    def style(self, s):
        if not s is None:
            self.__style += s
        return self
    def a(self, content, url):
        return self.tag('a', content, **{'href': url})
    def load(self, obj):
        self.style(call_method(obj, 'style'))
        self.script(call_method(obj, 'script'))
        fn = getattr(obj, 'jsvars', None)
        if callable(fn):
            self.script('window.py = ' + json.dumps(fn())+';')
        return self
    def simple_page(self):
        return """
        <html>
          <head>
            <style>
              body, div { font-family: sans-serif;}
              div.main {
                margin: auto;
                width: 800px;
              }
              """+self.__style+"""
            </style>
            <title>"""+self.__vars.get('title', '')+"""</title>
            """+self.__vars.get('meta', '')+"""
          </head>
          <body>
            <header>"""+self.__vars.get('header', '')+"""</header>
            <div class="main">"""+str(self)+"""</div>
            <footer>"""+self.__vars.get('footer', '')+"""</footer>
          </body>
        </html>
        """
    
    
def action(title=None):
    def actual_decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        func.__action=True
        return wrapper
    return actual_decorator

def style():
    def actual_decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper
    return actual_decorator

def script():
    def actual_decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper
    return actual_decorator


def get_decorators(cls):
    """ {func1: [decorator1, decorator2]}  """
    import ast
    import inspect
    decorators = {}

    def visit_FunctionDef(node):
        decorators[node.name] = []
        for n in node.decorator_list:
            name = ''
            if isinstance(n, ast.Call):
                name = n.func.attr if isinstance(n.func, ast.Attribute) else n.func.id
            else:
                name = n.attr if isinstance(n, ast.Attribute) else n.id

            decorators[node.name].append(name)

    node_iter = ast.NodeVisitor()
    node_iter.visit_FunctionDef = visit_FunctionDef
    try:
        node_iter.visit(ast.parse(inspect.getsource(cls)))
    except TypeError:
        print("Error: getsource not on built-in or just in time compiled classes")
    return decorators


def get_with_decorator(cls,  decorator_name):
    """ {func1: {params}, func2: {params}}  """
    import ast
    import inspect
    methods = {}

    def visit_FunctionDef(node):
        names = []
        for n in node.decorator_list:
            name = ''
            named_args = {'method': node.name}
            # print(ast.dump(node))
            if isinstance(n, ast.Call):
                name = n.func.attr if isinstance(n.func, ast.Attribute) else n.func.id
                for k in n.keywords:
                    named_args[k.arg] = k.value.value
            else:
                name = n.attr if isinstance(n, ast.Attribute) else n.id
            if name == decorator_name:
                methods[node.name] = named_args
            

    node_iter = ast.NodeVisitor()
    node_iter.visit_FunctionDef = visit_FunctionDef
    node_iter.visit(ast.parse(inspect.getsource(cls)))
    return methods

def call_method(obj, func, *args, **kwargs):
    fn = getattr(obj, func, None)
    if callable(fn):
        return fn(*args, **kwargs)
    return None

class WebPage:
    def page(self, params={}):
        fn = getattr(self, 'toHtml', None)
        if fn is not None:
            return fn(params)
        else:
            return "WebPage"

class WebObject(Base, WebPage):
    def __init__(self, obj, params={}):
        Base.__init__(self)
        self.obj = obj
        self.params = params
        self.addChild(self.obj)
    def solveObject(self, obj):
        import ctypes
        if isinstance(obj, int):
            obj = ctypes.cast(obj, ctypes.py_object).value
        return obj
    def __repr__(self):
        return "WebObject({0})".format(self.obj.__repr__())
    def __str__(self):
        return "WebObject({0})".format(self.obj.__str__())
    def html(self):
        p = Page()
        p.h1("WebObject")
        actions = get_with_decorator(self.obj, 'actions')
        return p.simple_page()
    def toHtml(self, params={}):
        to_html = getattr(self.obj, 'toHtml', None)
        if to_html is None:
            return self.html()
        return self.obj.toHtml(params)
    def page(self, params={}):
        return self.toHtml(params)
    

class WebInfo(Base, Named):
    name = 'nwebclient-info'
    def __init__(self):
        super().__init__();
    def toHtml(self, params={}):
        from importlib.metadata import version 
        p = Page()
        p('<h1>Info</h1>nwebclient ' + str(version('nwebclient')))
        return p.simple_page()

