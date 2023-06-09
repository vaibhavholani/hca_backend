import psycopg2
from psycopg2.extras import (RealDictCursor, )
import os
from typing import Tuple
from dotenv import load_dotenv


def connect():
    """
    Provides a reference to the database and its cursor
    """
    load_dotenv()

    mydb  = psycopg2.connect(
        dbname=os.getenv("DB_NAME"), 
        user=os.getenv("DB_USER"), 
        password=os.getenv("DB_PASSWORD"), 
        host="localhost")

    # DATABASE_URL = os.environ['DATABASE_URL']
    # mydb = psycopg2.connect(DATABASE_URL, sslmode="require")
    return mydb


def cursor(dict = False) -> Tuple:
    """
    return the cursor and db connection
    """
    database = connect()
    if dict:
        db_cursor = database.cursor(cursor_factory=RealDictCursor)
    else: 
        db_cursor = database.cursor()
    return database, db_cursor

def update(): pass

def add_stack_val(a, b): pass

def add_stack_val_multiple(a,b): pass

def add_stack(dfas): pass
