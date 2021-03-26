import xbmc, xbmcgui, xbmcplugin, xbmcaddon
import urllib.request
import urllib.parse
import sys, os, os.path
import json, re
import ntpath
from html.parser import HTMLParser

from common import addon_log, addon, Downloader, cleanJson, message

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Encoding': 'identity',
    'Accept-Language': 'en-US,en;q=0.5', 
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0'
  }
opener = urllib.request.build_opener()

def listCurrent():
  url = 'http://www.eteatru.ro/play.htm'
  request = urllib.request.Request(url, None, headers)
  response = opener.open(request)
  playInfoTxt = response.read()
  playInfoTxt =  playInfoTxt.decode('iso-8859-2')
  playInfoTxt = cleanJson(playInfoTxt)
  addon_log(playInfoTxt)
    
  try:
    playInfo = json.loads(playInfoTxt, encoding='iso-8859-2')
    name = playInfo[0][1]
    pars = HTMLParser()
    name = pars.unescape(name)
    name = name.encode('utf8')
    comment = playInfo[0][2]
    comment = pars.unescape(comment)
    tag_re = re.compile(r'(<!--.*?-->|<[^>]*>)')
    comment = tag_re.sub('', comment)
    #comment = re.sub('<[^<]+?>', '', comment)
    comment = comment.encode('utf8')
    url = playInfo[0][3]
    # offset = playInfo[0][6]
  except Exception as inst:
    addon_log(inst)
    return False
  addItem(url, name, comment)
  
def addItem(url, name, comment):
  plugin=sys.argv[0]
  listitem = xbmcgui.ListItem(name)
  listitem.setArt({'icon': "DefaultAudio.png"})
  #listitem.setInfo('music', {'Title': name, 'Comment':comment})
  listitem.setInfo( type="video", infoLabels={ "title": name, 'plot':comment })
  u=plugin+"?mode=2"+\
           "&url="+urllib.parse.quote_plus(url)+\
           '&title='+urllib.parse.quote_plus(name)+\
           '&comment='+urllib.parse.quote_plus(comment)
  contextMenuItems = [( addon.getLocalizedString(30010), "RunPlugin("+u+")", )]
  listitem.addContextMenuItems(contextMenuItems)
  
  xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=listitem,isFolder=False)
  
def addDir(name, mode, params=None, descr="", img=None):
  plugin=sys.argv[0]

  u = plugin+"?"+"mode="+str(mode)
  if(params!=None):
    for param in params:
      u = u + '&' + param['name'] + '=' + param['value']  
    
  if(img == None):
    img = "DefaultFolder.png"
  liz = xbmcgui.ListItem(name)
  liz.setArt({'icon': img})
  liz.setInfo( type="video", infoLabels={ "title": name, 'plot':descr })
  xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)

def catList():
  addDir(addon.getLocalizedString(30005), 1)
  addDir(addon.getLocalizedString(30006), 3)
  
  #Downloads
  if(addon.getSetting('download_path')!=''):
    liz = xbmcgui.ListItem(addon.getLocalizedString(30008))
    liz.setArt({'icon': "DefaultFolder.png"})
    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=addon.getSetting('download_path'), listitem=liz, isFolder=True)
    
  addDir(addon.getLocalizedString(30011), 5)
    
  xbmc.executebuiltin("Container.SetViewMode(51)")

def getParams():
  param=[]

  paramstring=sys.argv[2]

  if len(paramstring)>=2:
    params=sys.argv[2]
    cleanedparams=params.replace('?','')
    if (params[len(params)-1]=='/'):
      params=params[0:len(params)-2]
    pairsofparams=cleanedparams.split('&')
    param={}
    for i in range(len(pairsofparams)):
      splitparams={}
      splitparams=pairsofparams[i].split('=')
      if (len(splitparams))==2:
        param[splitparams[0]]=splitparams[1]
  return param

def downloadItem(params):
  addon_log(params)
  url = params['url']
  url = urllib.parse.unquote_plus(url)
    
  if(addon.getSetting('download_path')==''):
    message(addon.getLocalizedString(30001), addon.getLocalizedString(30009))
    return False
  
  dest = os.path.join(addon.getSetting('download_path'), ntpath.basename(url))
  
  try: 
    Downloader(url, dest, addon.getLocalizedString(30000), addon.getLocalizedString(30001))
    pass
  except Exception as inst:
    addon_log(inst)
    xbmc.executebuiltin("Notification(%s,%s,%i,%s)" % (addon.getLocalizedString(30011), url, 10000, "DefaultIconError.png"))
    return False
    
  #addon_log(params)
  #ADD ID3
  from mutagen.id3 import ID3NoHeaderError, ID3, TIT2, COMM, TCON
  title = params['title']
  title = urllib.parse.unquote_plus(title)
  comment = params['comment']
  comment = urllib.parse.unquote_plus(comment)
  try: 
    tags = ID3(dest)
  except ID3NoHeaderError:
    tags = ID3()
  tags['TIT2'] = TIT2( encoding=3, text=title )
  tags['COMM'] = COMM( encoding=3, desc='', text=comment )
  tags['TCON'] = TCON( encoding=3, text=u'teatru')
  tags.save(dest)

def downloadProgram(d=None):
  url = 'http://www.eteatru.ro/program.htm'
  if(d!=None):
    url = url + '?d='+d
  request = urllib.request.Request(url, None, headers)
  response = opener.open(request)
  programTxt = response.read()
  programTxt =  programTxt.decode('iso-8859-2')
  programTxt = cleanJson(programTxt)
  addon_log(programTxt)
  
  try:
    program = json.loads(programTxt, encoding='iso-8859-2')
    return program
  except Exception as inst:
    addon_log(inst)
    return False

def listProgram():
  program = downloadProgram()
  # addon_log(program)
  if(program != False): 
    for item in program:
      if(item[0]=='week' and item[4] == "1"):
        name = item[6]+' '+item[7]
        # name = name.encode('utf8')
        addDir(name, 4, [{'name':'d', 'value':item[5]}])
  
def listProgramDay(params):
  program = downloadProgram(params['d'])
  
  for item in program:
    if(item[0]=='program'):
      name = item[3]+' '+item[4]
      pars = HTMLParser()
      name = pars.unescape(name)
      name = name.encode('utf8')
      comment = item[5]
      comment = pars.unescape(comment)
      comment = comment.encode('utf8')
      listitem = xbmcgui.ListItem(name)
      listitem.setArt({'icon': "DefaultAudio.png"})
      listitem.setInfo('music', {'Title': name, 'Comment':comment})
      xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=None, listitem=listitem, isFolder=False)
  
  xbmc.executebuiltin("Container.SetViewMode(51)")
  
def listCollections():
  url = 'http://www.eteatru.ro/art-index.htm?c=3491'
  request = urllib.request.Request(url, None, headers)
  response = opener.open(request)
  collectionsTxt = response.read()
  collectionsTxt =  collectionsTxt.decode('utf-8', "ignore")
  collectionsTxt = cleanJson(collectionsTxt)
  #addon_log(collectionsTxt)
    
  program = []
  try:
    program = json.loads(collectionsTxt, encoding='iso-8859-2')
  except Exception as inst:
    addon_log(inst)
  
  pars = HTMLParser()
  tag_re = re.compile(r'(<!--.*?-->|<[^>]*>)')
  for item in program:
    if(item[0]=='subcategory'):
      name = item[3]
      name = pars.unescape(name)
      name = name.encode('utf8')
      
      descr = item[4]
      descr = pars.unescape(descr)
      descr = tag_re.sub('', descr)
      
      img = 'http://static.srr.ro/images/categories/'+item[8]
      
      addDir(name, 6, [{'name':'artId', 'value':item[1]}], descr, img)
      
def listCollectionItems(params):
  url = 'http://www.eteatru.ro/art-index.htm?c='+params['artId']
  request = urllib.request.Request(url, None, headers)
  response = opener.open(request)
  collectionItems = response.read()
  collectionItems = collectionItems.decode('iso-8859-2')
  collectionItems = cleanJson(collectionItems)
  #addon_log(collectionItems)
    
  program = []
  try:
    program = json.loads(collectionItems, encoding='iso-8859-2')
  except Exception as inst:
    addon_log(inst)
    
  #addon_log(program)
  
  pars = HTMLParser()
  tag_re = re.compile(r'(<!--.*?-->|<[^>]*>)')
  for item in program:
    if(item[0]=='articles' and item[10] != ''):
      name = item[4]
      name = pars.unescape(name)
      name = name.encode('utf8')
      
      descr = item[6]
      descr = pars.unescape(descr)
      descr = tag_re.sub('', descr)
      descr = descr.encode('utf8')

      url = "http://static.srr.ro/audio/articles/"+params['artId']+"/"+item[10]
      addon_log(url)
      
      addItem(url, name, descr)

#######################################################################################################################
#######################################################################################################################
#######################################################################################################################

#read params
params=getParams()
try:
  mode=int(params["mode"])
except:
  mode=None

if mode==None: 
  catList()
elif mode==1:
  listCurrent()
elif mode==2:
  downloadItem(params)
elif mode==3:
  listProgram()
elif mode==4:
  listProgramDay(params)
elif mode==5:
  listCollections()
elif mode==6:
  listCollectionItems(params)

xbmcplugin.endOfDirectory(int(sys.argv[1]))