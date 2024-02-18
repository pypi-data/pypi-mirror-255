""" This file contains functionality to handle OSIS urls. """

import requests
import json


def get_expedition_event_ids(expedition_id:int):
    """ returns dict {event_name: event_id} """
    ret = {}
    try:
        res = requests.get('https://osis.geomar.de/api/v1/expeditions/' + str(expedition_id) + '/events', timeout=5)
    except requests.exceptions.ConnectionError:
        res = False

    if not res:
        return ret
    
    events = json.loads(res.text)
    for event in events:
        ret[event['name']] = event['id']

    return ret


def get_expedition_ids():
    """ 
    returns dict {cruise_name: cruise_id} of all expeditions. 
    RATHER use get_expedition_id_from_label() if you look for a single
    expeditions id - much faster
    """
    ret = {}
    try:
        res = requests.get('https://osis.geomar.de/api/v1/expeditions', timeout=5)
    except requests.exceptions.ConnectionError:
        res = False    

    if not res:
        return ret
    
    nr_pages = json.loads(res.text)['meta']['total_pages']
    cruises = []
    for i in range(1, nr_pages + 1):
        res = requests.get('https://osis.geomar.de/api/v1/expeditions', params={'page':i}, timeout=5)
        cruises += json.loads(res.text)['data']

    for cruise in cruises:
        ret[cruise['label']] = cruise['id']

    return ret


def get_expedition_id_from_label(label:str):
    """ 
    queries osis for the expedition label and returns its id if exact match was found, 
    otherwise raise ValueError.
    """
    expeditions = get_expeditions_from_from_label(label)
    if len(expeditions) != 1:
        raise ValueError("No exact match found for label: " + label)
    else:
        return expeditions[0]['id']


def get_expeditions_from_from_label(label:str):
    """ queries osis for the expedition label and return list of matches """
    ret = {}
    try:
        res = requests.get('https://osis.geomar.de/api/v1/expeditions',
                           params={'filter':str({'label':label}).replace('\'','"')}, timeout=5)
    except requests.exceptions.ConnectionError:
        res = False    

    if not res:
        return ret
    
    ret = json.loads(res.text)['data']
    return ret


def get_event_url(expedition_id:int,event_id:int):
    """ returns url to osis event """
    return "https://osis.geomar.de/app/expeditions/" + str(expedition_id) + "/events/" + str(event_id)


def get_expedition_url(expedition_id:int):
    """ returns url to osis expedition """
    return "https://osis.geomar.de/app/expeditions/" + str(expedition_id)


def get_expedition_id_from_url(osis_url:str):
    """ returns parsed expedition from url as int. Returns -1 if not successful """
    # e.g. https://osis.geomar.de/app/expeditions/359211/events/1781066
    exp_id = -1
    url_split = osis_url.split("/")
    try:
        exp_id = int(url_split[url_split.index('expeditions') + 1])
    except (ValueError, IndexError):
        pass
    return exp_id