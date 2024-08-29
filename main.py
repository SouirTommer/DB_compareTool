from ttkbootstrap import Style
import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as ttk
import os, json

import compare_data
import connection_page
import compare_page
import jaydebeapi
import multiprocessing


config_file = "config.json"
jdbc_driver = "driver.jar"

def validate_number(x) -> bool:
    # Validates that the input is a number
    if x.isdigit():
        return True
    elif x == "":
        return True
    else:
        return False

def load_connection_data(server):
    # load connection data from config file
    if os.path.exists(config_file):
        with open(config_file, "r") as file:
            config_data = json.load(file)
        if server in config_data:
            return config_data[server]
    return {"host": "", "port": "", "user": "", "password": "", "database": "", "schema": ""}


def save_connection_data(dbname, host, port, user, password, database, schema):
    # save connection data to config file
    try:
        with open(config_file, "r") as file:
            data = json.load(file)
    except FileNotFoundError:
        data = {}
    data[dbname] = {"host": host, "port": port, "user": user, "password": password, "database": database, "schema": schema}

    with open(config_file, "w") as file:
        json.dump(data, file, indent=4)


def show_frame(frame):
    # change page
    frame.tkraise()
    
    
def get_connection(sy_host, sy_port, sy_user, sy_pwd, pg_host, pg_port, pg_user, pg_pwd, sy_database, pg_database):
    sy_conn = jaydebeapi.connect(
        "net.sourceforge.jtds.jdbc.Driver",
        f"jdbc:jtds:sybase://{sy_host}:{sy_port}/{sy_database};user={sy_user};password={sy_pwd};useLOBs=false;",
        [sy_user, sy_pwd],
        [jdbc_driver],
    )

    pg_conn = jaydebeapi.connect(
        "org.postgresql.Driver",
        f"jdbc:postgresql://{pg_host}:{pg_port}/{pg_database}",
        [pg_user, pg_pwd],
        [jdbc_driver],
    )
    return sy_conn, pg_conn


def on_connect(sy_host, sy_port, sy_user, sy_pwd, pg_host, pg_port, pg_user, pg_pwd, page2, page1, sy_database, pg_database, sy_schema, pg_schema):

    try:
        
        sy_conn, pg_conn = get_connection(sy_host, sy_port, sy_user, sy_pwd, pg_host, pg_port, pg_user, pg_pwd, sy_database, pg_database)
        
        sy_cur = sy_conn.cursor()
        pg_cur = pg_conn.cursor()
        
        sy_cur.execute(f"SELECT name FROM sysobjects WHERE type = 'U' AND uid = USER_ID('{sy_schema}')")
        sy_tables = [row[0] for row in sy_cur.fetchall()]

        pg_cur.execute(f"SELECT table_name FROM information_schema.tables WHERE table_schema = '{pg_schema}'")
        pg_tables = [row[0] for row in pg_cur.fetchall()]
        
        # find the common tables between the two databases
        common_tables = list(set(sy_tables) & set(pg_tables))
        # show the sybase unique table
        sy_unique_tables = list(set(sy_tables) - set(pg_tables))
        # show the postgres unique table
        pg_unique_tables = list(set(pg_tables) - set(sy_tables))
        
        common_tables.sort()
        
        # get databases from sybase and postgres
        # save connection data
        save_connection_data("sybase", sy_host, sy_port, sy_user, sy_pwd, sy_database, sy_schema)
        save_connection_data("postgres", pg_host, pg_port, pg_user, pg_pwd, pg_database, pg_schema)

        # create compare page if connection is successful
        compare_page.create_comapre_page(
            sy_database, pg_database, page2, page1, sy_schema, pg_schema, common_tables, sy_unique_tables, pg_unique_tables,
            sy_conn, pg_conn, sy_cur, pg_cur
        )
    except Exception as e:
        messagebox.showerror("Error", "An error occurred during connecting:\n" + str(e))
        print(e)
        



def create_ui():
    # create main UI
    root = tk.Tk()
    root.title("Compare database data application")
    root.geometry("600x450")
    root.resizable(False, False)
    # validate number function
    digit_func = root.register(validate_number)

    style = Style(theme="flatly")

    page1 = ttk.Frame(root)
    page2 = ttk.Frame(root)

    for frame in (page1, page2):
        frame.grid(row=0, column=0, sticky="nsew")
    # create connection page
    connection_page.create_connection_page(page1, digit_func, page2)

    show_frame(page1)

    root.mainloop()


if __name__ == "__main__":
    multiprocessing.freeze_support()
    create_ui()
