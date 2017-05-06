import json
import logging
import urlparse

import requests
from multicorn import ForeignDataWrapper
from multicorn.utils import log_to_postgres

OPERATORS = {
    '=': 'eq',
    '<': 'lt',
    '>': 'gt',
    '<=': 'le',
    '>=': 'ge',
    '<>': 'ne',
    '~~': 'exact',
    '~~*': 'iexact',
    '!~~*': 'notiexact',
    '!~~': 'notexact',
    ('=', True): 'in',
    ('<>', False): 'notin'
}


class FalconApiFDW(ForeignDataWrapper):
    def __init__(self, options, columns):
        super(FalconApiFDW, self).__init__(options, columns)
        self.columns = columns
        self.options = options
        self.params = {}
        if 'params' in self.options:
            self.params = urlparse.parse_qs(self.options['params'])
        if 'url' not in self.options:
            log_to_postgres('Falcon API FDW: url option is required',
                            level=logging.ERROR,
                            hint='Try adding the missing option in the table '
                                 'creation statement')

    def get_params(self, quals):
        params = {}
        for qual in quals:
            op = OPERATORS.get(qual.operator, None)
            if op is None:
                # skip unknown ops as PostgreSQL will apply them anyway
                continue
            params['{}__{}'.format(qual.field_name, op)] = qual.value
        return params

    def execute(self, quals, columns):
        params = self.params.copy()
        params.update(self.get_params(quals))
        response = requests.get(self.options['url'],
                                params=params)
        log_to_postgres('Request: {} {} {}'.format(response.request.method,
                                                   response.request.url,
                                                   response.request.body),
                        level=logging.DEBUG)
        log_to_postgres('Response: ' + response.text,
                        level=logging.DEBUG)
        results = []
        for result in response.json()['results']:
            for attribute, value in result.iteritems():
                if isinstance(value, (dict, list)):
                    result[attribute] = json.dumps(value)
            results.append(result)
        return results

    def insert(self, new_values):
        response = requests.post(self.options['url'],
                                 params=self.params,
                                 data=new_values)
        return response.json()

    def update(self, old_values, new_values):
        pk = new_values.pop('id')
        response = requests.put('{}/{}'.format(self.options['url'], pk),
                                params=self.params,
                                data=new_values)
        return response.json()

    def delete(self, old_values):
        pk = old_values.pop('id')
        response = requests.delete('{}/{}'.format(self.options['url'], pk),
                                   params=self.params)
        return response.json()
