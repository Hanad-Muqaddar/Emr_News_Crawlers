#!/bin/sh
# go to the spider directory
cd /home/emr/TestingDir/SonePar_News_Crawler/SonePar
PATH = $PATH: /home/emr/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/snap/bin
export PATH
# run the spider
scrapy crawl SonePar_Crawler