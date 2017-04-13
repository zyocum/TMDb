#!/usr/bin/env python3

"""Search TMDb for common credits between cast/crew"""

import os
import json
import requests
import sys
import urllib

from getpass import getpass

KEY = os.environ.get('TMDB_USER_KEY')
BASE_URL = 'https://api.themoviedb.org/3'

def search(facet, query, **params):
    """Query TMDb to find the ID of something"""
    # https://developers.themoviedb.org/3/search
    facets = {
        'company',
        'collection',
        'keyword',
        'movie',
        'multi',
        'person',
        'tv'
    }
    if facet not in facets:
        message = 'invalid facet "{}" (must be one of {})'
        raise ValueError(message.format(facet, sorted(facets)))
    query = urllib.parse.quote_plus(query)
    params['query'] = query
    url = '/'.join([BASE_URL, 'search', facet])
    response = requests.get(url, params=params)
    if response.status_code == 200:
        response = json.loads(response.content.decode(response.encoding))
        if response.get('results'):
            top_result = response['results'][0]
            return {
                'id': top_result['id'],
                'name': top_result['name']
            }
    message = (
        'Error {}: failed to get results for query '
        '"search/{}&query={}"'
    )
    print(message.format(response.status_code, facet, query), file=sys.stderr)

def credits(person_id, **params):
    """Generate a list of combined TV/movie credits for a person ID"""
    # https://developers.themoviedb.org/3/people/get-person-combined-credits
    url = '/'.join([BASE_URL, 'person', str(person_id), 'combined_credits'])
    response = requests.get(url, params=params)
    if response.status_code == 200:
        response = json.loads(response.content.decode(response.encoding))
        for key in 'cast', 'crew':
            for credit in response[key]:
                yield {
                    'title': (credit.get('title') or credit.get('name')),
                    'id': credit['id']
                }
    else:
        message = (
            'Error {}: failed to get credits for person ID '
            '"person/{}/combined_credits"'
        )
        print(message.format(response.status_code, person_id), file=sys.stderr)

def common_credits(*queries, **params):
    """Find the intersection of credits from a list of person queries"""
    persons = {}
    for query in queries:
        person = search('person', query, **params)
        if person:
            person['credits'] = {
                c['title'] for c in credits(person['id'], **params)
            }
            persons[person['id']] = person
    common_credits = set.intersection(
        *(p['credits'] for p in persons.values())
    )
    return {
        'persons': sorted(p['name'] for p in persons.values()),
        'common_credits': sorted(common_credits)
    }

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        'query',
        nargs='+',
        help="Names of persons to query"
    )
    parser.add_argument(
        '-k', '--api-key',
        default=KEY
    )
    args = parser.parse_args()
    key = args.api_key or getpass(prompt='TMDb API key: ')
    print(
        json.dumps(
            common_credits(*args.query, api_key=key),
            ensure_ascii=False,
            indent=4
        )
    )
