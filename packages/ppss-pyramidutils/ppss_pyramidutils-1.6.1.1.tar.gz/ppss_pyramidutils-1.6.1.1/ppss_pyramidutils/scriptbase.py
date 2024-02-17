from sqlalchemy import engine_from_config
from sqlalchemy.orm import sessionmaker
import configparser,os

import logging,logging.config
l = logging.getLogger(__name__)

def engineFromConfigPath(config_uri):

  config = configparser.ConfigParser() 
  with open(config_uri,"r") as inifile:
    config.read_string(inifile.read())
  ##TODO: here is wrong. what should it be?
  here = os.getcwd()
  config["app:main"]["here"] = here
  logging.config.fileConfig(config)
  return config,engineFromConfig(config)

def engineFromConfig(config):
  engine = engine_from_config(config["app:main"], "sqlalchemy.")
  return engine

def engineFromSettings(config):
  engine = engine_from_config(config, "sqlalchemy.")
  return engine

def factoryFormSettings(config):
  engine = engineFromSettings(config)
  session_factory = sessionmaker(bind=engine)
  return session_factory