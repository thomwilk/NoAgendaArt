import os
import html
import sys
from bs4 import BeautifulSoup
import re
from urllib.request import Request, urlopen
import urllib
import http
import urllib.request

opener=urllib.request.build_opener()
opener.addheaders=[('User-Agent','Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1941.0 Safari/537.36')]
urllib.request.install_opener(opener)


print("Scanning the archive, hang on MOFO...")

# Get number of pages
url = "https://noagendaartgenerator.com/artworks"
req = Request(url)
response = urlopen(req).read()
soup = BeautifulSoup(response, "html.parser")
lastPage = soup.find('a', rel='next')
lastPage = lastPage.parent
numPagesStr = lastPage.previous_sibling.get_text()
numPages = int(numPagesStr)
failed = []

invalidChars = ['/', '\\', ':', '*', '?', '"', '\'', '<', '>', '|']


def filter_nonprintable(text):
    import string
    # Get the difference of all ASCII characters from the set of printable characters
    nonprintable = set([chr(i) for i in range(128)]).difference(string.printable)
    # Use translate to remove all non-printable characters
    return text.translate({ord(character):None for character in nonprintable})

# Loop through pages
for i in range(1, numPages):
    print("Scanning archive page " + str(i) + " of " + numPagesStr + " for new art hang on MOFO...")
    url = "https://noagendaartgenerator.com/artworks?page=" + str(i)
    req = Request(url)
    response = urlopen(req).read()
    soup = BeautifulSoup(response, "html.parser")
    data = soup.find_all('div', attrs={'class': 'fx-overlay'})
    artIds = []
    for div in data:
        links = div.find_all('a')
        for a in links:
            if a.get('href') is None:
                continue
            else:
                artIds.append("https://noagendaartgenerator.com" + a.get('href'))
    for artId in artIds:
        req = Request(artId)
        response = urlopen(req).read()
        soup = BeautifulSoup(response, "html.parser")
        try:
            results = soup.find('h1', attrs={'class': 'artworktitle'}).get_text()
        except AttributeError:
            if "com/cdn-cgi/" not in artId:
                failed.append(artId)
            continue

        results = results.replace('\n', '')
        results = results.replace('Episode ', '')
        epNo = re.search('\d{1,4}', results)[0]
        epNo = epNo.replace(' ', '')
        artTitle = re.search('".*"', results)[0]
        artTitle = filter_nonprintable(html.unescape(artTitle))
        i = 0
        while i < len(invalidChars):
            artTitle = artTitle.replace(invalidChars[i], '')
            i += 1
        try:
            epArtist = re.search('by.*', results)[0]
            epArtist = epArtist.replace('by ', '')
        except TypeError:
            epArtist = "UNKNOWN"
        i = 0
        while i < len(invalidChars):
            epArtist = epArtist.replace(invalidChars[i], '')
            i += 1
        data = soup.find_all('img', attrs={'class': 'singleartwork'})
        if data:
            imgUrl = "https://noagendaartgenerator.com" + data[0]['src']
            imgFile = imgUrl.split("/")[-1]

            try:
                os.mkdir(epNo)
            except FileExistsError:
                pass
            filePath = os.path.join(epNo, epNo + "-" + artTitle + "-" + epArtist + ".png")
            if os.path.isfile(filePath) is False:
                urllib.request.urlretrieve(imgUrl, filePath)
                print(epNo + "-" + artTitle + "-" + epArtist + ".png has been downloaded")
print("Done. Thanks citizen!")
for fail in failed:
    print(fail)
