import os
import logging


class DefaultConfig:
    """Default configuration settings applicable to most/all applications. May be overridden per app."""

    INDEX_VIEW = "main.index"

    CONTACT_LABEL = "IT HelpDesk"
    CONTACT_URL = "https://help.mst.edu"

    DEBUG = False
    TESTING = False
    LOG_LEVEL = logging.INFO

    OIDC_VAULT_PATH = os.getenv(
        "OIDC_VAULT_PATH", "apps-shared/k8s/k8s-localhost-dev/oidc-env"
    )
    OAUTH_CONF_URL = "https://login.microsoftonline.com/e3fefdbe-f7e9-401b-a51a-355e01b05a89/v2.0/.well-known/openid-configuration"
    LOCAL_ENV = os.getenv("LOCAL_ENV", "dev")
    APP_URL = os.getenv("APP_URL", "/")
    APP_TEMPLATE = os.getenv(
        "APP_TEMPLATE", "https://apptemplate.mst.edu/v3-jinja-safe"
    )

    if LOCAL_ENV == "dev":
        DEBUG = True
        LOG_LEVEL = logging.DEBUG

    @classmethod
    def wrap_env(cls, app_title: str) -> str:
        """Wraps the input string with the current LOCAL_ENV, if not prod

        Args:
            app_title (str): The string to wrap, usually the APP_TITLE

        Returns:
            str: The input string wrapped with the LOCAL_ENV
        """
        if cls.LOCAL_ENV != "prod":
            _env = cls.LOCAL_ENV.upper()
            return f"{_env} - {app_title} - {_env}"
        return app_title
