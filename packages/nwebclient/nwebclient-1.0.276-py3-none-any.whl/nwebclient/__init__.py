import requests
import json
import urllib.parse
import sys
import os
import os.path
import traceback

from nwebclient import util

#import .sdb as sdb

name = "nwebclient"

class NWebGroup:
    __client = None
    __data = None
    def __init__(self, client, data):
        self.__client = client
        self.__data = data
    def guid():
        return self.__data['guid']
    def title():
        return self.__data['title']
    def println(self):
        for key, value in self.__data.iteritems():
            print(key + ": " + value)
    def asDict(self):
        return self.__data;
    def docs(self):
        """
        :rtype: [NWebDoc]
        """
        contents = self.__client.req('api/documents/' + str(self.__data['group_id']))
        j =json.loads(contents);
        items = j['items'];
        #return j.items;
        return map(lambda x: NWebDoc(self.__client, x), items)

    def contains_name(self, name):
        for d in self.docs():
            if d.name() == name:
                return True;
        return False

    def doc_by_name(self, name):
        for d in self.docs():
            if d.name() == name:
                return d;
        return None

class NWebDoc:
    __client = None
    __data = None
    def __init__(self, client, data):
        self.__client = client
        self.__data = data
        if self.__client.verbose:
            print("Doc created.")
    def __repr__(self):
        name = self.__data['name']
        return f'<Doc {self.id()} Name: {name}>'
    def __str__(self):
        return self.__repr__()
    def title(self):
        return self.__data['title']
    def name(self):
        return self.__data['name']
    def kind(self):
        return self.__data['kind']
    def content(self):
        return self.__data['content']
    def guid(self):
        return self.__data['guid']
    def is_image(self):
        return self.__data['kind'] == 'image'
    def printInfo(self):
        s = "Doc-"+self.kind()+"(id:"+self.id()+", title: "+self.title()
        if (self.kind()=="image"):
            s+=" thumb: " + self.__data['thumbnail']['nn'] + " "
        s+=")"
        print(s)
    def id(self):
        return self.__data['document_id']
    def tags(self):
        return self.__data['tags']
    def println(self):
        print(self.__data)
        #for key, value in self.__data.iteritems():
        #    print key + ": " + value
    def downloadThumbnail(self, file, size = 'nn'):
        # TODO imple   
        path = 'image/'+str(self.id())+'/thumbnail/'+size+'/'+str(self.id())+'.jpg'
        self.__client.reqToFile(path, file)
        return 0
    def save(self, file):
        self.__client.reqToFile('/w/d/'+str(self.id())+'/download', file)
    def setContent(self, content):
        self.__data['content'] = content
        self.__client.req('api/document/'+self.__data['document_id'], {
            'action': 'update',
            'content': content
        })
    def setMetaValue(self, ns, name, value):
        data = {'ns': ns, 'name':name, 'value':str(value)}
        #print("DATA: " + str(data))
        return self.__client.req('w/api/doc/'+str(self.__data['document_id'])+'/meta', data)
    def getMeta(self):
        json.loads(self.__client.reqGet('w/api/doc/'+self.__data['document_id']+'/meta'))
    def to_dict(self):
        return {
            'document_id': self.id(),
            'guid': self.guid(),
            'name': self.name(),
            'title': self.title()
        }
        
class NWebClient:
    
    __url = "" 
    __user = ""
    __pass = ""
    __cfg = {}
    __last_url = '{none}'
    ssl_verify = False
    verbose = False
    def __init__(self, url=None, username = '', password = ''):
        """
          Anstatt url kann auch ein Pfad zur einer JSON-Datei, die die Schluessel enthaelt, angegeben werden. 
          url https://bsnx.net/4.0/
        """
        if url is None:
            if os.path.isfile('nweb.json'):
                url = 'nweb.json'
            elif os.path.isfile('/etc/nweb.json'):
                url = '/etc/nweb.json'
            elif os.getenv('NWEB_URL') is not None and os.getenv('NWEB_USER') is not None and os.getenv('NWEB_PASS') is not None:
                url = os.getenv('NWEB_URL')
                username = os.getenv('NWEB_USER')
                password = os.getenv('NWEB_PASS')
        if url[0] == '/' or url.endswith('nweb.json'):
            self.__cfg = json.loads(self.file_get_contents(url))
            self.__url = self.__cfg['url']
            self.__user = self.__cfg['username']
            self.__pass = self.__cfg['password']
        else:
            self.__url = url
            self.__user = username
            self.__pass = password
    def __call__(self, q):
        return "NWebClient TODO"
    def __getitem__(self, key):
        if key in self.__cfg:
            return self.__cfg[key]
        else:
            return "Non Existing"
    def __repr__(self):
        return f'<NWebClient {self.__url} User: {self.__user} docs() >'
    def v(self, msg):
        if self.verbose:
            print("[NWebClient]" + str(msg))
    def file_get_contents(self, filename):
        with open(filename) as f:
            return f.read()
    def _appendGet(self, url, name, value):
        v = name + '=' + urllib.parse.quote(value)
        if '?' in url:
            return url + '&' + v
        else:
            return url + '?' + v
    def reqToFile(self, path, name):
        url = self.__url + path
        url = self._appendGet(url, 'username', self.__user)
        url = self._appendGet(url, 'password', self.__pass)
        r = requests.get(url, stream=True, verify=self.ssl_verify) 
        if r.status_code == 200:
            with open(name, 'wb') as f:
                for chunk in r:
                    f.write(chunk)
    def reqGet(self, path, params = {}):
        if self.__user != "":
            params["username"]= self.__user
            params["password"]= self.__pass
        url = self.__url+path
        self.v("GET " + url);
        res = requests.get(url, data=params, verify=self.ssl_verify)
        return res.text
    def req(self, path, params = {}):
        if self.__user != "":
            params["username"]= self.__user
            params["password"]= self.__pass
        url = self.__url+path
        self.__last_url = url
        self.v("POST " + url);
        res = requests.post(url, data=params, verify=self.ssl_verify)
        return res.text
    def upload(self, path, params={}, name='file', data=None):
        """ open('file.txt','rb') """
        url = self.__url+path
        if self.__user != "":
            params["username"]= self.__user
            params["password"]= self.__pass
        files = {name: data}
        self.v("UPLOAD " + url)
        r = requests.post(url, files=files, data=params)
        return r.text
    def doc(self, id):
        response = self.req("api/document/"+str(id), {format:"json"})
        #print(response)
        data = json.loads(response);
        return NWebDoc(self, data)
    def docs(self, q = ''):
        """ 
          Syntax: q 
          API: w/api/docs
        
        """
        ja = self.req('w/api/docs?'+q);
        try:
            items = json.loads(ja)
            return list(map(lambda x: NWebDoc(self, x), items))
        except Exception as error:
            print("URL: " + self.__last_url)
            print("Response:")
            print(ja)
            raise
    def group(self, id): 
        data = json.loads(self.req("api/group/"+id, {format:"json"}))
        return NWebGroup(self, data)
    def getOrCreateGroup(self, guid, title):
        return "TODO"
    def getOrCreateDoc(self, group_id, name):
        g = self.group(group_id)
        if g.contains_name(name):
            return g.doc_by_name(name)
        else:
            return self.createDoc(name, '', group_id)
    def createDoc(self, name, content, group_id, kind='markup', **data):
        """ Return: JSON """
        res = self.req("w/group/"+str(group_id)+"/create", {
            "title": name,
            "content": content,
            "kind": kind,
            "response": "json",
            "guid": data.get('guid', '')
        })
        print(res)
        j = json.loads(res)
        if 'document_id' in j:
            return self.doc(j['document_id'])
        else:
            print("Fail to Create Doc. " + res)
            return None
    def createFileDoc(self, name, group_id, data):
        """  open('file', 'rb') """
        res = self.upload("w/group/"+str(group_id)+"/create", {
            "title": name,
            "kind": 'binary',
            "response": "json"
        }, 'file', data)
        j = json.loads(res)
        return self.doc(j['document_id'])
    def deleteDoc(self, id):
        return self.req('w/d/'+str(id)+'/delete', {'confirm': 1})
    def downloadImages(self, limit=1000, tag=None, size=None):
        # https://bsnx.net/4.0/w/api/docs?tag=Untertage
        q = 'kind=image&limit='+str(limit)
        if not tag is None:
            q = q + "&tag=" + str(tag)
        docs = self.docs(q)
        for doc in docs:
            if size is None:
                self.reqToFile('image/'+str(doc.id())+'/orginal/web/'+str(doc.id())+'.jpg', str(doc.id())+ '.jpg')
            else:
                self.reqToFile('image/'+str(doc.id())+'/thumbnail/'+size+'/t.jpg', str(doc.id())+ '.jpg')
            print("Download Image: " + str(doc.id()))
    def downloadImageDataset(self, tags=[], limit=500):
        for tag in tags:
            print("Processing Tag: " + str(tag))
            folder = tag.replace(' ', '_')
            os.mkdir(folder)
            os.chdir(folder)
            self.downloadImages(limit=limit, tag=tag, size='cs')
            os.chdir('..')
        print("Done.");
    def imagesUrls(self, tag=None, limit=1000, size='cs', file=None):
        """ Erstellt eine Liste mit Image-URLs """
        res = []
        q = 'kind=image&limit='+str(limit)
        if not tag is None:
            q = q + "&tag=" + str(tag)
        docs = self.docs(q)
        for doc in docs:
            url = self.__url + 'image/'+str(doc.id())+'/thumbnail/'+size+'/'+str(doc.id())+'/t.jpg'
            url = url + '?username=' + self.__user + "&password=" + self.__pass
            res.append(url)
        if not file is None:
            with open(file, "w") as f:
                for item in res:
                    f.write("%s\n" % item)
        return res
    def mapDocMeta(self, meta_ns, meta_name, filterArgs='kind=image', limit=1000, update=True, mapFunction=None):
        meta = meta_ns + '.' + meta_name
        structure = {}
        q = 'no_meta='+meta+'&'+'limit='+str(limit)+'&'+filterArgs
        docs = self.docs(q)
        i = 0
        for doc in docs:
            print("Processing: " + str(doc) + "   i:" + str(i))
            try:
                result = mapFunction(doc, self)
                if update:
                    print(doc.setMetaValue(meta_ns, meta_name, result))
                print("Value: " + str(result))
                structure[doc.guid()] = {
                  meta_ns+'.'+meta_name: result
                }
            except Exception as e:
                print("[NWebClient] Error: " + str(e))
                print(traceback.format_exc());
            i = i + 1
        print("Count: "+str(i))    
        print("Done.")
        return structure

def metric_val(baseUrl, metricName, val):
    """ baseUrl: string = e.g. https://bsnx.net/metric-endpoint """
    requests.get(url=baseUrl, params= {'metric':metricName, 'val':val})
    
def download(url, filename, ssl_verify=True):
    r = requests.get(url, stream=True, verify=ssl_verify) 
    if r.status_code == 200:
        with open(filename, 'wb') as f:
            for chunk in r:
                f.write(chunk)


def main():
    print("nx-c")
    c = NWebClient(None)
    args = util.Args()
    print(sys.argv)
    print(str(c.docs()))

if __name__ == '__main__': # nx-c vom python-package bereitgestellt
    main()