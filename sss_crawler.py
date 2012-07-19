#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This program is free software. It comes without any warranty, to
# the extent permitted by applicable law. You can redistribute it
# and/or modify it under the terms of the Do What The Fuck You Want
# To Public License, Version 2, as published by Sam Hocevar. See
# http://sam.zoy.org/wtfpl/COPYING for more details.

import re
import urllib2
import sqlite3
import logging
import signal
import time
from datetime import datetime

from bs4 import BeautifulSoup
from bs4.element import Tag
from apscheduler.scheduler import Scheduler


def send_irc_message(msg):
	try:
		ircservice
	except:
		ircservice = __import__('ircservice')
	ircservice.send_irc_message(msg)

def timestamp_now():
    return int(datetime.now().strftime('%s'))

def parse_time_from_script(script_content):
    return int(script_re.search(script_content).group(1))

def parse_detail_link(link):
    m = link_re.match(link)
    if m is None:
        logging.warn('Invalid link: %s' % (link))
        raise LookupError
    return {'kind': m.group(1), 'id': int(m.group(2))}

def parse_app(app):
    if not isinstance(app, Tag):
        raise TypeError('An argument should be a Tag')
    
    app_link = app.find('a')
    if app_link is None:
        logging.info('There is no link to an app or sub. It seems to be an empty space.')
        raise LookupError
    dc_div = app.find('div', {'class': 'discount'})
    price_span = dc_div.find_all('span')
    
    try:
        ret = dict(parse_detail_link(app_link['href']))
    except LookupError as e:
        raise LookupError(e)
    ret['name'] = app_link['title']
    ret['discount'] = int(dc_div.next_element.strip()[1:-1])
    ret['before_price'] = price_span[0].contents[0].strip()
    ret['now_price'] = price_span[1].contents[0].strip()
    ret['end_date'] = parse_time_from_script(app.script.contents[0])
    return ret

def fetch_flash_sale(apps):
    for app in apps:
        try:
            parsed_app = parse_app(app)
        except LookupError as e:
            continue
    
        cur.execute('SELECT COUNT(id) FROM flash_sale WHERE id = ?', (parsed_app['id'], ))
        if cur.fetchone()[0] > 0:
            logging.info('%d is already registered.' % (parsed_app['id']))
            continue
    
        logging.info('Newly registering app id %d.' % (parsed_app['id']))
        end_datetime = datetime.fromtimestamp(parsed_app['end_date'])
        send_irc_message(u'[Steam] 새로운 깜짝 할인: %(name)s %(before_price)s -%(discount)d%%-> %(now_price)s http://store.steampowered.com/%(kind)s/%(id)d/' % (parsed_app) + u' %d일 %d시 %d분까지' % (end_datetime.day, end_datetime.hour, end_datetime.minute))
        cur.execute('INSERT INTO flash_sale VALUES (:id, :kind, :name, :discount, :before_price, :now_price, :end_date)', parsed_app)
    
    conn.commit()

def fetch_vote_candidates(vote_form):
    vote_id = int(vote_form.input['value'])
    cur.execute('SELECT COUNT(id) FROM vote_candidates WHERE id = ?', (vote_id, ))
    if cur.fetchone()[0] > 0:
        return
    
    candidates = []
    for vote_option in vote_form.find(id='ss_voteoptions').find_all(attrs={'class': 'option'}):
        candidates.append(vote_option.find('div', {'class': 'info'}).a['title'])
    
    end_date = datetime.fromtimestamp(parse_time_from_script(vote_form.script.contents[0]))
    result = ', '.join(candidates)
    cur.execute('INSERT INTO vote_candidates VALUES (?, ?)', (vote_id, result, ))
    send_irc_message(u'[Steam] 새로운 투표 후보들: %s http://store.steampowered.com/ %d일 %d시 %d분까지'
                        % (result, end_date.day, end_date.hour, end_date.minute))
    conn.commit()

def fetch_vote_results(result_div):
    cur.execute('SELECT last_timestamp FROM vote_results ORDER BY last_timestamp DESC LIMIT 0, 1')
    last_timestamp = cur.fetchone()
    if last_timestamp is not None and last_timestamp[0] >= timestamp_now() - 2400:
        return
    
    options = result_div.find_all('div', recursive=False, limit=3)
    result = []
    for option in options:
        item = dict()
        item['votes'] = int(option.find('div', {'class': 'votes'}).contents[0].strip()[:-1])
        item['name'] = option.find('div', {'class': 'info'}).a['title']
        result.append(item)
    result = ['%(name)s (%(votes)d%%)' % x for x in sorted(result, lambda x, y: y['votes'] - x['votes'])]
    
    end_date = datetime.fromtimestamp(parse_time_from_script(result_div.script.contents[0]))
    result_str = ', '.join(result)
    send_irc_message(u'[Steam] 투표 결과: %s http://store.steampowered.com/ 할인은 %d시 %d분부터 시작'
                        % (result_str, end_date.hour, end_date.minute))
    cur.execute('INSERT INTO vote_results VALUES (?, ?)', (timestamp_now(), result_str))
    conn.commit()

def fetch_community_choice(topvote_div, script):
    app = dict(parse_detail_link(topvote_div.a['href']))
    cur.execute('SELECT COUNT(id) FROM community_choice WHERE id = ?', (app['id'], ))
    if cur.fetchone()[0] > 0:
        return
    
    dc_div = topvote_div.find('div', {'class': 'discount'})
    price_span = dc_div.find_all('span')
    
    app['name'] = topvote_div.a['title']
    app['discount'] = int(dc_div.next_element.strip()[1:-1])
    app['before_price'] = price_span[0].contents[0].strip()
    app['now_price'] = price_span[1].contents[0].strip()
    app['end_date'] = parse_time_from_script(script.contents[0])
    end_datetime = datetime.fromtimestamp(app['end_date'])
    send_irc_message(u'[Steam] 새로운 커뮤니티 선택 할인: %(name)s %(before_price)s -%(discount)d%%-> %(now_price)s http://store.steampowered.com/%(kind)s/%(id)d/' % (app) + u' %d일 %d시 %d분까지' % (end_datetime.day, end_datetime.hour, end_datetime.minute))
    cur.execute('INSERT INTO community_choice VALUES (:id, :kind, :name, :discount, :before_price, :now_price, :end_date)', app)
    conn.commit()

def do_job():
    print 'crawling..'
    try:
        f = urllib2.urlopen('http://store.steampowered.com/?cc=us')
    except urllib2.URLError as e:
        logging.warn(e)
        return
    content = f.read()
    soup = BeautifulSoup(content, 'lxml')
    
    fetch_flash_sale(soup.find(id='ss_flash').find_all(attrs={'class': 'app'}))
    topvoted_div = soup.find(id='ss_topvoted')
    fetch_community_choice(topvoted_div, topvoted_div.parent.script)
    vote_options = soup.find(id='ss_voteoptions')
    if vote_options is not None:
        fetch_vote_candidates(vote_options.parent)
    vote_results = soup.find(id='ss_voteresults')
    if vote_results is not None:
        fetch_vote_results(vote_results)


def init_crawler():
	global link_re, script_re, conn, cur, sched, first_run
	conn = sqlite3.connect('steam_summer_sale.db', check_same_thread=False)
	cur = conn.cursor()
	sql_f = open('schema.sql')
	cur.executescript(sql_f.read())


	script_re = re.compile("InitDailyDealTimer\( \$\('\w+'\), ([0-9]+) \);")
	link_re = re.compile('http:\/\/store\.steampowered\.com\/(app|sub)\/([0-9]+)')

	sched = Scheduler()
	sched.add_interval_job(do_job, minutes=2)
	try:
	    first_run = True
	    do_job()
	    first_run = False
	    sched.start()
	    while True:
                time.sleep(300)
	except:
	    sched.shutdown()
	    conn.close()

