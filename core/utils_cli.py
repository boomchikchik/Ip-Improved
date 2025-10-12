# core/utils_cli.py
import pandas as pd
from tabulate import tabulate
from db.queries_sql import mycon, cursor, engcon
from styles import *

def pause(msg="Press Enter to continue..."):
    try: input(f"{DIM_YELLOW}{msg}")
    except EOFError: pass

def fetch_df(sql, params=None):
    try:
        if params:
            return pd.read_sql(sql, con=engcon, params=params)
        else:
            return pd.read_sql(sql, con=engcon)
    except Exception as e:
        print(f"{BRIGHT_RED}DB Error: {e}")
        return pd.DataFrame()


def exec_sql(sql, params=None, ok="✅ Done.",success=None):
    if success is not None:
        ok = success
    try:
        cursor.execute(sql, params or ())
        mycon.commit()
        print(f"{BRIGHT_GREEN}{ok}")
        return True
    except Exception as e:
        mycon.rollback()
        print(f"{BRIGHT_RED}DB Error: {e}")
        return False

def show_table(sql, params=None, title=None):
    df = fetch_df(sql, params)
    if df.empty:
        print(f"{BRIGHT_RED}No records found.")
    else:
        if title: print(f"\n{BRIGHT_CYAN}{title}")
        print(tabulate(df, headers="keys", tablefmt="fancy_grid", showindex=False))
    pause()
    return df

def menu_box(title, options, prompt="Select an option: "):
    print(f"\n{BRIGHT_YELLOW}{title}")
    print(tabulate([[k + ". " + v] for k, v in options.items()], tablefmt="fancy_grid"))
    return input(f"{BRIGHT_CYAN}{prompt}").strip()

def dashboard_loop(title, options):
    while True:
        choice = menu_box(title, {k: v[0] for k, v in options.items()})
        func = options.get(choice, [None, None])[1]
        if func: func()
        elif choice == "0" or func is None:
            print(f"{BRIGHT_MAGENTA}↩ Back to previous menu.")
            break
        else:
            print(f"{BRIGHT_RED}❌ Invalid choice.")
