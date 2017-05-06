import json
import logging
import urlparse

import requests
from multicorn import ForeignDataWrapper
from multicorn.utils import log_to_postgres

OPERATORS = {
    '=': 'exact',
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
        self._rowid_column = columns.keys()[0]
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

    def log_response(self, response):
        log_to_postgres('Request: {} {} {}'.format(response.request.method,
                                                   response.request.url,
                                                   response.request.body),
                        level=logging.DEBUG)
        log_to_postgres('Response: ' + response.text,
                        level=logging.DEBUG)

    def execute(self, quals, columns):
        params = self.params.copy()
        params.update(self.get_params(quals))
        response = requests.get(self.options['url'],
                                params=params)
        self.log_response(response)
        results = []
        for result in response.json()['results']:
            for attribute, value in result.iteritems():
                if isinstance(value, (dict, list)):
                    result[attribute] = json.dumps(value)
            results.append(result)
        return results

    @property
    def rowid_column(self):
        return self._rowid_column

    def insert(self, new_values):
        data = {key: value
                for key, value in new_values.iteritems()
                if value is not None}
        response = requests.post(self.options['url'],
                                 params=self.params,
                                 json=data)
        self.log_response(response)
        return response.json()

    def update(self, rowid, new_values):
        response = requests.put('{}/{}'.format(self.options['url'], rowid),
                                params=self.params,
                                json=new_values)
        self.log_response(response)
        return response.json()

    def delete(self, rowid):
        response = requests.delete('{}/{}'.format(self.options['url'], rowid),
                                   params=self.params)
        self.log_response(response)
        return response.json()
