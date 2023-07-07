import tkinter as tk
from tkinter import ttk
import sqlite3 as sq
from tkinter import messagebox


def validate_int(input):
    if input == '':
        return True
    try:

        int(input)
        return True
    except ValueError:
        return False


def validate_str(input):
    for ch in input:
        if not (ch.isalpha() or ch.isspace()):
            return False
    return True



def delete_all_rows():
    con = sq.connect('game.db')
    cur = con.cursor()

    # Удаление всех записей из таблицы "gamers"
    cur.execute("DELETE FROM gamers")

    con.commit()
    con.close()


def update_table():
    con = sq.connect('game.db')
    cur = con.cursor()
    cur.execute('SELECT * FROM gamers')
    rows = cur.fetchall()
    return rows


def coun_records():
    with sq.connect('game.db') as con:
        cur = con.cursor()
        cur.execute('SELECT count() FROM gamers')
        count = cur.fetchone()[0]
        return count


def count_man():
    with sq.connect('game.db') as con:
        cur = con.cursor()
        cur.execute("SELECT COUNT(*) FROM gamers WHERE sex='Прочитал'")
        count = cur.fetchone()[0]
        return count


def count_girl():
    with sq.connect('game.db') as con:
        cur = con.cursor()
        cur.execute("SELECT COUNT(*) FROM gamers WHERE sex='Читаю'")
        count = cur.fetchone()[0]
        return count


