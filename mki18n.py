#!/usr/bin/python
from StringIO import StringIO
import urllib2, os, zipfile, pycurl

crowdin_project_api_key = ''

crowdin_project_identifier = 'electrum-client'
crowdin_file_name = 'electrum.po'
locale_file_name = 'locale/messages.pot'

if crowdin_project_api_key:
    # Generate fresh translation template
    if not os.path.exists('locale'):
      os.mkdir('locale')

    cmd = 'xgettext -s --no-wrap -f app.fil --output=locale/messages.pot'
    print 'Generate template'
    os.system(cmd)

    # Push to Crowdin
    print 'Push to Crowdin'
    url = ('http://api.crowdin.net/api/project/' + crowdin_project_identifier + '/update-file?key=' + crowdin_project_api_key)

    c = pycurl.Curl()
    c.setopt(c.URL, url)
    c.setopt(c.POST, 1)
    fields = [('files[' + crowdin_file_name + ']', (pycurl.FORM_FILE, locale_file_name))]
    c.setopt(c.HTTPPOST, fields)
    c.perform()

    # Build translations
    print 'Build translations'
    response = urllib2.urlopen('http://api.crowdin.net/api/project/' + crowdin_project_identifier + '/export?key=' + crowdin_project_api_key).read()
    print response

# Download & unzip
zfobj = zipfile.ZipFile(StringIO(urllib2.urlopen('http://crowdin.net/download/project/' + crowdin_project_identifier + '.zip').read()))

for name in zfobj.namelist():
    uncompressed = zfobj.read(name)
    if name.endswith('/'):
        if not os.path.exists(name):
            os.mkdir(name)
    else:
        print 'Saving',name
        output = open(name,'w')
        output.write(uncompressed)
        output.close()

# Convert .po to .mo
for lang in os.listdir('./locale'):
    if len(lang) != 2:
        continue

    # Check two-letter lang folder
    if not os.path.exists('locale/'+lang):
        os.mkdir('locale/'+lang)

    # Check LC_MESSAGES folder
    mo_dir = 'locale/%s/LC_MESSAGES' % lang
    if not os.path.exists(mo_dir):
        os.mkdir(mo_dir)
        
    cmd = 'msgfmt --output-file="%s/electrum.mo" "locale/%s/electrum.po"' % (mo_dir,lang)
    print 'Installing',lang
    os.system(cmd)
