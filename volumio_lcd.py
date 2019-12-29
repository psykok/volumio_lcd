#!/usr/bin/python
# -*- coding: utf-8 -*-

#
# forked from https://www.jimkim.de/high-fidelity/digital-music-player-with-raspberry-pi-and-volumio/
#

import subprocess
import textwrap
import time
import signal
import sys
import json
 
import Adafruit_CharLCD as LCD
 
# Raspberry Pi gpio pin configuration
lcd_rs        = 7
lcd_en        = 8
lcd_d4        = 25
lcd_d5        = 24
lcd_d6        = 23
lcd_d7        = 18
lcd_backlight = 26
 
# define LCD column and row size for LCD
lcd_columns = 20
lcd_rows    = 4
 
# init the LCD using the pins above
lcd = LCD.Adafruit_CharLCD(lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6, lcd_d7, lcd_columns, lcd_rows, lcd_backlight)
 
def sigterm_handler(signal, frame):
  lcd.set_cursor(0,0)
  line1 = ('      Volumio 1.55      ')[0:lcd_columns]
  line2 = ('    shutting down...    ')[0:lcd_columns]

  lcd.message(line1 + '\n' + line2 )
  sys.exit(0)
 
signal.signal(signal.SIGTERM, sigterm_handler)
 
def replace_specialchars(message):
  try:
#    message = message.encode('utf-8')
    message = message.replace('ä', chr(228))
    message = message.replace('ö', chr(246))
    message = message.replace('ü', chr(252))
#    message = message.replace('(', '-')
#    message = message.replace(')', ' ')

#    message = message.replace('Ä', chr(196))
#    message = message.replace('Ö', chr(214))
#    message = message.replace('Ü', chr(220))
#    message = message.replace('ß', chr(223))
#    message = message.replace('°', chr(223))
#    message = message.replace('µ', chr(228))
#    message = message.replace('´', chr(96))
#    message = message.replace('€', chr(227))
#    message = message.replace('–', '-')
#    message = message.replace('“', '"')
#    message = message.replace('”', '"')
#    message = message.replace('„', '"')
#    message = message.replace('’', '\'')
#    message = message.replace('‘', '\'')
    message = message.replace('è' 'e')
    message = message.replace('é''e')
    message = message.replace('ê', '')
    message = message.replace('á' 'a')
    message = message.replace('à','a')
    message = message.prelace('â' 'a')
  except:
    return message;
  return message
 
def main():
 
  # print welcome message
  line1 = '      Volumio 1.55      '
  line2 = '  initializing system   '
  line3 = line4 = ''
  lcd.message(line1 + '\n' + line2 + '\n' + line3+ '\n' + line4)
 
  # create custom char (...) = three dots in one character
  char_threeDots = [0b00000,0b00000,0b00000,0b00000,0b00000,0b00000,0b10101,0b00000]
  # create in ram position 0
  lcd.create_char(0, char_threeDots)
 
  # wait 2 seconds
  time.sleep(2.0)
 
  # clear display and turn on backlight
  lcd.clear()
  # lcd.backlight(lcd.ON)
 
  songArtistPrevious = ''
  stoppedSet = 0
  z = 0
 
  while True:
    # get current status and playtime
    process = subprocess.Popen('mpc', shell=True, stdout=subprocess.PIPE)
    status = process.communicate()[0]
    statusLines = status.split('\n')
 
    # check if mpc returns more that one line plus an extra
    # in that case we dont have stopped the music and can parse additional data
    if len(statusLines) > 2:
      # extract the song name / artist name (first line)
      # web radio has station name before artist / song
      songArtist = statusLines[0]
      if ":" in songArtist:
        songArtist = statusLines[0].split(':',1)[1].strip()
      if ":" not in songArtist:
        songArtist = statusLines[0]
 
      # extract player status (playing/stopped)
      infoPlayerStatus = statusLines[1].split(' ',1)[0].strip()
 
      # check for song change; only write new data to display 
      # if there is a change cause this is nicer to cpu 
      if songArtist != songArtistPrevious:
        songArtistPrevious = songArtist
        stoppedSet = 0
        z = 0
 
        infoArtist = songArtist.split(' - ',1)[0].strip()
        # shorten artist name if longer than lcd_columns 
        if len(infoArtist) > lcd_columns:
          infoArtist = (infoArtist)[0:lcd_columns - 1] + '\x00'
        # center
        while len(infoArtist) < (lcd_columns -1):
          infoArtist = ' ' + infoArtist + ' '
        infoArtist = infoArtist + '        '
 
        infoSong = songArtist.split(' - ',1)[1].strip()
        # shorten song name if longer than lcd_columns
        if len(infoSong) > lcd_columns:
          infoSong = (infoSong)[0:lcd_columns - 1] + '\x00'
        # center
        while len(infoSong) < (lcd_columns -1):
          infoSong = ' ' + infoSong + ' '
        infoSong = infoSong + '        '
        
        #
        # get bitrate from volumio
        # alter native : cat /proc/asound/card1/pcm0p/sub0/hw_params
        #
        vprocess = subprocess.Popen('volumio status', shell=True, stdout=subprocess.PIPE)
        vstatus = vprocess.communicate()[0]
        
        bitrat=''
        data = json.loads(vstatus)
        try: bitrate =  data["samplerate"] + " - " +  data["bitdepth"]
        except KeyError: pass
 
      # extract a string like '2:01/3:43 (54%)' 
      # from the string '[playing] #2/8   2:01/4:38 (50%)'
      infoLine = statusLines[1].split(']',1)[1].strip()
      # remove first character ('#')
      # format aftwerwards: 2/8   2:01/4:38 (50%)
      infoLine = infoLine[1:]
      infoTrack = infoLine.split(' ',1)[0].strip()
      infoTimes = infoLine.split(' ',1)[1].strip()
      # split of (50%)
      #infoTimes = infoTimes.split('(',1)[0].strip()
      infoTotalPlaytime = infoTimes.split('/',1)[1].strip()
        

      # toggle artist / track info 
      if z > 40:
        z = 0

      if z == 0:
        # show song title and artist
        lcd.set_cursor(0,0)
        line1 = (infoSong)[0:lcd_columns]
        line2 = (infoArtist)[0:lcd_columns]
        # clean special chars
        line1 = replace_specialchars(line1)
        line2 = replace_specialchars(line2)
        lcd.message(line1 + '\n' + line2 + '\n' + line3 + '\n' + line4 )

 
      # show song title and total play time / track
      lcd.set_cursor(0,0)
      line3 = (infoTimes)[0:lcd_columns]
      line4 = (bitrate)[0:lcd_columns]

      while len(line3) < (lcd_columns -1):
        line3 = ' ' + line3 + ' '
      while len(line4) < (lcd_columns -1):
        line4 = ' ' + line4 + ' '
      if infoPlayerStatus == '[paused]':
        line4 = '    [playing paused]    '
      line1 = replace_specialchars(line1)
      line2 = replace_specialchars(line2)
      lcd.message(line1 + '\n' + line2 + '\n' + line3 + '\n' + line4 )

 
    else:
      # message when stopped
      # set message only once, not in a loop (cpu friendly)
      if stoppedSet != 1:
        lcd.set_cursor(0,0)
        line1 = ('      Volumio 1.55      ')[0:lcd_columns]
        line2 = ('   [no music playing]   ')[0:lcd_columns]
        lcd.message(line1 + '\n' + line2)
        songArtistPrevious = ''
        stoppedSet = 1
 
    # sleep 0.5s
    time.sleep(1)
    z += 1
 
if __name__ == '__main__':
  main()
