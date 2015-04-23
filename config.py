from flask import Flask
import os
import pickle
basedir = os.path.abspath(os.path.dirname(__file__))

class Config():
    pass

class ProductionConfig():
    PICKLE_PATH = os.path.join(basedir, 'contacts.p')
class DevelopmentConfig():
    DEBUG = True
    PICKLE_PATH = os.path.join(basedir, 'development.p')
