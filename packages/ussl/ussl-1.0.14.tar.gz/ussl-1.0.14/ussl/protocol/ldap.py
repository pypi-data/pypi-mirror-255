from typing import Optional

import ldap
from ldap.ldapobject import LDAPObject

from ..model import Protocol, Response, Query
from .base import BaseProtocol
from ..exceptions import CredentialsError, ConnectionFailed, ExecutionError


class LDAPProtocol(BaseProtocol):
    name = 'ldap'

    def __init__(self):
        self.base: Optional[str] = None
        self.con: Optional[LDAPObject] = None

    def connect(self, protocol: Protocol) -> LDAPObject:
        server = f'ldap://{protocol.host}'
        ldap_login = f'{protocol.username}@{protocol.domain}'
        self.base = ', '.join(f'dc={i}' for i in protocol.domain.split('.'))
        try:
            self.con = ldap.initialize(server, bytes_mode=False)
            self.con.protocol_version = ldap.VERSION3
            self.con.set_option(ldap.OPT_REFERRALS, 0)
            self.con.simple_bind_s(ldap_login, protocol.password)
            return self.con
        except ldap.INVALID_CREDENTIALS as e:
            raise CredentialsError(str(e))
        except ldap.SERVER_DOWN as e:
            raise ConnectionFailed(str(e))
        except Exception as e:
            raise ExecutionError(str(e))

    def close(self) -> None:
        try:
            self.con.unbind()
        except Exception as e:
            raise ExecutionError("Неожиданная ошибка при отключении")
        self.con = None

    def execute(self, query: Query) -> Response:
        pass