import requests
import os
from bs4 import BeautifulSoup
import re

CP_CONTEST_SITES = [
  "atcoder",
  "yukicoder",
  "codeforces",
  "codechef",
  "dmoj",
  "codejam",
  "usaco",
  "icpc", 
  "tlx.toki",
  "leetcode"
]

STATUS_LIST = [
  "coming",
  "running",
  "past"
]

BASE_URL = "https://cp-tc-contest-spider.herokuapp.com"
REFRESH_URL = BASE_URL + "/refresh_contest"
ANNOUNCE_URL = BASE_URL + "/announce"
URL = "https://clist.by/"

print("Start SCRAPING")

with requests.Session() as sess:
  resp = sess.get(URL)
  soup = BeautifulSoup(resp.text, 'html.parser')
  mydivs = soup.findAll("div", {"class": "contest"})
  contests = soup.find("div", {"id" : "contests"}).findAll("div", recursive=False)
  contest_titles = soup.findAll("span", {"class": "contest_title"})
  contest_coming_list = soup.findAll("div", {"class": "coming"})
  found = False
  for contest in contest_coming_list:
    for cp_site in CP_CONTEST_SITES:
      if cp_site in contest.text:
        contest_coming = contest
        found = True
    if found:
      break
  if found:
    duration = contest_coming.find("div", {"class": "countdown"}).text.strip()
    coming_title = contest_coming.find("span", {"class": "contest_title"}).text.strip()
    coming_link = contest_coming.find("span", {"class": "contest_title"}).a['href']
    if "days" not in duration:
      coming_hour, coming_minute, coming_second = duration.split(':')
      if (int(coming_hour) < 2):
        payload = {
          "secret_key": os.environ.get('SECRET_KEY'),
          "text" : str(coming_title) + "\n(" + str(coming_link) + ")\n" + "starts in " + str(coming_hour) + " hours " + str(coming_minute) + " minutes " + str(coming_second) + " second "
        }
        resp = sess.post(ANNOUNCE_URL, data=payload)
  cp_contest_titles = []
  for x in contests:
    cur_title = x.find("span", {"class" : "contest_title"})
    status = ""
    for status_list in STATUS_LIST:
      if status_list in x.attrs.get('class'):
        status = status_list
    if status == "":
      continue
    for y in CP_CONTEST_SITES:
      if y in str(cur_title):
        title = cur_title.a.get('title')
        href = cur_title.a.get('href')
        if title is not None and href is not None:
          cp_contest_titles.append((href, title, status.upper()))

          break
        
  payload = {
    "secret_key": os.environ.get('SECRET_KEY'),
    "contests": []
  }
  for i in cp_contest_titles:
    link, title, status = i[0], i[1], i[2]
    payload["contests"].append({"title" : title, "link" : link, "status" : status})
  sess.post(REFRESH_URL, json=payload)
