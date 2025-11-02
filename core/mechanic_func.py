# =====================================================
#  Mechanic Management System - ULTRA CONDENSED (~100 lines)
# =====================================================

import pandas as pd
import stdiomask
from tabulate import tabulate
from db.queries_sql import engcon
from styles import *
from core.utils_cli import fetch_df, exec_sql, pause, menu_box

# ================== HELPER ==================
def get_jobs(mech_id, status=None):
    """Fetch mechanic jobs with optional status filter"""
    base = """SELECT sb.booking_id,sb.status,sb.booking_date,s.service_name,s.category,v.vehicle_no,v.vehicle_brand,v.model
              FROM mechanic_assignments ma JOIN service_bookings sb ON sb.booking_id=ma.booking_id
              JOIN services s ON s.service_id=sb.service_id JOIN vehicles v ON v.vehicle_no=sb.vehicle_no
              WHERE ma.mechanic_id=%s"""
    
    if status:
        if isinstance(status, (list, tuple)):
            return fetch_df(f"{base} AND sb.status IN ({','.join(['%s']*len(status))}) ORDER BY sb.booking_date DESC", (mech_id, *status))
        return fetch_df(f"{base} AND sb.status=%s ORDER BY sb.booking_date DESC", (mech_id, status))
    return fetch_df(f"{base} ORDER BY FIELD(sb.status,'In Progress','Pending','Completed','Cancelled'),sb.booking_date DESC", (mech_id,))

# ================== AUTH ==================
def mechanic_login():
    print(f"{BRIGHT_CYAN}🛠️ MECHANIC LOGIN")
    username = input(f"{BRIGHT_YELLOW}Username/Email: ").strip()
    password = stdiomask.getpass(f"{BRIGHT_YELLOW}Password: ")
    
    if not (username and password):
        print(f"{BRIGHT_RED}❌ Both required.")
        return
    
    df = fetch_df("""SELECT u.user_id,u.username,u.name,mi.mechanic_id,mi.full_name FROM users u
                     JOIN mechanics_info mi ON mi.email=u.email
                     WHERE (u.username=%s OR u.email=%s) AND u.password=%s AND u.user_role='Mechanic'""",
                  (username, username, password))
    
    if not df.empty:
        mech_id, name = df.iloc[0][["mechanic_id", "full_name"]]
        print(f"{BRIGHT_GREEN}✅ Welcome {name} (ID: {mech_id})!")
        mechanic_dashboard(pd.DataFrame([{"mechanic_id": mech_id, "full_name": name}]))
    else:
        print(f"{BRIGHT_RED}❌ Invalid credentials.")

# ================== DASHBOARD ==================
def mechanic_dashboard(logindf):
    mech_id = int(logindf.iloc[0]["mechanic_id"])
    name = str(logindf.iloc[0]["full_name"])
    
    while True:
        choice = menu_box(
            f"🛠️  MECHANIC DASHBOARD — {name} (ID: {mech_id})",
            ["1) ✏️ Edit Profile", "2) 🔍 View All Jobs", "3) 🔄 Update Job Status", "4) 🗂️ Filter Jobs", "0) 🚪 Logout"],
            "Choice: "
        )
        
        if choice == "1":
            edit_profile(mech_id)
        elif choice == "2":
            view_jobs(mech_id)
        elif choice == "3":
            update_status(mech_id)
        elif choice == "4":
            filter_jobs(mech_id)
        elif choice == "0":
            print(f"{BRIGHT_BLUE}👋 Logged out!")
            break
        else:
            print(f"{BRIGHT_RED}Invalid.")
            pause()

# ================== PROFILE ==================
def edit_profile(mech_id):
    print(f"\n{BRIGHT_CYAN}🧾 Edit Profile")
    fields = {'1':('full_name','Name','mechanics_info'),'2':('specialization','Specialization','mechanics_info'),
              '3':('phone','Phone','both'),'4':('email','Email','both'),'5':('password','Password','users')}
    
    print(f"{BRIGHT_YELLOW}1=Name, 2=Specialization, 3=Phone, 4=Email, 5=Password")
    ch = input("Select: ").strip()
    
    if ch not in fields:
        print(f"{BRIGHT_RED}❌ Invalid.")
        pause()
        return
    
    field, label, table = fields[ch]
    val = stdiomask.getpass(f"{BRIGHT_YELLOW}New {label}: ") if field=='password' else input(f"{BRIGHT_YELLOW}New {label}: ").strip()
    
    if not val:
        print(f"{BRIGHT_RED}❌ Empty.")
        pause()
        return
    
    if table in ('users','both'):
        exec_sql(f"UPDATE users SET {field}=%s WHERE email=(SELECT email FROM mechanics_info WHERE mechanic_id=%s)", (val, mech_id), success=f"✅ Updated in users.")
    if table in ('mechanics_info','both') and field != 'password':
        exec_sql(f"UPDATE mechanics_info SET {field}=%s WHERE mechanic_id=%s", (val, mech_id), success=f"✅ Updated in profile.")
    pause()

# ================== JOBS ==================
def view_jobs(mech_id):
    print(f"\n{BRIGHT_CYAN}🔧 All Jobs")
    df = get_jobs(mech_id)
    print(tabulate(df, headers="keys", tablefmt="fancy_grid", showindex=False) if not df.empty else f"{BRIGHT_RED}❌ No jobs.")
    pause()

def update_status(mech_id):
    print(f"\n{BRIGHT_CYAN}🔄 Update Status")
    df = get_jobs(mech_id, ['Pending','In Progress'])
    
    if df.empty:
        print(f"{BRIGHT_RED}❌ No active jobs.")
        pause()
        return
    
    print(tabulate(df, headers='keys', tablefmt='fancy_grid', showindex=False))
    bid = input(f"\n{BRIGHT_YELLOW}Booking ID: ").strip()
    
    if not bid or int(bid) not in df['booking_id'].values:
        print(f"{BRIGHT_RED}❌ Invalid booking.")
        pause()
        return
    
    current = df[df['booking_id']==int(bid)]['status'].iloc[0]
    valid = {'Pending':['In Progress','Cancelled'], 'In Progress':['Completed','Cancelled']}
    allowed = valid.get(current, [])
    
    if not allowed:
        print(f"{BRIGHT_RED}❌ Can't change from '{current}'.")
        pause()
        return
    
    print(f"\n{BRIGHT_YELLOW}Current: {current}")
    for i, s in enumerate(allowed, 1):
        print(f"  {i}) {s}")
    
    try:
        idx = int(input(f"\n{BRIGHT_YELLOW}Select (1-{len(allowed)}): ")) - 1
        if 0 <= idx < len(allowed):
            exec_sql("UPDATE service_bookings SET status=%s WHERE booking_id=%s", (allowed[idx], bid), success=f"{BRIGHT_GREEN}✅ Updated to '{allowed[idx]}'.")
        else:
            print(f"{BRIGHT_RED}❌ Invalid.")
    except ValueError:
        print(f"{BRIGHT_RED}❌ Enter number.")
    pause()

def filter_jobs(mech_id):
    print(f"\n{BRIGHT_CYAN}🗂️ Filter Jobs")
    ch = menu_box("Filter", ["1) ✅ Completed", "2) ⏳ Active", "3) ❌ Cancelled", "4) 📋 All", "0) Back"], "Select: ")
    
    if ch == "0": return
    
    filters = {"1":("Completed",), "2":("Pending","In Progress"), "3":("Cancelled",), "4":None}
    status = filters.get(ch)
    
    if ch not in filters:
        print(f"{BRIGHT_RED}❌ Invalid.")
        pause()
        return
    
    df = get_jobs(mech_id, status)
    filter_name = {"1":"Completed", "2":"Active", "3":"Cancelled", "4":"All"}.get(ch, "Filtered")
    
    print(f"\n{BRIGHT_CYAN}📊 {filter_name} Jobs")
    print(tabulate(df, headers="keys", tablefmt="fancy_grid", showindex=False) if not df.empty else f"{BRIGHT_RED}❌ No jobs.")
    pause()
