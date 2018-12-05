# -*- coding: utf-8 -*-
"""Provider module"""

import os
import requests
import gzip
import json


class Provider:
    """Provider base class.

    Base for handling common provider operations.

    Provider types:
    1. Local provider - Work with locally existing url file.
       example: Provider('provider_name', 'path/to/file.txt')

    2. Custom provider - Work with external source.
       example:

       class CustomProvider(Provider):

        def __init__(self):
            Provider.__init__(self,
                              'provider_name',
                              'path/to/file.txt',
                               url='http://source.url')
        def download(self):
            requests.get(self.url)
            <your impl>

        * url is required for update method. (see Provider.update)
        * see Provider.download for implementation notes.

    Lazy provider.
    By default a created provider is LAZY provider, data file will
    be accessed at runtime. By initiating a provider with
    Provider(... ,lazy=False) provider's data will be loaded to memory.

    """

    def __init__(self, name, file_path, url=None, lazy=True):
        self.name = name
        self.file_path = file_path
        self.url = url
        self.lazy = lazy
        self.data = None
        self._errors = []

    def flush_errors(self):
        """Clean and return existing provider errors."""

        errors = self._errors
        self._errors = []
        return errors

    def load(self):
        """Provider data controller.

        Automated method to run download (see Provider.download) when
        local data source is not found. eventually, data will be loaded
        to memory if Provider.lazy is set to true.
        """
        try:
            open(self.file_path).close()
        except IOError:
            if self.url:
                path, file = os.path.split(self.file_path)
                if not os.path.exists(path):
                    os.makedirs(path)
                self._run_download()
        if not self.lazy:
            with open(self.file_path) as f:
                self.data = f.read().splitlines()

    def _run_download(self):
        """Catch exceptions caused by external download implementation."""

        try:
            self.download()
        except:
            self._errors.append('{} - Error'.format(self.name))

    def download(self):
        """
        To be implemented by provider creator.

        Implementation note:
        To ensure smooth operation of the provider, a custom download
        method is required to create a TXT file to Provider.file_path.
        In this case a TXT file is a new-line separated URL list.

        example:
        def download(self):
            response = requests.get(self.url)
            with open(self.file_path, 'w') as out:
                out.write(response.text)
        """
        raise NotImplementedError('method download not implemented')

    def has_url(self, value):
        """Check for value existence in provider data."""

        if not self.data:
            with open(self.file_path) as f:
                return value in f.read().splitlines()
        return value in self.data

    def update(self):
        """Provider data update."""

        if self.url:
            self._run_download()


class OpenPhish(Provider):
    """Custom provider - openphish.com."""

    def __init__(self):
        Provider.__init__(self,
                          'openphish.com',
                          'data/openphish.txt',
                          url='https://openphish.com/feed.txt')

    def download(self):
        response = requests.get(self.url)
        response.raise_for_status()
        with open(self.file_path, 'w') as out:
            out.write(response.text)


class PhishTank(Provider):
    """Custom provider - phishtank.com."""

    def __init__(self):
        Provider.__init__(self,
                          'phishtank.com',
                          'data/phishtank.txt',
                          url='http://data.phishtank.com/data/online-valid.json.gz')

    def download(self):
        """Custom provider download

        POOR PERFORMANCE WITH PYTHON 2 !!!
        * takes up about 1.6 G memory compared to about 400 M with Python3
        """
        temp_file = 'temp_phishtank'
        response = requests.get(self.url, stream=True)
        response.raise_for_status()
        with open(temp_file, "wb") as handle:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    handle.write(chunk)
        unpacked = gzip.open(temp_file)
        json_data = json.loads(unpacked.read())
        with open(self.file_path, 'w') as output:
            for entry in json_data:
                try:
                    output.write(entry['url'] + '\n')
                except:
                    # todo - UnicodeEncodeError: 'ascii' codec can't encode character (py2)
                    pass
        os.remove(temp_file)
