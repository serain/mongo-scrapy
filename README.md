# Mongo-Scrapy

## Description

Crawl and dirbust a list of URLs and store it all in a MongoDB, parsing out headers and cookies.

## Use cases

This may work for you if you're trying to answer questions like which websites:

* have a certain header
* set a cookie name/value
* present default pages, like default index pages or directory listings
* have pages containing any regexes you're after

## Limitations

* Dirbust signature based on body MD5 hash, this naturally isn't foolproof and leads to dirbust "loops" or "storms" on some websites
* Won't work on modern frameworks that rely heavily on JavaScript for navigation, will support Splash in the future
* Database modelling is hacky

## Setup

You'll need a MongoDB accessible to the scraper:

```terminal
$ docker run --name mongo-test -p 127.0.0.1:27017:27017 mongo:latest
...
```

Clone the repo:

```terminal
$ git clone https://github.com/serain/mongo-scrapy.git
...
```

## Usage

```terminal
$ cd mongo-scrapy
$ pipenv install
$ pipenv run python run.py -iL /tmp/list --dirbust-list /tmp/dict --depth 4 --mongo-host 127.0.0.1
...
```

You can omit the `--dirbust-list` argument if you don't want to dirbust.

## Database

By default, all crawled pages will be stored on the `crawler` database, in the `pages` collection. A random record looks like:

```terminal
$ mongo crawler
> db.pages.find().limit(1)
{
  "_id": ObjectId("5bcf97684f4ab8744ee5d531"),
  "url": "http://testphp.vulnweb.com/guestbook.php",
  "base_url": "http://testphp.vulnweb.com/",
  "previous_page_id": ObjectId("5bcf97684f4ab8744ee5d52f"),
  "path": "/guestbook.php",
  "query": "",
  "status": 200,
  "headers": [
    {
      "name": "server",
      "value": "nginx/1.4.1"
    },
    {
      "name": "date",
      "value": "Tue, 23 Jun 1970 06:45:39 GMT"
    },
    {
      "name": "content-type",
      "value": "text/html"
    },
    {
      "name": "x-powered-by",
      "value": "PHP/5.3.10-1~lucid+2uwsgi2"
    }
  ],
  "cookies": [
    {
      "name": "sessionid",
      "value": "dc9f9c37e4b270e3e6129a7dd2ca166"
    }
  ],
  "body": "<!DOCTYPE HTML PUBLIC>..."
}
```
