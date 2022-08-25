#!/usr/bin/env python3
# vim: set fileencoding=utf-8 :
# SPDX-License-Identifier: AGPL-3.0-or-later


import requests
import json

from urllib.parse import urlparse, urljoin, urlunparse
from time import sleep
from bs4 import BeautifulSoup

def getUrl(url, verbose=True):
    if (verbose):
        from sys import stderr
        stderr.write(f'... fetching {url}\n')
    return requests.get(url)


def sanitizeCoverUrl(coverUrl):
    return coverUrl.split('?')[0]


def getPrograms(baseUrl):
    response = getUrl(baseUrl)
    soup = BeautifulSoup(response.text, 'html.parser')

    programs = []
    for programLink in soup.find_all('a', class_='podcast__item'):
        programUrl = programLink['href']
        programTitle = programLink.findChild('h3').text
        programCover = sanitizeCoverUrl(programLink.findChild('img')['src'])
        programs.append((programUrl, programTitle, programCover))

    return programs


def getEpisodes(programUrl):
    response = getUrl(programUrl)
    soup = BeautifulSoup(response.text, 'html.parser')

    episodes = []
    episodeButtons = soup.find_all('button', class_='podcast__play ym')
    if not episodeButtons:
        episodeButtons = soup.find_all('button', class_='podcast__play')
    for episodeButton in episodeButtons:
        if not episodeButton.has_attr('data-track'):
            # do not rely on try/except to make errors more visible
            continue
        episodeAudioUrl = episodeButton['data-track']
        episodeTitle = episodeButton['data-track-title']
        episodeCoverUrl = sanitizeCoverUrl(episodeButton['data-track-cover'])
        episodes.append((episodeAudioUrl, episodeTitle, episodeCoverUrl))

    return episodes


if __name__ == '__main__':
    from sys import stdout
    baseUrl = 'https://www.deti.fm/fairy_tales'
    programs = []
    for programUrl, programTitle, programCoverUrl in getPrograms(baseUrl):
        program = {
                'title' : programTitle,
                'cover' : programCoverUrl,
                }
        episodes = []
        # XXX: program order is not stable (?)
        for episodeNum, (episodeAudioUrl, episodeTitle, episodeCoverUrl) in enumerate(reversed(getEpisodes(programUrl))):
            episodes.append({
                'num' : episodeNum + 1,
                'title' : episodeTitle,
                'audioUrl' : episodeAudioUrl,
                'coverUrl' : episodeCoverUrl,
                })
        program['episodes'] = episodes
        programs.append(program)
    stdout.write(json.dumps(programs, ensure_ascii=False))
