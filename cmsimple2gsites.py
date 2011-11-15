#!/usr/bin/env python -tt
# -*- coding: UTF-8 -*-
"""
Created on Mon Nov 14 21:17:30 2011

@author: Ulrik Landberg Stephansen <ulrikls@papio.dk>
"""

import argparse
import re
import getpass
import codecs
import HTMLParser
import gdata.gauth
import gdata.service
import gdata.sites.client
import gdata.sites.data


def main():
  """Main function."""

  # Define options
  parser = argparse.ArgumentParser(description = u'Import CMSimple HTML content to Google Sites.')
  parser.add_argument(u'username', help = u'User name (e-mail address).')
  parser.add_argument(u'site', help = u'Google Site name')
  parser.add_argument(u'file', type = file, help = u'CMSimple HTML content file')
  parser.add_argument(u'-p', u'--password', help = u'User password. If not provided user will be prompted.')
  parser.add_argument(u'-d', u'--domain', help = u'Google Apps domain')

  # Parse options
  options = parser.parse_args()
  if not options.password:
    options.password = getpass.getpass()
  options.file = codecs.open(options.file.name, r'rU', r'ISO-8859-1')

  # Authenticate
  if options.domain:
    client = gdata.sites.client.SitesClient(source='papio-cmsimple2gsites-v1', site=options.site, domain=options.domain)
    options.type = r'HOSTED'
  else:
    client = gdata.sites.client.SitesClient(source='papio-cmsimple2gsites-v1', site=options.site)
    options.type = r'HOSTED_OR_GOOGLE'

  try:
    client.ClientLogin(options.username, options.password, account_type = options.type, source = client.source)
  except gdata.service.CaptchaRequired:
    print u'Please visit ' + client.captcha_url
    answer = raw_input(u'Answer to the challenge? ')
    client.ClientLogin(options.usernam, options.password, account_type = options.type, source = client.source, captcha_token = client.captcha_token, captcha_response = answer)
  except gdata.service.BadAuthentication:
    exit(u'Users credentials were unrecognized')
  except gdata.service.Error:
    exit(u'Login Error')

  # Read file
  body = re.search(r'<body>(.*?)</body>', options.file.read(), re.DOTALL | re.IGNORECASE)
  entries = re.findall(r'<h([1-6])>(.*?)</h[1-6]>(.*)', body.group(1).strip(), re.IGNORECASE)
  h = HTMLParser.HTMLParser()

  # Import
  parents = {}
  for entry in entries:
    level = int(entry[0])
    title = h.unescape(re.sub(r'<.*?>', r'', entry[1].strip()))
    content = h.unescape(entry[2].strip())

    if level == 1:
      page = client.CreatePage('webpage', title, html=content)
      print u'%s' % title
    else:
      page = client.CreatePage('webpage', title, html=content, parent=parents[level - 1])
      print u'%s%s' % (u'\t'*(level-1), title)

    parents[level] = page





if __name__ == u'__main__':
  main()
