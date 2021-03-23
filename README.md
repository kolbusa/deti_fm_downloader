# Deti.fm downloader

These scripts crawl and download podcasts/audiobooks/radio plays (programs) from [Children's Radio](https://deti.fm)
which is broadcasting in Russian language and has a vast archive of programs.

# How to use

First, install all dependencies (best done using a virtual environment):

```sh
pip3 install -r requirements.txt
```

Then, create the list of all programs:

```sh
./crawler.py > programs.json
```

Finally, download the programs:

```sh
./downloader.py < programs.json
```

The last command will download the programs into the current directory. It will create the following directory
structure:
```
.
└── Program name
    ├── 1 - Episode name.mp3
    ├── 2 - Episode name.mp3
    ├── ...
    └── cover.jpg
```

The `downloader.py` will also try to set mp3 tags according to the metadata in the `programs.json` including cover art.

# Features and limitations

* There is no support for incremental downloads or for downloading updated content only.

* Both the `downloader.py` and `crawler.py` try to sleep at least for 1 second between requests to not overload the
  server.

# Keywords in Russian for search engines

Скрипты для скачивания программ с [Детского Радио](https://deti.fm).
