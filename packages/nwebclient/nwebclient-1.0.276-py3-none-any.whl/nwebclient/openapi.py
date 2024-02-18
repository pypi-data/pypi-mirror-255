# pip install pyyaml requests
import yaml
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper
import requests

from nwebclient import util
from nwebclient import base as b
from nwebclient import web as w


def openapitype_to_sql(typename):
    res = 'VARCHAR(255)'
    # integer string
    if typename == 'integer':
        res = 'NUMBER(9)' # PostgreSQL NUMERIC
    return res


def openapitype_to_java(typename):
    res = 'String'
    # integer string
    if typename == 'integer':
        res = 'int'
    return res


def openapi_to_sql_col_name(name):
    return name


class OpenApi(b.Base):
    classes = []

    def __init__(self, yaml_text):
        if yaml_text is not None:
            self.data = yaml.load(yaml_text, Loader=Loader)
            objs = self.data['components']['schemas']
            for name in objs.keys():
                self.classes.append(ObjectDef(name, objs[name]))

    def __len__(self):
        return len(self.classes)

    def __iter__(self):
        return self.classes.__iter__()

    def to_mermaid(self, for_gitlab=False):
       res = ''
       if for_gitlab:
           res += '```mermaid\n'
       res +=  '---\n'
       res += 'title: Klassendiagramm\n'
       res += '---\n'
       res += 'classDiagram\n'
       for obj in self.classes:
           res += obj.to_mermaid()
       if for_gitlab:
           res += '```\n'
       return res

    def to_sql(self):
       res = ''
       for obj in self.classes:
           res += obj.to_sql() + '\n'
       return res

    def to_java(self):
       res = ''
       for obj in self.classes:
           res += obj.to_java() + '\n\n\n'
       return res

    def to_markdown(self):
        res = ''
        for obj in self.classes:
            res += obj.to_markdown() + '\n\n\n'
        return res


class ObjectDef(b.Base):

    def __init__(self, name, data):
        self.name = name
        self.data = data

    def sql_col_modifier(self, name, data, i):
        if name == 'id' or i == 0:
            return ' PRIMARY KEY'
        return ''

    def sql_col_def(self):
        cols = []
        i = 0
        for name in self.data['properties'].keys():
            sql_type = openapitype_to_sql(self.data['properties'][name]['type'])
            sql_modifier = self.sql_col_modifier(name, self.data['properties'][name], i)
            cols.append('   ' + openapi_to_sql_col_name(name) + ' ' + sql_type + sql_modifier)
            i += 1
        return ', \n'.join(cols)

    def sql_col_names(self):
        cols = []
        for name in self.data['properties'].keys():
            cols.append(openapi_to_sql_col_name(name))
        return cols


    def to_sql(self):
        res = 'CREATE TABLE ' + self.name + '(\n'
        res += self.sql_col_def()
        res += ');\n'
        return res

    def to_mermaid(self):
        res = '    class '+self.name+'\n'
        for name in self.data['properties'].keys():
            res += '    ' + self.name + ' : +' + name + ': ' + self.data['properties'][name]['type']
        return res

    def to_java(self):
        res = '\n\n'
        res += 'public class ' + self.name + ' {\n\n'
        for name in self.data['properties'].keys():
            res += '    private '+openapitype_to_java(self.data['properties'][name]['type'])+' '+name+';\n'
        for name in self.data['properties'].keys():
            uname = name[0].upper() + name[1:]
            tname = openapitype_to_java(self.data['properties'][name]['type'])
            res += '    public '+tname+' get'+uname+'() {\n'
            res += '        return '+name+';\n'
            res += '    }\n\n'
            res += '    public void set' + uname + '('+tname+' value) {\n'
            res += '        this.' + name + ' = value;\n'
            res += '    }\n\n'
        res = '\n}'
        return res

    def to_markdown(self):
        """
            | Col   |      Are      |  Cool |
            |----------|:-------------:|------:|
            | col 1 is |  left-aligned | $1600 |
            | col 2 is |    centered   |   $12 |
        """
        res =  '| Spalte | Datentyp | Beschreibung |\n'
        res += '|--------|----------|--------------|\n'
        for name in self.data['properties'].keys():
            cols = [
                name,
                self.data['properties'][name]['type'],
                self.data['properties'][name].get('description', '')]
            res += '| '+(' | '.join(cols))+' |\n'
        return res

    def to_python(self):
        res = 'class '+self.name+':\n'
        for name in self.data['properties'].keys():
            res += '    '+name+'\n'

def info_text():
    return "This tool generates documentation and source code from OpenAPI-YAML specifications."

def help():
    print(info_text())
    print('Usage: python -m nwebclient.openapi sql-create --url {url}')
    print('Usage: python -m nwebclient.openapi mermaid-create --url {url}')
    print('Usage: python -m nwebclient.openapi java-create --url {url}')
    print('Usage: python -m nwebclient.openapi markdown-create --url {url}')
    print('Usage: python -m nwebclient.openapi serv')


class WebApp(b.WebPage):
    """
     Für setup.py: 'nweb_web': ['openapi-tools = nwebclient.openapi:WebApp' ]

    """
    def __init__(self):
        super().__init__()
        self.name = 'openapi'
    def onOwnerChanged(self, newOnwer):
        pass

    def toHtml(self, params={}):
        p = b.Page()
        p.h1("OpenAPI Generator")
        p.div(info_text())
        if 'url' in params:
            text = requests.get(params['url']).text
            api = OpenApi(text)
            p.h2("SQL Create")
            p.pre(api.to_sql())
            p.h2("Markdown")
            p.pre(api.to_markdown())
        else:
            p('<form>')
            p.input('url')
            p.input('submit', value="SQL Erstellen", type='submit')
            p('</form>')
        return p.simple_page()


def serv(args):
    print("Starting Webserver")
    w.NwFlaskRoutes(childs=[WebApp()]).serv(args)


def main():
    help()
    args = util.Args()
    args.shift()
    text = None
    if args.hasName('url'):
        text = requests.get(args.getValue('url')).text
    api = OpenApi(text)
    args.dispatch(
        sql_create=lambda args: print(api.to_sql()),
        mermaid_create=lambda args: print(api.to_mermaid()),
        java_create=lambda args: print(api.to_java()),
        markdown_create=lambda args: print(api.to_markdown()),
        serv=serv
    )


if __name__ == '__main__':
    main()
