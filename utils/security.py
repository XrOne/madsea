#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module pour la gestion sécurisée des informations sensibles (clés API, etc.).
"""

import logging
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

logger = logging.getLogger(__name__)

class SecurityManager:
    """Gère le chiffrement et le déchiffrement des données sensibles."""

    def __init__(self, config):
        """
        Initialise le gestionnaire de sécurité.

        Args:
            config (dict): Dictionnaire de configuration.
                         Doit contenir 'encryption_key_path' ou 'master_password'.
        """
        self.config = config
        self.fernet = self._get_fernet_instance()

    def _derive_key(self, password, salt):
        """ Dérive une clé de chiffrement à partir d'un mot de passe et d'un sel. """
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=480000, # Recommandé par OWASP (en 2023)
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key

    def _get_fernet_instance(self):
        """ Récupère ou génère la clé de chiffrement et initialise Fernet. """
        key_path = self.config.get("encryption_key_path", "./.encryption_key")
        master_password = self.config.get("master_password")
        salt_path = key_path + ".salt"

        key = None
        if os.path.exists(key_path):
            try:
                with open(key_path, 'rb') as f:
                    key = f.read()
                logger.info(f"Loaded encryption key from {key_path}")
            except Exception as e:
                 logger.error(f"Failed to load encryption key from {key_path}: {e}")
                 raise
        elif master_password:
             logger.info("Deriving encryption key from master password.")
             if os.path.exists(salt_path):
                 with open(salt_path, 'rb') as f:
                     salt = f.read()
             else:
                 salt = os.urandom(16)
                 try:
                     with open(salt_path, 'wb') as f:
                         f.write(salt)
                     logger.info(f"Generated and saved salt to {salt_path}")
                 except Exception as e:
                     logger.error(f"Failed to save salt file {salt_path}: {e}")
                     # Continue without saving salt, less secure if password changes

             key = self._derive_key(master_password, salt)
             # Optionnel: Sauvegarder la clé dérivée pour éviter de la redériver à chaque fois?
             # C'est un compromis sécurité vs performance.
             # Pour l'instant, on la dérive à chaque initialisation si basée sur mdp.
        else:
            logger.warning(f"No encryption key file found at {key_path} and no master_password provided. Generating a new key.")
            key = Fernet.generate_key()
            try:
                with open(key_path, 'wb') as f:
                    f.write(key)
                logger.info(f"Generated and saved new encryption key to {key_path}")
            except Exception as e:
                logger.error(f"Failed to save new encryption key to {key_path}: {e}. Encryption might not persist.")

        if not key:
             logger.critical("Could not load or generate an encryption key. SecurityManager cannot operate.")
             raise ValueError("Encryption key is missing or invalid.")

        return Fernet(key)

    def encrypt(self, data):
        """
        Chiffre les données (doivent être en bytes).

        Args:
            data (bytes): Les données à chiffrer.

        Returns:
            bytes: Les données chiffrées.
        """
        if not isinstance(data, bytes):
            raise TypeError("Data to encrypt must be bytes")
        if not self.fernet:
             logger.error("Encryption engine not initialized.")
             return None # Ou lever une exception?
        try:
             return self.fernet.encrypt(data)
        except Exception as e:
             logger.error(f"Encryption failed: {e}")
             return None

    def decrypt(self, encrypted_data):
        """
        Déchiffre les données.

        Args:
            encrypted_data (bytes): Les données chiffrées.

        Returns:
            bytes: Les données déchiffrées, ou None en cas d'erreur (ex: clé incorrecte, données corrompues).
        """
        if not isinstance(encrypted_data, bytes):
             raise TypeError("Data to decrypt must be bytes")
        if not self.fernet:
             logger.error("Decryption engine not initialized.")
             return None
        try:
            return self.fernet.decrypt(encrypted_data)
        except Exception as e: # cryptography.fernet.InvalidToken is common here
            logger.error(f"Decryption failed: {e}. Invalid key or corrupted data?")
            return None

    def encrypt_string(self, text):
        """ Chiffre une chaîne de caractères (UTF-8). """
        if not isinstance(text, str):
            raise TypeError("Input must be a string")
        encrypted_bytes = self.encrypt(text.encode('utf-8'))
        # Retourner en base64 pour faciliter le stockage/affichage
        return base64.urlsafe_b64encode(encrypted_bytes).decode('utf-8') if encrypted_bytes else None

    def decrypt_string(self, encrypted_text):
         """ Déchiffre une chaîne de caractères (encodée en base64). """
         if not isinstance(encrypted_text, str):
             raise TypeError("Input must be a base64 encoded string")
         try:
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_text.encode('utf-8'))
            decrypted_bytes = self.decrypt(encrypted_bytes)
            return decrypted_bytes.decode('utf-8') if decrypted_bytes else None
         except Exception as e:
             logger.error(f"String decryption failed: {e}")
             return None

# Example Usage:
# config = {"master_password": "mysecretpassword"} # Or {"encryption_key_path": "./mykey"}
# security_manager = SecurityManager(config)
#
# api_key = "sk-1234567890abcdef"
# encrypted_key_str = security_manager.encrypt_string(api_key)
# print(f"Encrypted: {encrypted_key_str}")
#
# decrypted_key = security_manager.decrypt_string(encrypted_key_str)
# print(f"Decrypted: {decrypted_key}")
#
# assert api_key == decrypted_key 