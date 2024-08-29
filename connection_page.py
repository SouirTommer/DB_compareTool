from ttkbootstrap import Style
import tkinter as tk
import ttkbootstrap as ttk

import main


def create_connection_page(page1, digit_func, page2):

    # load connection data from config file first

    sybase_dbconn = main.load_connection_data("sybase")
    pg_dbconn = main.load_connection_data("postgres")

    dbconn_frame = ttk.LabelFrame(page1, text="DB connection", height=430, width=580)
    dbconn_frame.grid(row=0, column=0, columnspan=4, padx=10, pady=10, sticky="ew")
    dbconn_frame.grid_propagate(False)

    syconn_label = ttk.Label(dbconn_frame, text="Sybase Database:")
    syconn_label.grid(row=0, column=0, pady=5, padx=10)

    syhost_label = ttk.Label(dbconn_frame, text="Sybase Host:")
    syhost_label.grid(row=1, column=0, pady=10, padx=10)

    syhost_entry = ttk.Entry(dbconn_frame)
    syhost_entry.grid(row=1, column=1, pady=10, padx=10)
    syhost_entry.insert(0, sybase_dbconn["host"])

    syport_label = ttk.Label(dbconn_frame, text="Sybase Post:")
    syport_label.grid(row=2, column=0, pady=10, padx=10)

    syport_entry = ttk.Entry(
        dbconn_frame, validate="focus", validatecommand=(digit_func, "%P")
    )
    syport_entry.grid(row=2, column=1, pady=10, padx=10)
    syport_entry.insert(0, sybase_dbconn["port"])

    syuser_label = ttk.Label(dbconn_frame, text="Sybase User:")
    syuser_label.grid(row=3, column=0, pady=10, padx=10)

    syuser_entry = ttk.Entry(dbconn_frame)
    syuser_entry.grid(row=3, column=1, pady=10, padx=10)
    syuser_entry.insert(0, sybase_dbconn["user"])

    sypwd_label = ttk.Label(dbconn_frame, text="Sybase Password:")
    sypwd_label.grid(row=4, column=0, pady=10, padx=10)

    sypwd_entry = ttk.Entry(dbconn_frame, show="\u25CF")
    sypwd_entry.grid(row=4, column=1, pady=10, padx=10)
    sypwd_entry.insert(0, sybase_dbconn["password"])
    
    sydb_label = ttk.Label(dbconn_frame, text="Sybase Database:")
    sydb_label.grid(row=5, column=0, pady=10, padx=10)

    sydb_entry = ttk.Entry(dbconn_frame)
    sydb_entry.grid(row=5, column=1, pady=10, padx=10)
    sydb_entry.insert(0, sybase_dbconn["database"])
    
    sysc_label = ttk.Label(dbconn_frame, text="Sybase schema:")
    sysc_label.grid(row=6, column=0, pady=10, padx=10)

    sysc_entry = ttk.Entry(dbconn_frame)
    sysc_entry.grid(row=6, column=1, pady=10, padx=10)
    sysc_entry.insert(0, sybase_dbconn["schema"])

    # postgreSQL

    pgconn_label = ttk.Label(dbconn_frame, text="PostgreSQL Database:")
    pgconn_label.grid(row=0, column=2, pady=5, padx=10)

    pghost_label = ttk.Label(dbconn_frame, text="PostgreSQL Host:")
    pghost_label.grid(row=1, column=2, pady=10, padx=10)

    pghost_entry = ttk.Entry(dbconn_frame)
    pghost_entry.grid(row=1, column=3, pady=10, padx=10)
    pghost_entry.insert(0, pg_dbconn["host"])

    pgport_label = ttk.Label(dbconn_frame, text="PostgreSQL Post:")
    pgport_label.grid(row=2, column=2, pady=10, padx=10)

    pgport_entry = ttk.Entry(
        dbconn_frame, validate="focus", validatecommand=(digit_func, "%P")
    )
    pgport_entry.grid(row=2, column=3, pady=10, padx=10)
    pgport_entry.insert(0, pg_dbconn["port"])

    pguser_label = ttk.Label(dbconn_frame, text="PostgreSQL User:")
    pguser_label.grid(row=3, column=2, pady=10, padx=10)

    pguser_entry = ttk.Entry(dbconn_frame)
    pguser_entry.grid(row=3, column=3, pady=10, padx=10)
    pguser_entry.insert(0, pg_dbconn["user"])

    pgpwd_label = ttk.Label(dbconn_frame, text="PostgreSQL Password:")
    pgpwd_label.grid(row=4, column=2, pady=10, padx=10)

    pgpwd_entry = ttk.Entry(dbconn_frame, show="\u25CF")
    pgpwd_entry.grid(row=4, column=3, pady=10, padx=10)
    pgpwd_entry.insert(0, pg_dbconn["password"])
    
    pgdb_label = ttk.Label(dbconn_frame, text="PostgreSQL Database:")
    pgdb_label.grid(row=5, column=2, pady=10, padx=10)

    pgdb_entry = ttk.Entry(dbconn_frame)
    pgdb_entry.grid(row=5, column=3, pady=10, padx=10)
    pgdb_entry.insert(0, pg_dbconn["database"])
    
    pgsc_label = ttk.Label(dbconn_frame, text="PostgreSQL schema:")
    pgsc_label.grid(row=6, column=2, pady=10, padx=10)

    pgsc_entry = ttk.Entry(dbconn_frame)
    pgsc_entry.grid(row=6, column=3, pady=10, padx=10)
    pgsc_entry.insert(0, pg_dbconn["schema"])
    
    


    connect_btn = ttk.Button(
        dbconn_frame,
        text="Connect",
        width=20,
        command=lambda: [
            main.on_connect(
                syhost_entry.get(),
                int(syport_entry.get()),
                syuser_entry.get(),
                sypwd_entry.get(),
                pghost_entry.get(),
                int(pgport_entry.get()),
                pguser_entry.get(),
                pgpwd_entry.get(),
                page2,
                page1,
                sydb_entry.get(),
                pgdb_entry.get(),
                sysc_entry.get(),
                pgsc_entry.get(),
            )
        ],
    )
    connect_btn.pack(pady=100, expand=True)
    connect_btn.grid(row=7, column=1, columnspan=2, pady=40)
