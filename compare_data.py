import datetime, xlsxwriter, numpy as np, pandas as pd, jaydebeapi

from ttkbootstrap import Style
from tkinter import ttk, messagebox
import tkinter as tk
import main
import os
import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import multiprocessing as mp

error = 0

# convert all datatype to string
# for the Nat nan noe nan, replace them with empty string
def convert_columns_toStr(df):
    for col in df.select_dtypes(include=['int64']).columns:
        df[col] = df[col].astype('float64')
    return df.astype(str).replace(["NaT", "nan", "None", "NaN"], "")

# highlight the differences between the two dataframes
def highlight_diff(data, color="yellow"):
    attr = "background-color: {}".format(color)
    first = data.xs("Sy", axis="columns", level=-1)
    other = data.xs("Pg", axis="columns", level=-1)
    # check if the data is equal, if not, highlight the cell
    return pd.DataFrame(
        np.where(data.ne(other, level=0) | data.ne(first, level=0),attr,"",),
        index=data.index,
        columns=data.columns,
    )
    
# get the data from the table and store it in a pandas dataframe
def get_dataframe(cursor, schema, table):
    cursor.execute(
        f'SELECT * FROM "{schema}"."{table}"'
    )
    rows = cursor.fetchall()
    return pd.DataFrame(rows, columns=[desc[0] for desc in cursor.description])

# prepare the dataframe for comparison
# step 1: sort the dataframe by all columns
# step 2: reset the index
# step 3: convert all columns to string
# step 4: add a unique ID column if the first column is not unique
def prepare_dataframe(df1, df2):
    
    df1.sort_values(by=list(df1.columns), ascending=False, inplace=True)
    df2.sort_values(by=list(df2.columns), ascending=False, inplace=True)
    
    df1.reset_index(drop=True, inplace=True)
    df2.reset_index(drop=True, inplace=True)
    
    if (len(df1) != len(df2)):
        matching_rows = pd.merge(df1, df2, how='inner', indicator=False)
        extra_rows = pd.merge(df1, df2, how='left', indicator=True)
        extra_rows = extra_rows[extra_rows['_merge'] == 'left_only'].drop('_merge', axis=1)
        df1 = pd.concat([matching_rows, extra_rows]).reset_index(drop=True)

    df1 = convert_columns_toStr(df1)
    df2 = convert_columns_toStr(df2)
    #if not df.iloc[:, 0].is_unique:
    #df.insert(0, "UniqueID", ["U" + str(i) for i in range(1, 1 + len(df))])
    df1.insert(0, "UniqueID", 'U' + (df1.index + 1).astype(str))
    df2.insert(0, "UniqueID", 'U' + (df2.index + 1).astype(str))
    
    return df1, df2

def process_data(sy_selected_db, pg_selected_db, syschema, pgschema, mode, table_name, common_tables, sy_unique_tables, pg_unique_tables, sy_conn, pg_conn, sy_cur, pg_cur, selected_tables):
    global error
    error = 0
    # output directory, you can modify it to rename
    output_dir = "output"
    try:
        # create the output directory if it does not exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        print("-------process_data--------")
        
        if mode == "Single":
            common_tables = [table_name]
        elif mode == "Multi":
            common_tables = selected_tables
            common_tables.sort()
            
        # get the current date and time, it is used to name the excel file
        formatted_datetime = datetime.datetime.now().strftime("output.%Y%m%d-%H%M%S")
        
        max_threads = os.cpu_count() * 2
    
        # load connection data from config file
        sybase_dbconn = main.load_connection_data("sybase")
        pg_dbconn = main.load_connection_data("postgres")
        sybase_info = [
            sybase_dbconn['host'],
            sybase_dbconn['port'],
            sybase_dbconn['user'],
            sy_selected_db,
            syschema
        ]
        postgres_info = [
            pg_dbconn['host'],
            pg_dbconn['port'],
            pg_dbconn['user'],
            pg_selected_db,
            pgschema
        ]
        
        with mp.Manager() as manager:
            queue = manager.Queue()
            pool = mp.Pool(processes=os.cpu_count())
            pool.apply_async(write_to_excel, (queue, output_dir, formatted_datetime,sybase_info,postgres_info))

            # create an excel file with the common tables
            with ThreadPoolExecutor(max_workers=max_threads) as executor:
                futures = {
                    executor.submit(
                        process_table_wrapper,
                        (sy_conn, pg_conn, syschema, pgschema, table, output_dir, formatted_datetime, queue)
                    ): table for table in common_tables}
                
                for future in as_completed(futures):
                    try:
                        future.result()
                    except Exception as e:
                        with open(os.path.join(output_dir, f"log_{formatted_datetime}.txt"),"a",) as f:
                            f.write(f"An error occurred with table {futures[future]}: {e}\n")
                            print(e)

            queue.put("DONE")
            pool.close()
            pool.join()
        
        sy_cur.close()
        pg_cur.close()
        
        messagebox.showinfo("Success", "Data processing completed!\nErrors: " + str(error))
        # print all processed table
        print("Processed tables: ", common_tables)
        # print the unqiue tables
        print("Sybase unique tables: ", sy_unique_tables)
        print("Postgres unique tables: ", pg_unique_tables)
        with open(os.path.join(output_dir, f"log_{formatted_datetime}.txt"),"a",) as f:
            f.write(f"Sybase unique tables: {sy_unique_tables}\n\n")
            f.write(f"Postgres unique tables: {pg_unique_tables}\n\n")

        # if it is single table mode and have error, delete the excel file
        if len(common_tables) == 1 and error > 0:
            os.remove(os.path.join(output_dir, f"{formatted_datetime}.xlsx"))

    # if an error occurs before looping, delete the excel file
    except Exception as e:
        messagebox.showerror("Error", "An error occurred during processing:\n" + str(e))
        os.remove(os.path.join(output_dir, f"{formatted_datetime}.xlsx"))
        print(e)
        

def write_to_excel(queue, output_dir, formatted_datetime, sybase_info, postgres_info):
    
    with pd.ExcelWriter(os.path.join(output_dir, f"{formatted_datetime}.xlsx"), engine="xlsxwriter") as writer:
        dbdf = pd.DataFrame(
            {
                "Sybase": sybase_info,
                "Postgres": postgres_info,
            },
            index=["Host", "Port", "User", "Database", "Schema"],
        )
        dbdf.to_excel(writer, sheet_name="Database Info")
        
        info_row = len(dbdf) + 2
        info_worksheet = writer.sheets["Database Info"]
        
        while True:
            item = queue.get()
            if item == "DONE":
                print("Finished compare, writing to Excel...")
                break
            
            table, df_diff, df_final, diffnum, difflen, df1_length, df2_length  = item

            if df_diff is not None:
                df_diff.to_excel(writer, sheet_name=table, startrow=1)

            startcol = 4 + len(df_diff.columns) if diffnum > 0 else 2

            df_final_styled = df_final.style.apply(highlight_diff, axis=None)
            df_final_styled.to_excel(writer, sheet_name=table, startrow=1, startcol=startcol)

            workbook = writer.book
            worksheet = writer.sheets[table]
            worksheet.set_column("A:A", 13)
            worksheet.set_column("B:ZZ", 13)
            worksheet.autofit()
            
            if difflen:
                message = "Differences: {} - Lengths different (Sybase: {} Postgres: {})".format(diffnum, df1_length, df2_length)
            else:
                message = "Differences: {}".format(diffnum)
                
            worksheet.write(0, 0, message, workbook.add_format({"bold": True}))
            
            if diffnum > 0:
                info_worksheet.write(info_row, 0, table)
                info_worksheet.write(info_row, 1, message)
                info_row += 1
                

        info_worksheet.set_column("A:A", 20)
        info_worksheet.set_column("B:G", 15)
            
def process_table_wrapper(args):
    return process_table(*args)

def process_table(sy_conn, pg_conn, syschema, pgschema, table, output_dir, formatted_datetime, queue):
    global error
    try:
        
        sy_cur = sy_conn.cursor()
        pg_cur = pg_conn.cursor()
        
        print(table)

        # store the results in a pandas dataframe
        df1 = get_dataframe(sy_cur, syschema, table)
        df2 = get_dataframe(pg_cur, pgschema, table)

        df1, df2 = prepare_dataframe(df1, df2)
        # merge the two dataframes
        df_all = pd.concat(
            [df1.set_index(df1.columns[0]), df2.set_index(df2.columns[0])],
            axis="columns",
            keys=["Sy", "Pg"],
        )

        df_final = df_all.swaplevel(axis="columns")[df1.columns[1:]]
        
        # cut the table name if it exceeds 31 characters
        if len(table) > 31:
            with open(os.path.join(output_dir, f"log_{formatted_datetime}.txt"),"a",) as f:
                f.write(f"The sheet name {table} exceeds 31 characters, the new sheet name is {table[:31]} \n")
            table = table[:31]
            
        diffnum = 0
        difflen = len(df1) != len(df2)
        
        df1_length = len(df1)
        df2_length = len(df2)
        if difflen:
            df1, df2 = df1.align(df2, join='outer', axis=0, fill_value="")
            df1, df2 = df1.align(df2, join='outer', axis=1, fill_value="")
                
        # store the differences in a new dataframe
        df_diff = df1.compare(df2)
        df_diff.rename(columns={"self": "Sy", "other": "Pg"}, inplace=True)
        diffnum = len(df_diff)

        df_diff.index.name = df1.columns[0]
        df_diff.index += 1
        df_diff.index = df_diff.index.map(lambda x: f'U{x}')

        # create a different table if have differences,
        if len(df_diff) > 0:
            queue.put((table, df_diff, df_final, diffnum, difflen, df1_length, df2_length))
        else:
            queue.put((table, None, df_final, diffnum, difflen, df1_length, df2_length))
        
        sy_cur.close()
        pg_cur.close()
        

    except Exception as e:
        with open(os.path.join(output_dir, f"log_{formatted_datetime}.txt"),"a",) as f:
            error += 1
            current_time = datetime.datetime.now().strftime("%H:%M:%S")
            f.write(f"{current_time} An error occurred with table {table}: {e}\n")
        print(e)