import datetime as dt
from collections import ChainMap
from copy import deepcopy

from toolz import thread_last, dissoc


class Projection:
    _full = {
        '_id': 0,
        'title': 1,
        'author': 1,
        'body': 1,
        'permlink': 1,
        'identifier': 1,
        'created': 1,
        'pending_payout_value': 1,
        'total_payout_value': 1,
        'net_votes': 1,
        'net_rshares': 1,
        'author_reputation': 1,
        'json_metadata': 1,
        'tags': 1,
    }

    _light = dissoc(_full, 'body')

    @staticmethod
    def full():
        return deepcopy(Projection._full)

    @staticmethod
    def light():
        return deepcopy(Projection._light)


def despam_results(results):
    """ Remove spammy looking posts. """

    def _filters(result):
        # do not remove this filter, the app requires it
        if not result.get('json_metadata') or type(result['json_metadata']) != dict:
            return False

        # filter out spam and unloved posts
        if len(result['json_metadata'].get('links', [])) > 15:
            return False
        if len(result['json_metadata'].get('users', [])) > 10:
            return False

        # filter out nsfw stuff
        tags = result['json_metadata'].get('tags', [])
        if len(set(tags) & {'nsfw', 'porn', 'fuck', 'sex'}) > 0:
            return False

        # detect if post was flagged down
        if int(result.get('net_rshares', 0)) < 0:
            return False

        # todo add more filters
        return True

    def _clean_body(result):
        # todo sanitize non https links
        if result.get('body'):
            result['body'] = result['body'].replace('steemitboard.com', 'localhost')
        return result

    return thread_last(
        results,
        (filter, _filters),
        (map, _clean_body),
        list
    )


def route(mongo, query):
    conditions = dict()
    if query.startswith('@'):
        account = query.strip('@').split('/')[0]
        conditions['author'] = account
        results = perform_query(mongo, conditions=conditions)
    else:
        results = perform_query(mongo, search=query)

    return results


def perform_query(mongo, conditions=None, search=None, sort_by='new', options=None):
    """ Run a query against SteemQ Posts. """
    # apply conditions, such as time constraints
    conditions = conditions or {}
    conditions['created'] = {
        '$gte': dt.datetime.now() - dt.timedelta(days=90),
    }
    query = {
        **conditions,
    }
    projection = Projection.full()

    sorting = []
    if sort_by == 'new':
        sorting = [('created', -1)]
    elif sort_by == 'payout':
        sorting = [
            ('pending_payout_value.amount', -1),
            ('total_payout_value.amount', -1),
        ]
    elif sort_by == 'votes':
        sorting = [('net_votes', -1)]

    if search:
        query['$text'] = {'$search': search}
        projection['score'] = {'$meta': 'textScore'}
        sorting.insert(0, ('score', {'$meta': 'textScore'}))

    options = options or {}
    default_options = {
        'limit': 100,
        'skip': 0,
    }
    options = ChainMap(options, default_options)

    return list(mongo.db['Posts'].find(
        filter=query,
        projection=projection,
        sort=sorting,
        limit=options.get('limit'),
        skip=options.get('skip'),
    ))
