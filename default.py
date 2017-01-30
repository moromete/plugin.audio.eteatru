import xbmc, xbmcgui, xbmcplugin, xbmcaddon
import urllib
import os, os.path
import json, re
import ntpath

from glob import addon_log, addon, Downloader, cleanJson
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
    name = name.encode('utf8')
    comment = playInfo[0][2]
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
  contextMenuItems = [( 'Download', "XBMC.RunPlugin("+u+")", )]
  listitem.addContextMenuItems(contextMenuItems)
  
  #"&mode=2"+\
  #u=plugin+"?url="+urllib.quote_plus(url)+\
  #         "&name="+urllib.quote_plus(name)+\
  #         "&offset="+urllib.quote_plus(offset)
  
  xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=listitem,isFolder=False)
  xbmc.executebuiltin("Container.SetViewMode(51)")
  
#def playCurrent(params):
#  p = player(xbmc.PLAYER_CORE_AUTO, offset=int(playInfo[0][6]))
#  p.play(playInfo[0][3], listitem)
  
def addDir(name, mode):
  contextMenuItems = []

  plugin=sys.argv[0]

  u = plugin+"?"+"mode="+str(mode) + \
      "&name="+urllib.quote_plus(name)
  ok = True

  liz = xbmcgui.ListItem(name, iconImage="DefaultFolder.png",thumbnailImage="")
  liz.setInfo( type="Audio", infoLabels={ "Title": name })
  ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
  return ok

def catList():
  addDir(addon.getLocalizedString(30005), 1)
  addDir(addon.getLocalizedString(30006), 3)
  #addDir('Favorites', 3)
    
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
  
  dest = os.path.join(addon.getSetting('download_path'), ntpath.basename(url))
  
  try: 
    Downloader(url, dest, addon.getLocalizedString(30000), addon.getLocalizedString(30001))
  except Exception as inst:
    addon_log(inst)

def listProgram():
  url = 'http://www.eteatru.ro/program.htm'
  
  temp = os.path.join(addon.getAddonInfo('path'),"program.htm")
  
  try: 
    Downloader(url, temp, addon.getLocalizedString(30000), addon.getLocalizedString(30007))
    f = open(temp)
    programTxt = f.read()
    f.close()
    os.remove(temp)
  except Exception as inst:
    programTxt = ""
  
  #programTxt = '["page","program",]'
  
  programTxt = cleanJson(programTxt)
  
  addon_log(programTxt)
  
  try:
    program = json.loads(programTxt, encoding='iso-8859-2')
  except Exception as inst:
    addon_log(inst)
    return False
  
  
  
  
  addon_log(program)
  
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
#elif mode==3:
#  pass

xbmcplugin.endOfDirectory(int(sys.argv[1]))