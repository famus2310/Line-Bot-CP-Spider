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

ANNOUNCE_URL = "https://cp-tc-contest-spider.herokuapp.com/announce"
URL = "https://clist.by/"

print("Start SCRAPING")

with requests.Session() as sess:
    resp = sess.get(URL)
    soup = BeautifulSoup(resp.text, 'html.parser')
    mydivs = soup.findAll("div", {"class": "contest"})
    contest_titles = soup.findAll("span", {"class": "contest_title"})
    contest_coming = soup.find("div", {"class": "coming"})
    duration = contest_coming.find("div", {"class": "countdown"}).text.strip()
    coming_title = contest_coming.find("span", {"class": "contest_title"}).text.strip()
    if "days" not in duration:
        coming_hour, coming_minute, coming_second = duration.split(':')
        if (int(coming_hour) < 2):
            payload = {
                "text" : str(coming_title) + " starts in " + str(coming_hour) + " hours " + str(coming_minute) + " minutes " + str(coming_second) + " second "
            }
            resp = sess.post(ANNOUNCE_URL, data=payload)

    cp_contest_titles = []
    for x in contest_titles:
        for y in CP_CONTEST_SITES:
            if y in str(x):
                cp_contest_titles.append(re.search('href="(?!#)(.)*"', str(x))[0].strip('href='))

                break
                
    payload = {
        "secret_key": os.environ.get('SECRET_KEY'),
        "contests": []
    }
    for i in cp_contest_titles:
        link, title = i.split(' title=')
        link = link.strip('\"')
        title = title.strip('\"')
        payload["contests"].append({"title" : title, "link" : link})

    sess.post(URL, json=payload)