from typing import Dict
from flask_login import UserMixin, LoginManager
from flask import Flask, request, session, g

from mst.privsys.privsys import check_priv


class User(UserMixin):
    """User model for use with LoginManager"""

    def __init__(self, id_: str, email: str, upn: str):
        """Creates a new user object

        Args:
            id_ (str): The Azure ID given to a user
            email (str): The user's email address
            upn (str): The user's UPN
        """
        self.id = id_
        self.email = email
        self.upn = upn

    @property
    def username(self) -> str:
        """The user's username. Derived from the UPN.

        Returns:
            str: username
        """
        return self.upn.split("@")[0]

    def get_userinfo(self) -> Dict[str, str]:
        """Collects the user's info into a dictionary

        Returns:
            Dict[str, str]: Dict containing the user's id, email, username, and upn.
        """
        userinfo = {
            "id": self.id,
            "email": self.email,
            "username": self.username,
            "upn": self.upn,
        }
        return userinfo


def init_login(app: Flask) -> LoginManager:
    """Initalizes the LoginManager for the app

    Args:
        app (Flask): the flask app

    Returns:
        LoginManager: the initalized LoginManager
    """
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "oauth.login"
    login_manager.USE_SESSION_FOR_NEXT = True
    login_manager.SESSION_COOKIE_SECURE = True
    login_manager.REMEMBER_COOKIE_SECURE = True

    @login_manager.user_loader
    def load_user(user_id):
        app.logger.debug(f"load_user: {user_id}")

        user = User(
            id_=user_id, email=session["user"]["email"], upn=session["user"]["upn"]
        )

        impersonate_priv = app.config.get("IMPERSONATE_PRIV_CODE")

        if (
            impersonate_priv
            and request.cookies.get("REMOTE_USER_IMPERSONATE")
            and check_priv(user.username, impersonate_priv)
        ):
            fake_user = request.cookies["REMOTE_USER_IMPERSONATE"].lower()
            fake_email = f"{fake_user}@umsystem.edu"

            user = User(id_="FAKEUSER", email=fake_email, upn=fake_email)

        g.user = user.get_userinfo()

        return user

    return login_manager
