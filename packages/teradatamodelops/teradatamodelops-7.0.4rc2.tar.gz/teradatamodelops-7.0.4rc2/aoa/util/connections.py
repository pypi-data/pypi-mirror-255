from teradataml import (
    create_context,
    get_context,
    configure
)

import os
import logging
import urllib.parse
import sqlalchemy

logger = logging.getLogger(__name__)


def aoa_create_context(database: str = None) -> sqlalchemy.engine.Engine:
    """
    Creates a teradataml context if one does not already exist.
    Most users should not need to understand how we pass the environment variables etc for dataset connections. This
    provides a way to achieve that and also allow them to work within a notebook for example where a context is already
    present.

    We create the connection based on the following environment variables which are configured automatically by the
    aoa based on the dataset connection selected:

        AOA_CONN_HOST
        AOA_CONN_USERNAME
        AOA_CONN_PASSWORD
        AOA_CONN_LOG_MECH
        AOA_CONN_DATABASE
        AOA_VAL_INSTALL_DB
        AOA_BYOM_INSTALL_DB

    :param database: default database override
    :return: None
    """
    if get_context() is None:
        if not database:
            database = os.getenv("AOA_CONN_DATABASE")

        host = os.environ["AOA_CONN_HOST"]
        logmech = os.getenv("AOA_CONN_LOG_MECH", "TDNEGO")
        username = os.environ["AOA_CONN_USERNAME"]
        # url encode the password to protect for special characters
        password = urllib.parse.quote_plus(os.environ["AOA_CONN_PASSWORD"])

        if database:
            logger.debug(f"Configuring temp database for tables/views to {database}")
            configure.temp_table_database = database
            configure.temp_view_database = database

        configure.val_install_location = os.environ.get("AOA_VAL_INSTALL_DB", "VAL")
        configure.byom_install_location = os.environ.get("AOA_BYOM_INSTALL_DB", "MLDB")

        logger.debug(f"Connecting to {host} on database {database} using logmech {logmech} as {username}")
        td_sqlalchemy_engine = _aoa_create_engine(host=host,
                                                  database=database,
                                                  username=username,
                                                  password=password,
                                                  logmech=logmech)

        create_context(tdsqlengine=td_sqlalchemy_engine)

        from aoa import __version__
        execute_sql(f"""
        SET QUERY_BAND = 'appVersion={__version__};appName=VMO;appFunc=python;org=teradata-internal-telem;' FOR SESSION VOLATILE
        """)

    else:
        logger.info("teradataml context already exists. Skipping create_context.")


def _aoa_create_engine(host: str,
                       database: str,
                       username: str,
                       password: str,
                       logmech: str) -> sqlalchemy.engine.Engine:
    """
    Custom create_engine which works around teradataml bug wrt to password encoding. Will be removed when
    teradataml patch is released.
    """

    from sqlalchemy import create_engine
    from teradataml.common.exceptions import TeradataMlException
    from teradataml.common.messages import Messages
    from teradataml.common.messagecodes import MessageCodes
    from teradataml.context.context import _mask_logmech_logdata, _get_other_connection_parameters

    username = '' if username is None else username
    host_value = '{}:{}@{}'.format(username, password, host)
    other_connection_parameters = _get_other_connection_parameters(logmech=logmech,
                                                                   logdata=None,
                                                                   database=database)

    try:
        engine_url = "teradatasql://{}{}"
        td_sqlalchemy_engine = create_engine(engine_url.format(host_value, other_connection_parameters))

        # Masking senstive information - password, logmech and logdata.
        try:
            # Below statement raises an AttributeError with SQLAlchemy
            # version 1.4.x
            td_sqlalchemy_engine.url.password = "***"
        except AttributeError:
            # Masking the password should be different from above as SQLAlchemy
            # converted _URL object to immutable object from version 1.4.x.
            new_url = td_sqlalchemy_engine.url.set(password="***")
            td_sqlalchemy_engine.url = new_url
        except Exception:
            pass
        _mask_logmech_logdata()

    except TeradataMlException:
        raise
    except Exception as err:
        raise TeradataMlException(Messages.get_message(MessageCodes.CONNECTION_FAILURE),
                                  MessageCodes.CONNECTION_FAILURE) from err

    return td_sqlalchemy_engine


def execute_sql_in_context(context, statement, parameters = None):
    from teradataml.common.exceptions import TeradataMlException
    from teradataml.common.messages import Messages
    from teradataml.common.messagecodes import MessageCodes

    if context is not None:
        tdsql_con = context.raw_connection().driver_connection
        cursor = tdsql_con.cursor()
        return cursor.execute(statement, parameters)
    else:
        raise TeradataMlException(Messages.get_message(MessageCodes.INVALID_CONTEXT_CONNECTION),
                                  MessageCodes.INVALID_CONTEXT_CONNECTION)

def execute_sql(statement, parameters = None):
    return execute_sql_in_context(get_context(),statement,parameters)

def tmo_create_context(database: str = None) -> sqlalchemy.engine.Engine:
    """
    Creates a teradataml context if one does not already exist.
    Most users should not need to understand how we pass the environment variables etc for dataset connections. This
    provides a way to achieve that and also allow them to work within a notebook for example where a context is already
    present.

    We create the connection based on the following environment variables which are configured automatically by the
    aoa based on the dataset connection selected:

        AOA_CONN_HOST
        AOA_CONN_USERNAME
        AOA_CONN_PASSWORD
        AOA_CONN_LOG_MECH
        AOA_CONN_DATABASE
        AOA_VAL_INSTALL_DB
        AOA_BYOM_INSTALL_DB

    :param database: default database override
    :return: None
    """
    return aoa_create_context(database)
