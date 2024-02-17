from .ldap import LDAPProtocol
from .winrm import WinRMProtocol
from .ssh import SSHProtocol


INTERFACES = {
    'ssh': SSHProtocol,
    # 'winexe': WinexeProtocol,
    # 'wmi': WMIProtocol,
    'winrm': WinRMProtocol,
    'ldap': LDAPProtocol,
}