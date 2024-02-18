# -*- coding: utf-8 -*-
# Copyright (C) 2023 - Scalizer (<https://www.scalizer.fr>).
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from .logging import get_logger
from s6r_bitwarden_cli import BitwardenCli
from .apps import connection

logger = get_logger("Bitwarden".ljust(20))
CACHE = "/tmp/.configurator_cache"


class Bitwarden:

    def __init__(self, configurator):
        self.configurator = configurator
        self.init_bitwarden_cli()

    def get_bitwarden_params(self):
        bitwarden_params = ['bitwarden_username', 'bitwarden_password', 'bitwarden_session_key']
        return {param: self.configurator.config.get(param) for param in bitwarden_params}

    def init_bitwarden_cli(self):
        params = self.get_bitwarden_params()
        connection.OdooConnection(self.configurator).pre_config(params)
        if params['bitwarden_session_key']:
            self.bw_cli = BitwardenCli()
            if not self.bw_cli.session_key:
                self.bw_cli.session_key = params['bitwarden_session_key']
        elif params['bitwarden_username'] and params['bitwarden_password']:
            self.bw_cli = BitwardenCli(params['bitwarden_username'], params['bitwarden_password'])
        else:
            self.bw_cli = BitwardenCli()

    def get_bitwarden_password(self, collection_name, name, default=''):
        try:
            return self.bw_cli.get_item_password(name, collection_name=collection_name)
        except Exception as err:
            logger.error(err)
            pass
            return default
