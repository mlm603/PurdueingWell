# import libraries
import datetime
import pytz
import tweepy
import json
import os.path
import time
##import csv
from string import digits
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select

def get_api(cfg):
  auth = tweepy.OAuthHandler(cfg['consumer_key'], cfg['consumer_secret'])
  auth.set_access_token(cfg['access_token'], cfg['access_token_secret'])
  return tweepy.API(auth)

def send_tweet(twit):
  cfg = { 
    "consumer_key"        : "VALUE",
    "consumer_secret"     : "VALUE",
    "access_token"        : "VALUE",
    "access_token_secret" : "VALUE" 
    }
  api = get_api(cfg)
  tweet = twit
  status = api.update_status(status=tweet) 

def same_games():
  for x in range(1,game_count):
    try:
      #if Purdue is winning when it wasn't before
      if detail[x]['competitor0']=='Purdue' and (float(detail[x]['score0'])-float(detail[x]['score1']))>0 and (float(data[x]['score0'])-float(data[x]['score1']))<=0:
          #twit it
          twit = 'Purdue takes the lead against '+details[x]['competitor1']+'! Score: '+details[x]['score0']+'-'+details[x]['score1']+'; Excitement Index: '+details[x]['excitement']
          send_tweet(twit)
      elif detail[x]['competitor1']=='Purdue' and (float(detail[x]['score1'])-float(detail[x]['score0']))>0 and (float(data[x]['score1'])-float(data[x]['score0']))<=0:
          #twit it
          twit = 'Purdue takes the lead against '+details[x]['competitor0']+'! Score: '+details[x]['score1']+'-'+details[x]['score0']+'; Excitement Index: '+details[x]['excitement']
          send_tweet(twit)
      elif detail[x]['competitor0']=='Purdue' and (float(detail[x]['score0'])-float(detail[x]['score1']))<0 and (float(data[x]['score0'])-float(data[x]['score1']))>=0:
          #twit it
          twit = 'Nothing to see here...'
          send_tweet(twit)
      elif detail[x]['competitor1']=='Purdue' and (float(detail[x]['score1'])-float(detail[x]['score0']))<0 and (float(data[x]['score1'])-float(data[x]['score0']))>=0:
          #twit it
          twit = 'Nothing to see here...'
          send_tweet(twit)
    except:
      pass

#pick threshold for alerting (could potentially increase this as the tournament progresses)
threshold=4.5

#set url
quote_page = 'https://projects.fivethirtyeight.com/2018-march-madness-predictions/'

starttime=time.time()
while True:

  #use selenium/geckodriver to open firefox, navigate to url,
  #wait for 'livegame' css class to be present (indicates that needed data is loaded from 538's external scripts)
  #then grab all inner HTML and close browser
  browser = webdriver.Firefox()
  browser.get(quote_page)
  WebDriverWait(browser, 3).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div.livegame")))

  #FOR TESTING ONLY - REMOVE THIS LINE FOR LIVE GAMES
  ###########################################################################################################
  #Select(browser.find_element_by_id('gamedate-selector-mens')).select_by_value('March 18')
  ###########################################################################################################

  innerHTML = browser.execute_script("return document.body.innerHTML")
  browser.quit()


  # parse the html using beautiful soup and store in variable 'soup'
  soup = BeautifulSoup(innerHTML, 'html.parser')

  ready = soup.find(class_='excitement-num')
  if ready:

    # get useful info out of html
    comp=0
    details=[]
    game_dets = {}
    now=datetime.datetime.now(pytz.timezone('US/Eastern')).strftime("%m-%d-%Y")
    game_dets["date"]=now
    details.append(game_dets)
    game_dets = {}
    game_num=1
    #add competitors to objects pushed into an array (1 object/game)
    for x in soup.findAll('td', attrs={'class':'team'}):
        clean_team = x.text.strip().translate(str.maketrans('', '', digits))
        competitor="competitor"+str(comp)
        comp=(comp+1)%2
        game_dets[competitor] = clean_team
        if comp==0:
            game_dets["game_number"]=game_num
            details.append(game_dets)
            game_dets = {}
            game_num = game_num+1
    game_num=1
    #add excitement indices to existing game objects
    for x in soup.findAll('span', attrs={'class':'excitement-num'}):
        excitement_num=x.text.strip()
        details[game_num]["excitement"]=excitement_num
        game_num = game_num+1
    game_num=1
    sc=0
    #add scores to existing game objects
    for x in soup.findAll('td',attrs={'class':'score'}):
        clean_score = x.text.strip()
        score="score"+str(sc)
        sc=(sc+1)%2
        details[game_num][score]=clean_score
        if sc==0:
            game_num = game_num+1

    print(details)
    game_count=len(details)

    if os.path.exists('game_data.txt'):
        with open('game_data.txt') as datafile:
            data = json.loads(datafile.read())
            #if the dates are the same, compare new data to existing
            if now == data[0]['date']:
                #loop through games
                same_games()
            #else dump the existing data for new data
            else:
                same=true
                for x in range(1,game_count):
                  if details[x]['competitor0']!=data[x]['competitor0'] or details[x]['competitor1']!=data[x]['competitor1']:
                    same=false
                if same==false:
                  #loop through games
                  try:
                    #if Purdue is winning when it wasn't before
                    for x in range(1,game_count):
                      if detail[x]['competitor0']=='Purdue' and (float(detail[x]['score0'])-float(detail[x]['score1']))>0:
                          #twit it
                          twit = 'Purdue takes the lead against '+details[x]['competitor1']+'! Score: '+details[x]['score0']+'-'+details[x]['score1']+'; Excitement Index: '+details[x]['excitement']
                          send_tweet(twit)
                      elif detail[x]['competitor1']=='Purdue' and (float(detail[x]['score1'])-float(detail[x]['score0']))>0:
                          #twit it
                          twit = 'Purdue takes the lead against '+details[x]['competitor0']+'! Score: '+details[x]['score1']+'-'+details[x]['score0']+'; Excitement Index: '+details[x]['excitement']
                          send_tweet(twit)
                      elif detail[x]['competitor0']=='Purdue' and (float(detail[x]['score0'])-float(detail[x]['score1']))<0:
                          #twit it
                          twit = 'Nothing to see here...'
                          send_tweet(twit)
                      elif detail[x]['competitor1']=='Purdue' and (float(detail[x]['score1'])-float(detail[x]['score0']))<0:
                          #twit it
                          twit = 'Nothing to see here...'
                          send_tweet(twit)
                  except:
                    pass
                else:
                  same_games()
            #dump existing data for new data
            with open('game_data.txt','w') as new_datafile:
                json.dump(details,new_datafile)
    else:
        #loop through games
        try:
          for x in range(1,game_count):
            if detail[x]['competitor0']=='Purdue' and (float(detail[x]['score0'])-float(detail[x]['score1']))>0:
                #twit it
                twit = 'Purdue takes the lead against '+details[x]['competitor1']+'! Score: '+details[x]['score0']+'-'+details[x]['score1']+'; Excitement Index: '+details[x]['excitement']
                send_tweet(twit)
            elif detail[x]['competitor1']=='Purdue' and (float(detail[x]['score1'])-float(detail[x]['score0']))>0:
                #twit it
                twit = 'Purdue takes the lead against '+details[x]['competitor0']+'! Score: '+details[x]['score1']+'-'+details[x]['score0']+'; Excitement Index: '+details[x]['excitement']
                send_tweet(twit)
            elif detail[x]['competitor0']=='Purdue' and (float(detail[x]['score0'])-float(detail[x]['score1']))<0:
                #twit it
                twit = 'Nothing to see here...'
                send_tweet(twit)
            elif detail[x]['competitor1']=='Purdue' and (float(detail[x]['score1'])-float(detail[x]['score0']))<0:
                #twit it
                twit = 'Nothing to see here...'
                send_tweet(twit)
        except:
          pass
        #dump existing data for new data
        with open('game_data.txt','w') as new_datafile:
            json.dump(details,new_datafile)
  else:
    print('no live games')
  time.sleep(60.0 - ((time.time() - starttime) % 60.0))

##
##if __name__ == "__main__":
##  main()
