#!/usr/bin/env python2.7

# Work sample which scrapes news.ycombinator.com
# and outputs an HTML table containing:
# 1. Rank
# 2. Title
# 3. Link
# 4. Points
# 5. Submitter

import requests
from bs4 import BeautifulSoup
import markup

import re
from collections import namedtuple

Article = namedtuple('Article', 'rank, title, link, points, submitter')

SCORE_REGEX = re.compile('^score_\d+')
USER_REGEX = re.compile('user\?id=.*')

class Webscraper:
    soup = None
    articles = []

    # Constructor takes url and outputfile as argument
    def __init__(self, url):
        req = requests.get(url)
        self.soup = BeautifulSoup(req.text)
        req.close()

    def parse(self):
        # table[0] is the page layout
        # table[1] is login header
        # table[2] contains the actual articles
        newsTable = self.soup.findAll('table')[2]
        # tr rows alternate between news article,
        # followed by metadata, followed by 5px spacer
        newsRows = newsTable.findAll('tr')
        # create tuples of article, metadata from groups of 3 trs
        articleMetaPairs = zip(newsRows[0::3], newsRows[1::3])
        for (article, meta) in articleMetaPairs:
            # 10px spacer indicates 'More' link, which is not an article
            if not (article.find('td') is None or article.has_attr('style')):
                self.parseItem(article, meta)

    # Parse news item and its metadata, add it to the list of articles
    def parseItem(self, article, meta):
        titleTDs = article.findAll('td', class_='title')
        articleRank = titleTDs[0].text
        articleAnchor = titleTDs[1].find('a')
        articleLink = articleAnchor['href'] if articleAnchor.has_attr('href') else ''
        articleTitle = articleAnchor.text
        scoreSpan = meta.find('span', id=SCORE_REGEX)
        articleScore = scoreSpan.text if scoreSpan is not None else 'no points'
        userAnchor = meta.find('a', href=USER_REGEX)
        articleSubmitter = userAnchor.text if userAnchor is not None else 'unknown'

        self.articles.append(Article(rank=articleRank, title=articleTitle, link=articleLink, points=articleScore, submitter=articleSubmitter))

    # Output in requested html table format
    def outputTable(self, outputFileName):
        with open(outputFileName, 'w') as outputfile:
            page = markup.page()
            page.init(title="AKovacs Work Sample",
                css="http://netdna.bootstrapcdn.com/bootstrap/3.1.1/css/bootstrap.min.css")
            page.h3("""Articles scraped from <a href="http://news.ycombinator.com">Hacker News</a> frontpage""")
            page.table(class_="table table-hover")

            # Build table header
            page.thead.open()
            page.tr.open()
            for column in Article._fields:
                if column != 'link':
                    page.th(column)
            page.tr.close()
            page.thead.close()

            # Build table rows
            for article in self.articles:
                self.outputArticle(page, article)
            page.table.close()
            page.p("Created by akovacs")
            outputfile.write(page.__str__().encode('utf8'))

    def outputArticle(self, page, article):
        page.tr.open()
        page.td(article.rank)
        page.td.open()
        # Truncate title text to 50 lines
        page.a(article.title[:80] + (article.title[80:] and '...'), href=article.link)
        page.td.close()
        page.td(article.points)
        page.td(article.submitter)
        page.tr.close()


if __name__ == "__main__":
    hnscraper = Webscraper('http://news.ycombinator.com/')
    hnscraper.parse()
    hnscraper.outputTable('index.html')
