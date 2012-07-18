import lxml.html
import os
import sys
import cookielib
import re
from urlparse import urlparse
import uuid
import urllib2
import zipfile
import shutil

class WFFetcher(object):
    def __init__(self, url, html, local_store="/tmp/"):
        self.url = url
        self.html = html
        self.externalLinks = None
        self.local_store = local_store

    def _parseExternalLinks(self):
        tree = lxml.html.fromstring(self.html)
        if tree is None:
            return

        images = tree.xpath("//img | //IMG")
        for img in images:
            src = img.get('src')
            if src is None:
                continue

            urlparts = urlparse(src)
            filename = os.path.basename(urlparts.path)
            filename, ext = os.path.splitext(filename)
            new_filename = '{0}{1}'.format(uuid.uuid4(), ext)

            if self.externalLinks is None:
                self.externalLinks = []
            if src not in self.externalLinks:
                self.externalLinks.append({'src': src, 'store_file': new_filename, 'store_folder': 'images'})

            img.set('src', 'images/{0}'.format(new_filename))

        self.html = lxml.html.tostring(tree)

    def _fetchFile(self, url, local_path):
        jar = cookielib.CookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(jar))
        opener.addheaders = [('Referer', self.url)]
        if not re.match(".*t\.co/.+", url):
            opener.addheaders.append(('User-agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_4) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.52 Safari/536.5'))
        request = urllib2.Request(url.encode('utf-8'))
        page = opener.open(request)
        if page.getcode() == 200:
            ctype = page.headers['content-type']
            content = page.read()
            if ('Content-Encoding' in page.headers.keys() and page.headers['Content-Encoding'] == 'gzip') or \
               ('content-encoding' in page.headers.keys() and page.headers['content-encoding'] == 'gzip'):
                import gzip
                import cStringIO
                gz = gzip.GzipFile(fileobj=cStringIO.StringIO(content), mode='rb')
                content = gz.read()
                gz.close()

            fd = open(local_path, 'w')
            fd.write(content)
            fd.close()

            return local_path
        else:
            return None
            

    def _downloadExternalObjects(self, base_store):
        if self.externalLinks is None:
            return

        for extLink in self.externalLinks:
            src = extLink['src']
            store_file = extLink['store_file']
            store_folder = extLink['store_folder']
            folder_path = '{0}/{1}'.format(base_store, store_folder)
            if not os.access(folder_path, os.F_OK):
                os.mkdir(folder_path)

            local_file = '{0}/{1}'.format(folder_path, store_file)
            self._fetchFile(src, local_file)

    def _makeZip(self, zipfname, local_store):
        zipHandler = zipfile.ZipFile(zipfname, "w", compression=zipfile.ZIP_DEFLATED)
        
        cwd = os.getcwd()
        os.chdir(local_store)

        for root, folders, files in os.walk("./"):
            for each in files:
                aFile = os.path.join(root, each)
                zipHandler.write(aFile)
        zipHandler.close()

        os.chdir(cwd)

    def download(self):
        while True:
            new_store = '{0}/{1}'.format(self.local_store, uuid.uuid4())
            if os.access(new_store, os.F_OK):
                continue 
            os.mkdir(new_store)
            break
        
        self._parseExternalLinks()
        self._downloadExternalObjects(new_store)
    
        indexhtml = '{0}/index.html'.format(new_store)
        fd = open(indexhtml, 'w')
        fd.write(self.html)
        fd.close()

        zipfname = '{0}.zip'.format(new_store)
        self._makeZip(zipfname, new_store)

#        self._makeMHTML()
        shutil.rmtree(new_store)

