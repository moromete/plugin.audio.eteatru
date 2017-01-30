import xbmc, xbmcgui, xbmcplugin, xbmcaddon
import urllib
import os, os.path
import json, re
import ntpath
import HTMLParser

from glob import addon_log, addon, Downloader, cleanJson, message
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
  #addon_log(playInfoTxt)
    
  try:
    playInfo = json.loads(playInfoTxt, encoding='iso-8859-2')
    name = playInfo[0][1]
    pars = HTMLParser.HTMLParser()
    name = pars.unescape(name)
    name = name.encode('utf8')
    comment = playInfo[0][2]
    comment = pars.unescape(comment)
    comment = re.sub('<[^<]+?>', '', comment)
    comment = comment.encode('utf8')
    url = playInfo[0][3]
    offset = playInfo[0][6]
  except Exception as inst:
    addon_log(inst)
    return False
  
  plugin=sys.argv[0]
  listitem = xbmcgui.ListItem(name, iconImage="DefaultAudio.png")
  listitem.setInfo('music', {'Title': name, 'Comment':comment})
  u=plugin+"?mode=2"+\
           "&url="+urllib.quote_plus(url)
  contextMenuItems = [( addon.getLocalizedString(30010), "XBMC.RunPlugin("+u+")", )]
  listitem.addContextMenuItems(contextMenuItems)
  
  xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=listitem,isFolder=False)
  xbmc.executebuiltin("Container.SetViewMode(51)")
  
#def playCurrent(params):
#  p = player(xbmc.PLAYER_CORE_AUTO, offset=int(playInfo[0][6]))
#  p.play(playInfo[0][3], listitem)
  
def addDir(name, mode, params=None):
  contextMenuItems = []

  plugin=sys.argv[0]

  u = plugin+"?"+"mode="+str(mode)
  if(params!=None):
    for param in params:
      u = u + '&' + param['name'] + '=' + param['value']  
    
  liz = xbmcgui.ListItem(name, iconImage="DefaultFolder.png")
  liz.setInfo( type="Audio", infoLabels={ "Title": name })
  xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)

def catList():
  addDir(addon.getLocalizedString(30005), 1)
  addDir(addon.getLocalizedString(30006), 3)
  
  #Downloads
  if(addon.getSetting('download_path')!=''):
    liz = xbmcgui.ListItem(addon.getLocalizedString(30008), iconImage="DefaultFolder.png")
    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=addon.getSetting('download_path'), listitem=liz, isFolder=True)
    
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
  except Exception as inst:
    addon_log(inst)

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

xbmcplugin.endOfDirectory(int(sys.argv[1]))