""" A simple LDAP connector
    The library standardizes how we get connected to our LDAP environment.

    If no configuration data is available to the module
    it will attempt to make a connection to localhost
    on the default tcp port 389.
"""

import ssl
from os import getenv
from pathlib import Path

from ldap3 import Connection, Server, Tls


def get_connection():
    """
    Provide an insecure client that allows us to read
    NCSU LDAP based people attributes
    """

    try:
        tls = Tls(validate=ssl.CERT_NONE, version=ssl.PROTOCOL_TLSv1_2)
        server = Server("ldap.ncsu.edu", use_ssl=True, tls=tls)
        return Connection(server, auto_bind=True)

    except Exception as ex:
        print("This went off like a SpaceX launch.", ex)


def get_secure_connection(**settings):
    """
    Provide a secure client that allows us to read LDAP based
    people attributes from any LDAP store.

    Parameters
    ----------
    name : settings
    A dictionary of values that define the ldap environment.
    Should only contain the parameters used by the function.

    name: server
    The ldap host to connect to.

    port:
    The TCP port the ldap server is listening on.

    username:
    The ldap user to specify in the bind operation.

    password:
    The password associated to the bind user specified
    in the username parameter.

    Usage:
    ------
    get_connection(server='dilbert', port=1000)
    or
    settings = {"server': 'dilbert', 'port': 1000}
    get_connection(**settings)

    """

    _server = None
    _tls = None

    try:
        server_name = settings.get("server", getenv("server")) or "localhost"
        tcp_port = settings.get("port", getenv("port")) or 389
        ldap_user = settings.get("username", getenv("username")) or None
        ldap_password = settings.get("password", getenv("password")) or None

        if Path("intermediate.pem"):
            _tls = Tls(
                ciphers="ALL",
                local_certificate_file="intermediate.pem",
                validate=ssl.CERT_REQUIRED,
                version=ssl.PROTOCOL_TLS,
            )

        _tls = Tls(ciphers="ALL", validate=ssl.CERT_NONE, version=ssl.PROTOCOL_TLS)

        _server = Server(host=server_name, port=tcp_port, use_ssl=True, tls=_tls)

        if not ldap_user:
            return Connection(server=_server)

        return Connection(server=_server, user=ldap_user, password=ldap_password, auto_bind=True)

    except Exception as ex:
        print("We encountered an error saving the universe.\n", ex)


def get_user_attributes(unity_id: str):
    """
    Returns a dictionary that contains
    the name, unity id, campus id and job title
    for the person

    Parameters
    ----------
    name : unity_id
    The unity id for a campus person
    """
    _attributes = ["cn", "uid", "uidNumber", "title"]

    try:
        with get_connection() as conn:
            conn.search("ou=people,dc=ncsu,dc=edu", f"(uid={unity_id})", attributes=_attributes)

        person_data = {}

        for e in conn.entries:
            for attr in str(e).split("\n"):
                if "DN" in attr:
                    continue

                if "cn" in attr:
                    person_data["name"] = attr.split(":")[1].strip()

                if "title" in attr:
                    person_data["title"] = attr.split(":")[1].strip()

                if "uid" in attr:
                    person_data["unity_id"] = attr.split(":")[1].strip()

                if "uidNumber" in attr:
                    person_data["campus_id"] = attr.split(":")[1].strip()

        return person_data

    except Exception as ex:
        print("Hold on while we try that extension\n", ex)
