#coding=utf8

'''
Anna Bonazzi, 02/09/2018

# Script to scrape water-relevant articles from Indian newspaper The Hindu (https://www.thehindu.com/archive/), with a focus on newspaper sections concerning Tamil Nadu and Chennai. Saves articles as "section_date_title.txt"

'''
# To time the script
from datetime import datetime
startTime = datetime.now()
import datetime, os, re
from collections import defaultdict
# For scraping
from lxml import html
import requests

#--------------------------

# Variables to be defined
out_dir = '/home/anna/Documents/corpus_work/The_Hindu'
archive = 'https://www.thehindu.com/archive/web/'
start_date = '15/08/2009'
end_date = '01/09/2018'
options = 'water|flood|drought|drainage|sewage|inundation|rain|stream|river|ocean|lake|reservoir'
# Allows to separate results in 2 groups of choice
folder1 = 'tn_articles'
folder2 = 'all_articles'
# Newspaper sections that go in the first group
folder1_words = ['chennai', 'tamil nadu']


#--------------------------
os.chdir(out_dir)
try:
    os.system("mkdir "+folder1)
    os.system("mkdir "+folder2)
except:
    pass

def scraper(url):
    # Retrieves page
    page = requests.get(url)
    # Saves parsed results
    tree = html.fromstring(page.content)
    return (tree)

# Creates range of dates to be scraped
dates = []
start = datetime.datetime.strptime(start_date, '%d/%m/%Y')
end = datetime.datetime.strptime(end_date, '%d/%m/%Y')
date_generated = [start + datetime.timedelta(days=x) for x in range(0, (end-start).days)]
for d in date_generated:
    date = d.strftime('%d/%m/%Y')
    dates.append(date)

for date in dates:
    print('\nScraping '+date)
    url = archive+date
    # Scrapes 1 archive page
    tree = scraper(url)
    
    # Saves section names
    sections = tree.xpath('//div[@class="section-header"]/div//h2/a/text()')
    for i in range (0, len(sections)):
        sections[i] = sections[i].strip()
    
    # Saves article links for each section
    articles = defaultdict(list)
    for s in sections:
        art_links = tree.xpath('//section[@id="section_'+str(int(sections.index(s))+1)+'"]//div[@class="section-container"]/div/div/div/ul/li/a/@href')
        for a in art_links:
            articles[s].append(a)
     
    # Gets article text
    for section in articles: 
        for url in articles[section]:
            tree = scraper(url)
            # Gets title
            title = tree.xpath('//div[@class="article"]/h1[@class="title"]/text()')
            try:
                title = title[0].strip()
            except:
                title = 'N/A'
            # Gets author
            author = tree.xpath('//a[@class="auth-nm no-lnk"]/text()')
            try:
                author = author[0].strip()
            except:
                author = 'N/A'
            # Gets text
            text = tree.xpath('//div[starts-with(@id, "content-body-")]//text()')
            # Writes output in taggable format
            str_txt = str(text).strip("['").strip("']").replace("', '",'')
            regex = re.search('(?i)('+options+')', str_txt)
            if regex:
                # Sorts contents in predefined folders
                word = 'no'
                for w in folder1_words:
                    if w == section:
                        word = 'yes'
                if word == 'yes':
                    folder = folder1
                else:
                    folder = folder2
                with open(folder+'/'+section+'_'+date.replace('/', '_')+'_'+title+'.txt', 'w') as out:
                    out.write('<title>'+title+'</title>\n<date>'+date+'</date>\n<author>'+author+'</author>\n<article>\n')
                    # Cleans article text of initial \n
                    if text[0] == '\n':
                        del text[0]
                    for l in text:
                        out.write(l)
                    out.write('</article>')
        
   
#--------------------------
# To time the script
time = datetime.now() - startTime
print ("\n(Script running time: " + str(time) + ")")
