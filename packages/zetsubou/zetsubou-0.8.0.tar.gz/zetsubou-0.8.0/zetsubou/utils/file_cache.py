from datetime import datetime
from typing import Dict
from fs.base import FS
from fs.errors import ResourceNotFound


FILE_CACHE_PATH = 'build/files.cache'
FILE_CACHE_PREFIX_SYMBOL = ' @ '


class FileCache:
    _entries : Dict[str, datetime] = {}
    _fs : FS
    _stale : bool

    def get_modified_time(self, filename:str) -> datetime:
        return self._fs.getinfo(filename, ['details']).modified

    # Checks if file is present in cache at all
    def is_cached(self, filename:str) -> bool:
        return filename in self._entries

    # Checks if timestamp/hash changed
    def is_fresh(self, filename:str) -> bool:
        if filename not in self._entries:
            return False
        if not self._fs.exists(filename):
            return False
        return self._entries[filename] == self.get_modified_time(filename)

    # Adds new file to cache
    def add_file(self, filename):
        if isinstance(filename, bytes):
            filename = filename.decode('utf-8')

        self._entries[filename] = self.get_modified_time(filename)

    def is_stale(self):
        return self._stale

    # Loads the cache. Returns true if cache is fresh.
    def load(self, fs : FS) -> bool:
        self._fs = fs

        if not self._fs.exists(FILE_CACHE_PATH):
            self._stale = True
            return False

        self._stale = False

        with self._fs.open(FILE_CACHE_PATH, 'r', encoding='utf-8') as f_cache:
            for line in f_cache.readlines():
                filename_part, timestamp_part = line.split(FILE_CACHE_PREFIX_SYMBOL)
                filename = filename_part.strip()
                timestamp = datetime.fromisoformat(timestamp_part.strip())

                self._entries[filename] = timestamp
                try:
                    if timestamp != self.get_modified_time(filename):
                        self._stale = True
                except ResourceNotFound as err:
                    self._stale = True

        return not self._stale

    # Saves the cache to a file
    def save(self):
        with self._fs.open(FILE_CACHE_PATH, 'w', encoding='utf-8') as f_cache:
            for filename, timestamp in self._entries.items():
                f_cache.write(f'{filename}{FILE_CACHE_PREFIX_SYMBOL}{timestamp}\n')
