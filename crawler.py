#!/usr/bin/env python3

import requests
from urllib.parse import urlparse, urljoin, urlunparse
from time import sleep
from bs4 import BeautifulSoup
from sys import stderr

def getUrl(url, verbose=False):
    if (verbose):
        stderr.write(f'... fetching {url}\n')
    return requests.get(url)

def getPrograms(baseUrl):

    def worker(baseUrl, pageNum):

        def getBackgroundUrl(div):
            u = urlparse(div['style'].split('\'')[1])
            u = u._replace(query='')
            return urlunparse(u)

        response = getUrl(baseUrl + f'/page/{pageNum}')
        soup = BeautifulSoup(response.text, 'html.parser')
        programUrls = [urljoin(baseUrl, link['href'])
                for link in soup.find_all('a', class_='tales__list-link')]
        programTitles = [''.join(div.find_all(text=True)).strip()
                for div in soup.find_all('div', class_='tales__list-anonce-title')]
        programCoverUrls = [getBackgroundUrl(div)
                for div in soup.find_all('div', class_='tales__list-img_wrap')]

        return list(zip(programUrls, programTitles, programCoverUrls))

    data_ = []
    pageNum = 1
    while True:
        d = worker(baseUrl, pageNum)
        if len(d) == 0:
            break
        data_.extend(d)
        pageNum += 1
        sleep(1)  # Don't be rude

    # Recurse
    data = []
    for d in data_:
        programUrl = d[0]
        if programUrl.find('program_child') != -1:
            data.append(d)
        else:
            subData = getPrograms(programUrl)
            data.extend(subData)

    return data


def getEpisodes(programUrl):
    podcastsBaseUrl = 'https://www.deti.fm/more_podcast/uid/'
    programId = programUrl.split('/')[-1]
    podcastBaseUrl = urljoin(podcastsBaseUrl, programId)

    def worker(podcastBaseUrl, pageNum):
        response = getUrl(podcastBaseUrl + f'?page={pageNum}')
        soup = BeautifulSoup(response.text, 'html.parser')

        items = []
        for name_tag in soup.find_all('div', class_='podcasts__item-name'):
            title = ''.join(name_tag.find_all(text=True)).strip()
            url = urljoin(programUrl, name_tag['onclick'].split('\'')[1])
            if title:
                items.append((url, title))
        return items

    pageNum = 1
    data = []
    while True:
        d = worker(podcastBaseUrl, pageNum)
        pageNum += 1
        if len(d) == 0:
            break
        data.extend(d)
        sleep(1)  # Don't be rude

    return data


def getEpisodeData(episodeUrl):
    response = getUrl(episodeUrl)
    soup = BeautifulSoup(response.text, 'html.parser')
    coverUrl = urlparse(soup.find('img', class_='podcasts__screen-pic')['src'])._replace(query='')
    episodeId = episodeUrl.split('/')[-1]
    audioUrl = soup.find('audio', id=f'player_{episodeId}')['src']
    return (audioUrl, urlunparse(coverUrl))


if __name__ == '__main__':
    baseUrl = 'https://www.deti.fm/fairy_tales'
    for programUrl, programTitle, programCoverUrl in getPrograms(baseUrl):
        print('\t'.join(['program', programTitle, programCoverUrl]))
        for episodeNum, (episodeUrl, episodeTitle) in enumerate(reversed(getEpisodes(programUrl))):
            episodeAudioUrl, episodeCoverUrl = getEpisodeData(episodeUrl)
            print('\t'.join(
                ['episode', str(episodeNum + 1), episodeTitle, episodeAudioUrl, episodeCoverUrl]))
