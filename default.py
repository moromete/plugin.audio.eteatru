import xbmc, xbmcgui, xbmcplugin, xbmcaddon
import urllib
import os, os.path
import json
import re

from player import player

addon = xbmcaddon.Addon('plugin.audio.eteatru')

def addon_log(string):
  #DEBUG = addon.getSetting('debug')
  DEBUG = 'true'
  ADDON_VERSION = addon.getAddonInfo('version')
  if DEBUG == 'true':
    if isinstance(string, unicode):
      string = string.encode('utf-8')
    xbmc.log("[plugin.audio.eteatru-%s]: %s" %(ADDON_VERSION, string))

def Downloader(url,dest,description,heading):
  dp = xbmcgui.DialogProgress()
  dp.create(heading,description,url)
  dp.update(0)

  urllib.urlretrieve(url,dest,lambda nb, bs, fs, url=url: _pbhook(nb,bs,fs,dp))
  
def _pbhook(numblocks, blocksize, filesize, dp=None):
  try:
    percent = int((int(numblocks)*int(blocksize)*100)/int(filesize))
    dp.update(percent)
  except:
    percent = 100
    dp.update(percent)
  if dp.iscanceled():
    #raise KeyboardInterrupt
    dp.close()

def cleanJson(string):
  string = re.sub(",[ \t\r\n]+}", "}", string)
  string = re.sub(",[ \t\r\n]+\]", "]", string)

  return string

def playCurrent():
  url = 'http://www.eteatru.ro/play.htm'
  
  temp = os.path.join(addon.getAddonInfo('path'),"play.htm")
  
  try: 
    Downloader(url, temp, addon.getLocalizedString(30000), addon.getLocalizedString(30001))
    f = open(temp)
    playInfoTxt = f.read()
    f.close()
    os.remove(temp)
  except Exception as inst:
    playInfoTxt = ""
  
  playInfoTxt = cleanJson(playInfoTxt)
  
  addon_log(playInfoTxt)
  
  try:
    playInfo = json.loads(playInfoTxt, encoding='iso-8859-2')
  except Exception as inst:
    addon_log(inst)
    return False
  
  addon_log(playInfo)
  
  addon_log(playInfo[0][3])
  
  listitem = xbmcgui.ListItem(playInfo[0][1], iconImage="DefaultVideo.png")
  #listitem.setLabel(name)
  listitem.setInfo('music', {'Title': playInfo[0][1], 'Comment':playInfo[0][2]})

  addon_log(int(playInfo[0][6]))
  
  p = player(xbmc.PLAYER_CORE_AUTO, offset=int(playInfo[0][6]))
  p.play(playInfo[0][3], listitem)
  

#######################################################################################################################
#######################################################################################################################
#######################################################################################################################

playCurrent()

xbmcplugin.endOfDirectory(int(sys.argv[1]))