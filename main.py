#!/usr/bin/env python

import logging
import wsgiref.handlers

from re import compile
from cgi import escape
from urllib import urlencode
from django.utils import simplejson
from xml.dom.minidom import parseString

from google.appengine.ext import webapp
from google.appengine.api import urlfetch
from google.appengine.api import memcache

class MainHandler(webapp.RequestHandler):
  def get(self):
#    for debugging
#    memcache.flush_all()
    
    if self.request.query_string:
      
      amount = escape(self.request.get('amount'))
      what = escape(self.request.get('what'))
      start = escape(self.request.get('start'))
      lang = escape(self.request.get('lang'))
      callback = escape(self.request.get('callback'))
      
      if not amount: amount = 5
      if not what: what = 'paras'
      start = 'yes' if not start or start == 1 else 'no'
      if not lang or lang == 'www': lang = 'en'
      
      key = str(amount)+'.'+what+'.'+str(start)+'.'+lang
      logging.info(key)
      
      json = memcache.get(key)
      
      if json is None:
        params = {
          'amount': amount,
          'what': what,
          'start': start
        }
        
        query = urlencode(params);
        url = 'http://'+lang+'.lipsum.com/feed/xml?'+query
        logging.info(url)
        
        obj = {}
        error = 0
        
        try:
          result = urlfetch.fetch(url)
          if result.status_code == 200:
            dom = parseString(result.content)
            lipsum = dom.getElementsByTagName('lipsum')[0].firstChild.data
            whatexp = compile('^paras|lists$')
            whatmatch = whatexp.match(what)
            if whatmatch: lipsum = lipsum.split('\n')
            
            obj['lipsum'] = lipsum
            obj['generated'] = dom.getElementsByTagName('generated')[0].firstChild.data
            
        except urlfetch.Error:
          logging.error('urlfetch error')
          obj['error'] = True
          error = 1
      
        json = simplejson.dumps(obj, sort_keys=True, indent=4, ensure_ascii=False)
        
        if not error:
          logging.debug('Adding json output to memcache')
          memcache.add(key, json)
      else:
        logging.info('The key is in memcache')
      
      if callback:
        logging.info('Adding callback to JSON')
        exp = compile('^[A-Za-z_$][A-Za-z0-9_$]*?$')
        match = exp.match(callback)
        if match: json = callback + '(' + json + ')'
      
      self.response.headers['Content-Type'] = 'application/javascript; charset=utf-8'
      self.response.out.write(json)

    else:
      self.response.out.write("""
      <!DOCTYPE html>
      <title>json-lipsum</title>
      <style>
      var{font-weight: bold; font-style: normal;}
      dt{display: list-item;}
      dl{margin-left: 40px;}
      </style>
      <h1>json-lipsum</h1>
      <p>JSON (and JSON-P) API for generating Lorem Ipsum text.</p>
      <ul>
      <li><a href="/?amount=5">/?amount=5</a></li>
      <li><a href="/?amount=40&amp;what=words&amp;start=no">/?amount=40&amp;what=words&amp;start=no</a></li>
      <li><a href="/?amount=10&amp;lang=fr&amp;callback=foo">/?amount=10&amp;lang=fr&amp;callback=foo</a></li>
      </ul>
      <p>The parameters:</p>
      <dl>
      <dt><var>amount</var></dt>
        <dd>Indicates the amount of output. Default is 5.</dd>
      <dt><var>what</var></dt>
        <dd>Indicates the type of output. Note that 'paras' and 'lists' returns an array.
          <ul>
          <li>paras &larr; Paragraphs <em>(default)</em></li>
          <li>words</li>
          <li>bytes</li>
          <li>lists</li>
          </ul>
        </dd>
      <dt><var>start</var></dt>
        <dd>Indicates the output to start with 'Lorem Ipsum dolor sit amet...'.
          <ul>
          <li>yes<em>(default)</em></li>
          <li>no</li>
          </ul>
        </dd>
      <dt><var>lang</var></dt>
        <dd>Indicates the language of the output.
          <ul>
          <li>sq &larr; Shqip</li>
          <li>bg &larr; &#1041;&#1098;&#1083;&#1075;&#1072;&#1088;&#1089;&#1082;&#1080;</li>
          <li>ca &larr; Catal&agrave;</li>
          <li>hr &larr; Hrvatski</li>
          <li>cs &larr; &#268;esky</li>
          <li>da &larr; Dansk</li>
          <li>nl &larr; Nederlands</li>
          <li>en OR www &larr; English <em>(default)</em></li>
          <li>et &larr; Eesti</li>
          <li>fr &larr; Fran&ccedil;ais</li>
          <li>ka &larr; &#4325;&#4304;&#4320;&#4311;&#4323;&#4314;&#4312;</li>
          <li>de &larr; Deutsch</li>
          <li>el &larr; &#917;&#955;&#955;&#951;&#957;&#953;&#954;&#940;</li>
          <li>he &larr; &#8235;&#1506;&#1489;&#1512;&#1497;&#1514;</li>
          <li>hu &larr; Magyar</li>
          <li>id &larr; Indonesia</li>
          <li>it &larr; Italiano</li>
          <li>mk &larr; &#1084;&#1072;&#1082;&#1077;&#1076;&#1086;&#1085;&#1089;&#1082;&#1080;</li>
          <li>ms &larr; Melayu</li>
          <li>no &larr; Norsk</li>
          <li>pl &larr; Polski</li>
          <li>pt &larr; Portugu&ecirc;s</li>
          <li>ro &larr; Rom&acirc;na</li>
          <li>ru &larr; Pycc&#1082;&#1080;&#1081;</li>
          <li>sr &larr; &#1057;&#1088;&#1087;&#1089;&#1082;&#1080;</li>
          <li>sk &larr; Sloven&#269;ina</li>
          <li>sl &larr; Sloven&#353;&#269;ina</li>
          <li>es &larr; Espa&ntilde;ol</li>
          <li>sv &larr; Svenska</li>
          <li>tr &larr; T&uuml;rk&ccedil;e</li>
          <li>uk &larr; &#1059;&#1082;&#1088;&#1072;&#1111;&#1085;&#1089;&#1100;&#1082;&#1072;</li>
          <li>vi &larr; Ti&#7871;ng Vi&#7879;t</li>
          </ul>
        </dd>
      <dt><var>callback</var></dt>
        <dd>The callback function for JSON-P.</dd>
      </dl>
      <p>Powered by <a href="http://lipsum.com/">Lipsum.com</a>. <a href="http://json-lipsum.googlecode.com/">Google Code</a></p>
      """)

def main():
  application = webapp.WSGIApplication([('/', MainHandler)],
                                       debug=True)
  wsgiref.handlers.CGIHandler().run(application)

if __name__ == '__main__':
  main()
