import xbmc, xbmcgui, xbmcplugin, xbmcaddon
import urllib
import os, os.path
import json, re
import ntpath
import HTMLParser

from common import addon_log, addon, Downloader, cleanJson, message
from player import player

def listCurrent():
  url = 'http://www.eteatru.ro/play.htm'
  
  temp = os.path.join(addon.getAddonInfo('path'),"play.htm")
  
  try: 
    Downloader(url, temp, addon.getLocalizedString(30000), addon.getLocalizedString(30001))
    f = open(temp)
    playInfoTxt = f.read()
    f.close()
    os.remove(temp)
  except Exception as inst:
    addon_log(inst)
    playInfoTxt = ""
  
  playInfoTxt = cleanJson(playInfoTxt)
  addon_log(playInfoTxt)
    
  try:
    playInfo = json.loads(playInfoTxt, encoding='iso-8859-2')
    name = playInfo[0][1]
    pars = HTMLParser.HTMLParser()
    name = pars.unescape(name)
    name = name.encode('utf8')
    comment = playInfo[0][2]
    comment = pars.unescape(comment)
    tag_re = re.compile(r'(<!--.*?-->|<[^>]*>)')
    comment = tag_re.sub('', comment)
    #comment = re.sub('<[^<]+?>', '', comment)
    comment = comment.encode('utf8')
    url = playInfo[0][3]
    offset = playInfo[0][6]
  except Exception as inst:
    addon_log(inst)
    return False
  
  addItem(url, name, comment)
  #xbmc.executebuiltin("Container.SetViewMode(51)")
  
def addItem(url, name, comment):
  plugin=sys.argv[0]
  listitem = xbmcgui.ListItem(name, iconImage="DefaultAudio.png")
  #listitem.setInfo('music', {'Title': name, 'Comment':comment})
  listitem.setInfo( type="video", infoLabels={ "title": name, 'plot':comment })
  u=plugin+"?mode=2"+\
           "&url="+urllib.quote_plus(url)+\
           '&title='+urllib.quote_plus(name)+\
           '&comment='+urllib.quote_plus(comment)
  contextMenuItems = [( addon.getLocalizedString(30010), "XBMC.RunPlugin("+u+")", )]
  listitem.addContextMenuItems(contextMenuItems)
  
  xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=listitem,isFolder=False)
  
#def playCurrent(params):
#  p = player(xbmc.PLAYER_CORE_AUTO, offset=int(playInfo[0][6]))
#  p.play(playInfo[0][3], listitem)
  
def addDir(name, mode, params=None, descr="", img=None):
  contextMenuItems = []

  plugin=sys.argv[0]

  u = plugin+"?"+"mode="+str(mode)
  if(params!=None):
    for param in params:
      u = u + '&' + param['name'] + '=' + param['value']  
    
  if(img == None):
    img = "DefaultFolder.png"
  liz = xbmcgui.ListItem(name,
                         iconImage=img)
  liz.setInfo( type="video", infoLabels={ "title": name, 'plot':descr })
  xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)

def catList():
  addDir(addon.getLocalizedString(30005), 1)
  addDir(addon.getLocalizedString(30006), 3)
  
  #Downloads
  if(addon.getSetting('download_path')!=''):
    liz = xbmcgui.ListItem(addon.getLocalizedString(30008), iconImage="DefaultFolder.png")
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
  url = params['url']
  url = urllib.unquote_plus(url)
    
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
  title = urllib.unquote_plus(title)
  comment = params['comment']
  comment = urllib.unquote_plus(comment)
  try: 
    tags = ID3(dest)
  except ID3NoHeaderError:
    tags = ID3()
  tags['TIT2'] = TIT2( encoding=3, text=title.decode('utf8') )
  tags['COMM'] = COMM( encoding=3, desc='', text=comment.decode('utf8') )
  tags['TCON'] = TCON( encoding=3, text=u'teatru')
  tags.save(dest)

def downloadProgram(d=None):
  url = 'http://www.eteatru.ro/program.htm'
  if(d!=None):
    url = url + '?d='+d
   
  temp = os.path.join(addon.getAddonInfo('path'),"program.htm")
  
  try: 
    Downloader(url, temp, addon.getLocalizedString(30000), addon.getLocalizedString(30007))
    f = open(temp)
    programTxt = f.read()
    f.close()
    os.remove(temp)
  except Exception as inst:
    programTxt = ""
  
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
  
  for item in program:
    if(item[0]=='week'):
      name = item[6]+' '+item[7]
      name = name.encode('utf8')
      addDir(name, 4, [{'name':'d', 'value':item[5]}])
  
  xbmc.executebuiltin("Container.SetViewMode(51)")
  
def listProgramDay(params):
  program = downloadProgram(params['d'])
  
  for item in program:
    if(item[0]=='program'):
      name = item[3]+' '+item[4]
      pars = HTMLParser.HTMLParser()
      name = pars.unescape(name)
      name = name.encode('utf8')
      comment = item[5]
      comment = pars.unescape(comment)
      comment = comment.encode('utf8')
      listitem = xbmcgui.ListItem(name, iconImage="DefaultAudio.png")
      listitem.setInfo('music', {'Title': name, 'Comment':comment})
      xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=None, listitem=listitem, isFolder=False)
  
  xbmc.executebuiltin("Container.SetViewMode(51)")
  
def listCollections():
  url = 'http://www.eteatru.ro/art-index.htm?c=3491'
  temp = os.path.join(addon.getAddonInfo('path'),"collections.json")
  try: 
    Downloader(url, temp, addon.getLocalizedString(30000), addon.getLocalizedString(30007))
    f = open(temp)
    collectionsTxt = f.read()
    f.close()
    os.remove(temp)
  except Exception as inst:
    addon_log(inst)
    collectionsTxt = ""
  
  collectionsTxt = cleanJson(collectionsTxt)
  #addon_log(collectionsTxt)
    
  program = [];
  try:
    program = json.loads(collectionsTxt, encoding='iso-8859-2')
  except Exception as inst:
    addon_log(inst)
  
  pars = HTMLParser.HTMLParser()
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
  temp = os.path.join(addon.getAddonInfo('path'),"collectionItem.json")
  try: 
    Downloader(url, temp, addon.getLocalizedString(30000), addon.getLocalizedString(30007))
    f = open(temp)
    collectionItems = f.read()
    f.close()
    os.remove(temp)
  except Exception as inst:
    addon_log(inst)
    collectionItems = ""
  
  collectionItems = cleanJson(collectionItems)
  #addon_log(collectionItems)
    
  program = [];
  try:
    program = json.loads(collectionItems, encoding='iso-8859-2')
  except Exception as inst:
    addon_log(inst)
    
  #addon_log(program)
  
  pars = HTMLParser.HTMLParser()
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