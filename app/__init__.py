#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import logging
from celery import Celery

import config

db = SQLAlchemy()
celery = Celery(__name__,broker=config.Config.CELERY_BROKER_URL)


def logger_init(name="root"):
    """
    log 初始化
    :param name:
    :return:
    """
    logger = logging.getLogger(name)
    handler = logging.FileHandler('app.log', encoding='utf-8')
    logging_format = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - %(lineno)s - %(message)s")
    logger.setLevel(logging.DEBUG)
    handler.setFormatter(logging_format)
    #logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    return logger


def logger(name="root"):
    """
    日志 logger
    :param name:
    :return:
    """
    return logging.getLogger(name)


def create_app():
    import controllers
    app = Flask(__name__, instance_relative_config=True)
    # 注册配置文件
    app.config.from_object(config.Config)
    celery.conf.update(app.config)
    # SQLAlchemy
    db.init_app(app)

    # 注册 Blueprint
    app.register_blueprint(controllers.ctl)
    controllers.api.init_app(app)
    # CORS
    CORS(app, resources={r"*": {"origins": config.Config.CORS_ORIGINS}})
    # LOG
    app.debug = config.Config.DEBUG
    logger_init()

    return app