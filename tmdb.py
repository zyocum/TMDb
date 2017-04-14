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
    status_code = response.status_code
    if status_code == 200:
        encoding = response.encoding or 'utf-8'
        try:
            response = json.loads(response.content.decode(encoding))
            if response.get('results'):
                top_result = response['results'][0]
                return {
                    'id': top_result['id'],
                    'name': top_result['name']
                }
        except Exception as e:
            print(e, file=sys.stderr)
            print(response.content.decode(encoding), file=sys.stderr)
    else:
        message = '\n'.join([
            'Error {}: failed to get results for query',
            'URL: {}',
            'parameters: {}'
        ])
        print(message.format(status_code, url, params), file=sys.stderr)

def credits(person_id, **params):
    """Generate a list of combined TV/movie credits for a person ID"""
    # https://developers.themoviedb.org/3/people/get-person-combined-credits
    url = '/'.join([BASE_URL, 'person', str(person_id), 'combined_credits'])
    response = requests.get(url, params=params)
    status_code = response.status_code
    if status_code == 200:
        encoding = response.encoding
        try:
            response = json.loads(response.content.decode(encoding))
            for key in 'cast', 'crew':
                for credit in response[key]:
                    yield {
                        'title': (credit.get('title') or credit.get('name')),
                        'id': credit['id']
                    }
        except Exception as e:
            print(e, file=sys.stderr)
            print(response.content.decode(encoding), file=sys.stderr)
    else:
        message = '\n'.join([
            'Error {}: failed to get credits for person ID'
            'URL: {}',
            'parameters: {}'
        ])
        print(message.format(status_code, url, params), file=sys.stderr)

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
    if persons:
        common_credits = set.intersection(
            *(p['credits'] for p in persons.values())
        )
        return {
            'persons': sorted(p['name'] for p in persons.values()),
            'common_credits': sorted(common_credits)
        }
    else:
        message = "No persons found for names: {}"
        print(
            message.format('"{}"'.format('", "'.join(queries))),
            file=sys.stderr
        )

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
