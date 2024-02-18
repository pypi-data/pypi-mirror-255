
from nwebclient import util
from nwebclient import base as b
import base64
import uuid

def tag(tag_name, content, **kw):
    a = ''
    if '_class' in kw:
        kw['class'] = kw['_class']
        kw.pop('_class', None)
    for k in kw.keys():
        a += ' ' + k + '="' + str(kw[k]) + '"'
    return '<'+tag_name+a+'>'+content+'</'+tag_name+'>'

def a(content, href):
    if isinstance(href, str):
        return tag('a', content, href=href)
    else:
        return tag('a', content, **href)
    
def pre(content, **kw):
    return tag('pre', content, **kw)

def div(content, **kw):
    return tag('div', content, **kw)

def input(name, **attrs):
    attrs['name'] = name
    return tag('input', '', **attrs)

def js_ready(js):
    return 'document.addEventListener("DOMContentLoaded", function() { '+js+' }, false);';

def js_fn(name, args, code=[]):
    return 'function '+name+'('+','.join(args)+') {\n'+'\n'.join(code)+'\n}\n\n'
def js_add_event_for_id(id, event_js):
    return 'document.getElementById("'+id+'").addEventListener("click", function(e) {\n '+event_js+' \n});\n'
def button_js(title, js_action):
    id = 'btn' + str(uuid.uuid4()).replace('-','')
    js = js_ready(js_add_event_for_id(id, js_action))
    res = '<button id="'+id+'">'+str(title)+'</button><script type="text/javascript">'+js+'</script>'
    return res


def route_root(web, root):
    web.add_url_rule('/pysys/root', 'r_root', view_func=lambda: root.getHtmlTree())
    res = NwFlaskRoutes()
    res.addTo(web)
    return res


class WebRoute(b.Base, b.WebPage):
    def __init__(self, route, name, func):
        self.route = route
        self.name = name
        self.func = func
    def page(self, params={}):
        return self.func()

class NwFlaskRoutes(b.Base):

    def __init__(self, childs=[]):
        super().__init__()
        for child in childs:
            self.addChild(child)

    def requestParams(self):
        from flask import request
        data = {}
        for tupel in request.files.items():
            name = tupel[0]
            f = tupel[1]
            #print(str(f))
            data[name] = base64.b64encode(f.read()).decode('ascii')
        params = {
            **request.cookies.to_dict(),
            **request.args.to_dict(), 
            **request.form.to_dict(),
            **data,
            **{'request_url': request.url}}
        return params
    def addTo(self, app):
        self.web = app
        app.add_url_rule('/nw/<path:p>', 'nw', lambda p: self.nw(p), methods=['GET', 'POST'])
        app.add_url_rule('/nws/', 'nws', self.nws)
    def nws(self):
        p = b.Page().h1("Module")
        for e in b.Plugins('nweb_web'):
            p.div('<a href="{0}" title="Plugin">{1}</a>'.format('/nw/'+e.name, e.name))
        for e in self.childs():
            p.div('<a href="{0}" title="Object">{1}</a>'.format('/nw/' + e.name, e.name))
        return p.simple_page()

    def add_url_rule(self, route, name, view_func):
        print("Route" + route + " via add_url_rule")
        self.addChild(WebRoute(route, name, view_func))

    def load_flask_blueprints(self, app):
        for e in b.Plugins('flask_blueprints'):
            blueprint = util.load_class(e)
            app.register_blueprint(blueprint)


    def nw(self, path):
        params = self.requestParams()
        n = path.split('/')[0]
        if self.hasName(n):
            return self.getChildByName(n).page(params)
        plugin = b.Plugins('nweb_web')[n]
        if plugin is not None:
            obj = util.load_class(plugin.value, create=True)
            w = self.addChild(b.WebObject(obj, {**{'path': path}, **params}))
            w.name = n
            return w.page(params)
        else:
            return "Error: 404 (NwFlaskRoutes)"

    def serv(self, args = {}):
        from flask import Flask, request
        app = Flask(__name__)
        # @app.route('/')
        self.addTo(app)
        app.run(host='0.0.0.0', port=8080)
