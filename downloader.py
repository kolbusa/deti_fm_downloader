#!/usr/bin/env python3
# vim: set fileencoding=utf-8 :
# SPDX-License-Identifier: AGPL-3.0-or-later

from time import sleep
import os
import os.path
import json
import requests
import eyed3

def getUrl(url, verbose=False):
    if (verbose):
        from sys import stderr
        stderr.write(f'... fetching {url}\n')
    return requests.get(url)


def getUrlFileName(url):
    urlFileName = url.split('/')[-1]
    return urlFileName


def getUrlFileExt(url):
    urlFileName = getUrlFileName(url)
    ext = os.path.splitext(urlFileName)[-1]
    return ext


def saveFile(url, fileName):
    response = getUrl(url)
    with open(fileName, 'wb+') as f:
        f.write(response.content)


def sanitizeFileName(fileName):
    fileName = fileName.replace(os.path.sep, '-')
    baseName, ext = os.path.splitext(fileName)
    maxLen = 250
    while len(bytes(fileName, 'utf-8')) > maxLen:
        baseName = baseName[:-1]
        fileName = baseName + ext
    return fileName


def downloadPrograms(programs):
    newPrograms = []
    for program in programs:
        programTitle, coverUrl, programEpisodes = program['title'], program['cover'], program['episodes']
        try:
            programTitle = sanitizeFileName(programTitle)
            os.mkdir(programTitle)
        except FileExistsError:
            pass
        except Exception as e:
            print(f'Could not mkdir \'{programTitle}\': {e}')
            continue
        coverExt = getUrlFileExt(coverUrl)
        coverFileName = f'{programTitle}/cover{coverExt}'
        if not os.path.isfile(coverFileName):
            try:
                saveFile(coverUrl + '?w=640&h=480&q=100', coverFileName)
            except Exception as e:
                print(f'Could not save \'{coverFileName}\': {e}')
                # Something went wrong
                continue
        for episode in programEpisodes:
            episodeNum, episodeTitle, episodeAudioUrl, episodeCoverUrl = \
                    episode['num'], episode['title'], episode['audioUrl'], episode['coverUrl']
            audioExt = getUrlFileExt(episodeAudioUrl)
            audioFileName = os.path.join(programTitle, sanitizeFileName(f'{episodeNum} - {episodeTitle}{audioExt}'))
            if os.path.isfile(audioFileName):
                continue

            newPrograms.append(audioFileName)
            try:
                saveFile(episodeAudioUrl, audioFileName)
            except Exception as e:
                # Something went wrong
                print(f'Could not save \'{audioFileName}\': {e}')
                continue
            if audioExt == '.mp3':
                mp3 = eyed3.load(audioFileName)
                mp3.initTag()
                mp3.tag.artist = 'deti.fm'
                mp3.tag.recording_date = 2021
                mp3.tag.album = programTitle
                mp3.tag.track_num = episodeNum
                mp3.tag.title = episodeTitle

                coverFileName = getUrlFileName(episodeCoverUrl)
                coverFileExt = getUrlFileExt(episodeCoverUrl)
                r = getUrl(episodeCoverUrl + '?w=640&h=480&q=100')
                mp3.tag.images.set(3, r.content, r.headers['Content-Type'])

                mp3.tag.save()
            sleep(1)
    return newPrograms


if __name__ == '__main__':
    import sys
    programs = json.load(sys.stdin)
    newPrograms = downloadPrograms(programs)
    if len(newPrograms):
        print('New programs:')
        for newProgram in newPrograms:
            print(f'{newProgram}')
    else:
        print('No new programs')
