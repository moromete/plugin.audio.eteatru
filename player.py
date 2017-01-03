import xbmc

import xbmcaddon
addon = xbmcaddon.Addon('plugin.audio.eteatru')
def addon_log(string):
  #DEBUG = addon.getSetting('debug')
  DEBUG = 'true'
  ADDON_VERSION = addon.getAddonInfo('version')
  if DEBUG == 'true':
    if isinstance(string, unicode):
      string = string.encode('utf-8')
    xbmc.log("[plugin.audio.eteatru-%s]: %s" %(ADDON_VERSION, string))

class player(xbmc.Player):
  def __init__( self , *args, **kwargs):
    self.offset=kwargs.get('offset')
    self.player_status = None
   
  def play(self, url, listitem):
    self.player_status = 'play';
    super(player, self).play(url, listitem, True)
    self.keep_allive()
    
  def onPlayBackStarted(self):
    #addon_log('aaaaaaaaaaaaaaaaa')
    #addon_log(self.offset)
    self.seekTime(self.offset)
    self.player_status = 'offset';
    #self.seekTime(10)
    #super(player, self).onPlayBackStarted()  
  
  #def onPlayBackEnded(self):
    #self.player_status = 'end';

  #def onPlayBackStopped(self):
    #self.player_status = 'stop';
    
  def keep_allive(self):
    xbmc.sleep(500)
    #addon_log(self.player_status)
    while (self.player_status=='play'):
      addon_log('ALLIVE-')
      addon_log('ALLIVE|')
      xbmc.sleep(500)
