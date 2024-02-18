from base64 import b64decode
from crypt import crypt
from functools import wraps
from flask import redirect, url_for, request, abort
from flask_login import current_user
from mst.privsys.privsys import check_priv, check_priv_regex, fetch_privs
from mst.sql import DBHandler


def token_required(host="sysp"):
    """A decorator function for routes that expect token-based authentication, either through Basic auth or headers.

    For Basic auth, current expectation is that the specified header is in the format client_id:client_secret.
    For header-based auth, the headers X-CLIENT-ID and X-CLIENT-SECRET should be used to store their respective fields.
    Creds are expected to be stored in a table named auth_clients. Also assumes that client_id is unique in the table.

    Args:
        host (str): The host to connect for cred check. Defaults to sysp.

    Returns:
        Returns a decorator that will check if the creds are correct for the wrapped route function.
    """

    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            auth_header = request.headers.get("Authorization")
            if auth_header:
                stripped = auth_header.replace("Basic ", "", 1)
                cid, csecret = b64decode(stripped).decode("ascii").split(":")
            else:
                cid = request.headers.get("X-CLIENT-ID")
                csecret = request.headers.get("X-CLIENT-SECRET")

            if cid and csecret:
                database = DBHandler(host)

                data = database.select_first_dict(
                    "select id, client_secret_crypt, client_id_sub from auth_clients where client_id=:client_id and enabled='Y' order by last_auth desc",
                    client_id=cid,
                )
                if (
                    data
                    and crypt(csecret, data["client_secret_crypt"])
                    == data["client_secret_crypt"]
                ):
                    database.execute(
                        "update auth_clients set last_auth=now(3),auth_count=auth_count+1 where id=:id",
                        {"id": data["id"]},
                    )
                    return f(*args, **kwargs)
            return abort(401)

        return wrapped

    return decorator


def priv_required(priv_code: str, regex: bool = False):
    """Requires the user to have a specific priv grant to access the route.

    Set regex to true to provide a regular expression search for the priv grant.

    If the user is not logged in, redirect to login first.

    Args:
        priv_code (str): the priv code to check against
        regex (bool, optional): indcates whehter the provided priv_code should be processed as a regex pattern. Defaults to False.
    """

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if current_user.is_anonymous:
                return redirect(url_for("oauth.login", next=request.url))
            func = check_priv_regex if regex else check_priv
            if func(current_user.username, priv_code):
                return f(*args, **kwargs)
            abort(403, {"priv_code": priv_code})

        return decorated_function

    return decorator


def priv_required_any(*codes):
    """Determines if the current user has been granted priv access to any of the provided priv codes.
    If the user is not logged in, then redirect to login.

    Args:
        codes: an arbitrary number of priv codes as strings.
    """

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if current_user.is_anonymous:
                return redirect(url_for("oauth.login", next=request.url))
            user_privs = fetch_privs(current_user.username)
            for code in codes:
                if code in user_privs:
                    return f(*args, **kwargs)
            msg = f"Any one of: {', '.join(sorted(codes))}"
            abort(403, {"priv_code": msg})

        return decorated_function

    return decorator
