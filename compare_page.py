from ttkbootstrap import Style
import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as ttk
import threading

import main


def create_comapre_page(sy_database, pg_database, page2, page1, sy_schema, pg_schema, common_tables, sy_unique_tables, pg_unique_tables,
                        sy_conn, pg_conn, sy_cur, pg_cur):
    
    main.show_frame(page2)

    compare_frame = ttk.LabelFrame(page2, text="Compare data", height=430, width=580)
    compare_frame.grid(row=0, column=0, columnspan=4, padx=10, pady=10, sticky="ew")
    compare_frame.grid_propagate(False)

    sy_label = ttk.Label(compare_frame, text="Sybase Database:")
    sy_label.grid(row=0, column=0, pady=15, padx=10)

    sydb_entry = ttk.Entry(compare_frame)
    sydb_entry.insert(0,sy_database)
    sydb_entry.configure(state='readonly')
    sydb_entry.grid(row=0, column=1, pady=15, padx=10)

    syschema_label = ttk.Label(compare_frame, text="Sybase Schema:")
    syschema_label.grid(row=0, column=2, pady=15, padx=10)

    syschema_entry = ttk.Entry(compare_frame)
    syschema_entry.insert(0, sy_schema)
    syschema_entry.configure(state='readonly')
    syschema_entry.grid(row=0, column=3, pady=15, padx=10)

    pg_label = ttk.Label(compare_frame, text="PostgreSQL Database:")
    pg_label.grid(row=1, column=0, pady=15, padx=10)

    pgdb_entry = ttk.Entry(compare_frame)
    pgdb_entry.insert(0,pg_database)
    pgdb_entry.configure(state='readonly')
    pgdb_entry.grid(row=1, column=1, pady=15, padx=10)
    
    pgschema_label = ttk.Label(compare_frame, text="Postgres Schema:")
    pgschema_label.grid(row=1, column=2, pady=15, padx=10)

    pgschema_entry = ttk.Entry(compare_frame)
    pgschema_entry.insert(0, pg_schema)
    pgschema_entry.configure(state='readonly')
    pgschema_entry.grid(row=1, column=3, pady=15, padx=10)

    table_select_all_label = ttk.Label(compare_frame, text="All tables:")
    table_select_all_label.grid(row=2, column=0, pady=15)
    
    # radio button variable
    selected_campare_table = tk.StringVar()
    # default value
    selected_campare_table.set("All")

    def on_single_radio_button_select():
        # when the radio button is selected, show or hide the single table entry, user need to enter the table name
        if selected_campare_table.get() == "Single":
            table_select_single_entry.config(state="normal")
            table_select_single_entry.grid()
        else:
            table_select_single_entry.config(state="disabled")
            table_select_single_entry.grid_remove()
            
        if selected_campare_table.get() == "Multi":
            table_select_multi_entry.config(state="normal")
            table_select_multi_entry.grid()
        else:
            table_select_multi_entry.config(state="disabled")
            table_select_multi_entry.grid_remove()


    table_select_all = ttk.Radiobutton(
        compare_frame,
        variable=selected_campare_table,
        value="All",
        command=on_single_radio_button_select,
    )
    table_select_all.grid(row=2, column=1, pady=15)

    table_select_single_label = ttk.Label(compare_frame, text="Single tables:")
    table_select_single_label.grid(row=2, column=2, pady=15)

    table_select_single = ttk.Radiobutton(
        compare_frame,
        variable=selected_campare_table,
        value="Single",
        command=on_single_radio_button_select,
    )
    table_select_single.grid(row=2, column=3, pady=15)

    table_select_single_entry = ttk.Entry(compare_frame, state="disabled")
    table_select_single_entry.grid(row=2, column=3)
    table_select_single_entry.grid_remove()
    
    table_select_multi_label = ttk.Label(compare_frame, text="Select tables:")
    table_select_multi_label.grid(row=3, column=0, pady=15)
    
    table_select_multi = ttk.Radiobutton(
        compare_frame,
        variable=selected_campare_table,
        value="Multi",
        command=on_single_radio_button_select,
    )
    table_select_multi.grid(row=3, column=1, pady=15)
    
    table_select_multi_entry = tk.Listbox(compare_frame, selectmode=tk.MULTIPLE)
    table_select_multi_entry.grid(row=3, column=1)
    table_select_multi_entry.grid_remove()
        
    for table in common_tables:
        table_select_multi_entry.insert(tk.END, table)
        
    #a function to get table_select_multi_entry array
    def get_selected_tables():
        selected_tables = []
        for index in table_select_multi_entry.curselection():
            selected_tables.append(table_select_multi_entry.get(index))
        return selected_tables


    # back button to go back to connection page
    back_button = ttk.Button(
        compare_frame,
        text="Back",
        command=lambda: main.show_frame(page1),
        bootstyle="SECONDARY",
    )
    back_button.grid(row=5, column=0, columnspan=1, pady=15)

    def start_processing():

        process_button.config(text="Processing...", state="disabled")

        def thread_target():
            #main.save_schemas(syschema_entry.get(), pgschema_entry.get())
            main.compare_data.process_data(
                sy_database,
                pg_database,
                syschema_entry.get(),
                pgschema_entry.get(),
                selected_campare_table.get(),
                table_select_single_entry.get(),
                common_tables,
                sy_unique_tables,
                pg_unique_tables,
                sy_conn,
                pg_conn,
                sy_cur,
                pg_cur,
                get_selected_tables()
                
            )
            # This needs to be done in the main thread, hence using `after`
            process_button.after(
                0, lambda: process_button.config(text="Process", state="normal")
            )

        # Start the thread
        threading.Thread(target=thread_target, daemon=True).start()

    # Modify the command to use the new start_processing function
    process_button = ttk.Button(
        compare_frame, text="Process", width=20, command=start_processing
    )
    process_button.grid(row=5, column=1, columnspan=2, pady=15)
