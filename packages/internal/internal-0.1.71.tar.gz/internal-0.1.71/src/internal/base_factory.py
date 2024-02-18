import logging
import logging.handlers
import os
import traceback
from abc import ABCMeta, abstractmethod
from functools import lru_cache

import dotenv
import watchtower
from beanie import init_beanie
from fastapi import FastAPI, status, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from . import database
from .const import LOG_FMT, LOG_FMT_NO_DT, LOG_DT_FMT, DEFAULT_LOGGER_NAME
from .exception.base_exception import InternalBaseException
from .ext.amazon import aws
from .http.responses import async_response
from .utils import update_dict_with_cast


class BaseFactory(metaclass=ABCMeta):
    DEFAULT_APP_NAME = ""
    API_VERSION = "v0.0.0"

    @abstractmethod
    def init_modules(self, app):
        """
        Each factory should define what modules it wants.
        """

    @abstractmethod
    async def get_document_model_list(self) -> list:
        """
        Each factory should define what model it wants.
        """

    @abstractmethod
    @lru_cache()
    def get_app_config(self):
        """
        Each factory should define what config it wants.
        """

    def create_app(self, title=None) -> FastAPI:
        if title is None:
            title = self.DEFAULT_APP_NAME

        app = FastAPI(title=title, debug=self.get_app_config().DEBUG, version=self.API_VERSION)

        origins = ["*"]

        app.add_middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        self.__load_local_config()
        app.state.config = self.get_app_config()
        self.__setup_main_logger(app, level=logging.DEBUG)
        app.state.aws_session = aws.init_app(app)
        self.__setup_cloud_log(app)
        self.__load_cloud_config(app)

        mongodb = database.MongoDB(self.get_app_config().DATABASE_URL, self.get_app_config().DATABASE_NAME)

        @app.on_event("startup")
        async def startup_db_client():
            await mongodb.connect()
            document_model_list = await self.get_document_model_list()
            await init_beanie(database=app.state.db.get_database(), document_models=document_model_list)
            app.state.logger.info("Database connected")

        @app.on_event("shutdown")
        async def shutdown_db_client():
            await mongodb.close()
            app.state.logger.info("Database disconnected")

        app.state.db = mongodb
        app.state.config = self.get_app_config()
        self.__init_modules(app)
        self.__init_builtin_api(app)

        @app.exception_handler(InternalBaseException)
        async def http_exception_handler(request: Request, exc: InternalBaseException):
            detail = exc.detail
            return await async_response(data=detail.get("data"), code=detail.get("code"), message=detail.get("message"),
                                        status_code=exc.status_code)

        @app.exception_handler(RequestValidationError)
        async def validation_exception_handler(request: Request, exc: RequestValidationError):
            return await async_response(data={"detail": exc.errors(), "body": exc.body},
                                        code="error_unprocessable_entity", message="Validation failed",
                                        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)

        @app.exception_handler(Exception)
        async def http_exception_handler(request: Request, exc: Exception):
            app.state.logger.warn(f"Exception, request:{request.__dict__}, exc:{exc}")
            app.state.logger.warn(traceback.format_exc())
            return await async_response(code="error_internal_server", message="Internal server error",
                                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return app

    def __load_local_config(self):
        dotenv.load_dotenv(override=True)
        update_dict_with_cast(self.get_app_config(), os.environ)

    def __load_cloud_config(self, app):
        if not app.state.aws_session or not self.get_app_config().AWS_PARAMETER_PATH_PREFIX:
            app.state.logger.warn("No AWS session or Parameter Storage configuration, ignore cloud config")
            return

        cloud_conf = {}

        params = {
            "Path": self.get_app_config().AWS_PARAMETER_PATH_PREFIX,
            "Recursive": True,
            "WithDecryption": True
        }

        # AWS only give us 10 parameters per api call
        ssm_client = app.state.aws_session.client("ssm")
        while True:
            result = ssm_client.get_parameters_by_path(**params)
            cloud_conf.update({para["Name"].split("/")[-1]: para["Value"] for para in result["Parameters"]})
            if not result.get("NextToken"):
                break
            params.update({"NextToken": result["NextToken"]})

        update_dict_with_cast(self.get_app_config(), cloud_conf)

    def __init_modules(self, app):
        self.init_modules(app)

    def __setup_main_logger(self, app, logger_name=DEFAULT_LOGGER_NAME, level=logging.INFO):
        logger = self.__setup_logger(app, logger_name, level)
        app.state.logger = logger

    #
    def __setup_logger(self, app, logger_name, level=logging.INFO):
        logger = logging.getLogger(logger_name)
        logger.setLevel(level)

        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(logging.Formatter(fmt=LOG_FMT))
        logger.addHandler(stream_handler)

        return logger

    def __setup_cloud_log(self, app):
        if app.state.aws_session and self.get_app_config().AWS_LOGGROUP_NAME:
            logs_client = app.state.aws_session.client("logs")
            watchtower_handler = watchtower.CloudWatchLogHandler(
                log_group_name=self.get_app_config().AWS_LOGGROUP_NAME,
                boto3_client=logs_client, create_log_group=False)
            watchtower_handler.setFormatter(logging.Formatter(fmt=LOG_FMT_NO_DT, datefmt=LOG_DT_FMT))
            app.state.logger.addHandler(watchtower_handler)

    def __init_builtin_api(self, app):

        @app.get(f'/health', tags=["System"])
        async def health():
            return await async_response()

        @app.get(f'/hello', tags=["System"])
        async def hello():
            return await async_response(data={"API version": app.version})
