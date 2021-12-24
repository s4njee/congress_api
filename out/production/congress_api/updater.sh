#!/usr/bin/env bash

cd ~/ebs/congress_api/scraper
./run govinfo --bulkdata=BILLSTATUS
./run bills
