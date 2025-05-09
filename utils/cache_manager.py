#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module de gestion du cache pour les résultats intermédiaires.
"""

import logging
import os
import pickle
import time
import hashlib
from pathlib import Path

logger = logging.getLogger(__name__)

class CacheManager:
    """Gère la mise en cache et la récupération des données sur disque."""

    def __init__(self, config):
        """
        Initialise le gestionnaire de cache.

        Args:
            config (dict): Dictionnaire de configuration.
        """
        self.config = config
        self.cache_dir = Path(config.get("cache_dir", "cache"))
        self.cache_ttl = config.get("cache_ttl", 3600 * 24) # Default: 24 hours
        self.enabled = config.get("cache_enabled", True)

        if self.enabled:
            os.makedirs(self.cache_dir, exist_ok=True)
            logger.info(f"Cache enabled. Directory: {self.cache_dir}, TTL: {self.cache_ttl}s")
        else:
            logger.info("Cache is disabled.")

    def _get_cache_key(self, *args, **kwargs):
        """ Crée une clé de cache unique basée sur les arguments. """
        # Combine args and sorted kwargs items for deterministic key
        key_data = (args, sorted(kwargs.items()))
        # Use pickle to serialize complex objects, then hash
        serialized_data = pickle.dumps(key_data)
        return hashlib.sha256(serialized_data).hexdigest()

    def _get_cache_filepath(self, key):
         """ Retourne le chemin complet du fichier de cache. """
         return self.cache_dir / f"{key}.pkl"

    def get(self, key):
        """
        Récupère une donnée depuis le cache si elle existe et est valide.

        Args:
            key (str): Clé de cache.

        Returns:
            object or None: La donnée en cache ou None si non trouvée ou expirée.
        """
        if not self.enabled:
            return None

        filepath = self._get_cache_filepath(key)
        if filepath.exists():
            try:
                file_mod_time = filepath.stat().st_mtime
                if time.time() - file_mod_time < self.cache_ttl:
                    with open(filepath, 'rb') as f:
                        data = pickle.load(f)
                    logger.debug(f"Cache hit for key: {key}")
                    return data
                else:
                    logger.debug(f"Cache expired for key: {key}. Removing file.")
                    os.remove(filepath)
            except Exception as e:
                logger.warning(f"Error reading cache file {filepath} for key {key}: {e}. Removing file.")
                try:
                    os.remove(filepath)
                except OSError:
                    pass # Ignore error if file removal fails
        else:
             logger.debug(f"Cache miss for key: {key}")

        return None

    def set(self, key, data):
        """
        Met en cache une donnée.

        Args:
            key (str): Clé de cache.
            data (object): Donnée à mettre en cache.
        """
        if not self.enabled:
            return

        filepath = self._get_cache_filepath(key)
        try:
            with open(filepath, 'wb') as f:
                pickle.dump(data, f)
            logger.debug(f"Data cached for key: {key}")
        except Exception as e:
            logger.error(f"Error writing cache file {filepath} for key {key}: {e}")

    def generate_key(self, *args, **kwargs):
         """ Génère une clé de cache à partir d'arguments variés. """
         return self._get_cache_key(*args, **kwargs)

    def clear(self):
        """ Vide l'ensemble du cache. """
        if not self.enabled:
             logger.warning("Cache is disabled, cannot clear.")
             return
        try:
             count = 0
             for item in self.cache_dir.iterdir():
                 if item.is_file() and item.suffix == '.pkl':
                     os.remove(item)
                     count += 1
             logger.info(f"Cache cleared. Removed {count} items from {self.cache_dir}.")
        except Exception as e:
             logger.error(f"Error clearing cache directory {self.cache_dir}: {e}")

# Example Usage:
# config = {"cache_dir": "./my_cache", "cache_enabled": True, "cache_ttl": 60}
# cache_manager = CacheManager(config)
#
# my_key = cache_manager.generate_key("user_data", user_id=123, params={"a": 1, "b": 2})
# cached_data = cache_manager.get(my_key)
#
# if cached_data is None:
#     print("Cache miss, fetching data...")
#     new_data = {"name": "Alice", "value": 42}
#     cache_manager.set(my_key, new_data)
# else:
#     print(f"Cache hit: {cached_data}")
#
# # Clear cache after use (optional)
# # cache_manager.clear() 