# =====================================================
#  User Management System - ULTRA CONDENSED (~150 lines)
# =====================================================

import pandas as pd
import stdiomask
from db.queries_sql import engcon
from styles import *
from core.utils_cli import fetch_df, exec_sql, show_table, pause

# ================== VALIDATION ==================
def validate_input(prompt, validator, error):
    while True:
        val = input(f"{BRIGHT_YELLOW}{prompt}").strip()
        if validator(val): return val
        print(f"{BRIGHT_RED}❌ {error}")

def get_password():
    while True:
        pwd = stdiomask.getpass(f"{BRIGHT_YELLOW}Password (min 6 chars): ")
        if len(pwd) >= 6:
            if pwd == stdiomask.getpass(f"{BRIGHT_YELLOW}Confirm: "):
                return pwd
            print(f"{BRIGHT_RED}❌ Passwords don't match.")
        else:
            print(f"{BRIGHT_RED}❌ Too short.")

# ================== AUTH ==================
def user_registration():
    print(f"{BRIGHT_CYAN}\n🧾 USER REGISTRATION")
    data = {
        'name': validate_input("Name: ", lambda x: x.replace(" ", "").isalpha(), "Letters only."),
        'email': validate_input("Email: ", lambda x: "@" in x and "." in x, "Invalid email."),
        'phone': validate_input("Phone (10-12 digits): ", lambda x: x.isdigit() and len(x) in [10,11,12], "Invalid phone."),
        'address': input(f"{BRIGHT_YELLOW}Address: ").strip(),
        'city': input(f"{BRIGHT_YELLOW}City: ").strip(),
        'state': input(f"{BRIGHT_YELLOW}State: ").strip(),
        'username': input(f"{BRIGHT_YELLOW}Username: ").strip(),
        'password': get_password()
    }
    exec_sql("INSERT INTO users(name,email,phone,address,city,state,username,password,user_role) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,'Customer')",
             tuple(data.values()), success=f"{BRIGHT_GREEN}✅ Registration successful!")

def user_login():
    print(f"{BRIGHT_CYAN}\n🔐 USER LOGIN")
    while True:
        username = input(f"{BRIGHT_YELLOW}Username/Email: ").strip()
        password = stdiomask.getpass(f"{BRIGHT_YELLOW}Password: ")
        if not (username and password):
            print(f"{BRIGHT_RED}❌ Both fields required.")
            continue
        df = fetch_df("SELECT * FROM users WHERE (username=%s OR email=%s) AND password=%s", (username, username, password))
        if not df.empty:
            print(f"{BRIGHT_GREEN}✅ Login successful!")
            user_dashboard(df)
            return
        print(f"{BRIGHT_RED}❌ Invalid credentials.")
        if input(f"{DIM_YELLOW}Retry? (Enter/exit): ").lower() == "exit": return

# ================== DASHBOARD ==================
def user_dashboard(df):
    uid = int(df.iloc[0]["user_id"])
    name = df.iloc[0]["name"]
    
    menu = {
        "1": ("Profile", lambda: manage_profile(uid)),
        "2": ("Add Vehicle", lambda: add_vehicle(uid)),
        "3": ("Manage Vehicles", lambda: manage_vehicles(uid)),
        "4": ("Browse Services", browse_services),
        "5": ("Book Service", lambda: book_service(uid)),
        "6": ("Make Payment", lambda: make_payment(uid)),
        "7": ("Booking History", lambda: show_user_view(uid, "history")),
        "8": ("Track Order", lambda: show_user_view(uid, "track")),
        "9": ("Cancel Order", lambda: cancel_order(uid)),
        "10": ("View Invoices", lambda: show_user_view(uid, "invoices")),
        "11": ("Payment Status", lambda: show_user_view(uid, "payments")),
        "12": ("Leave Feedback", lambda: leave_feedback(uid)),
    }
    
    while True:
        print(f"\n{BRIGHT_CYAN}===== USER DASHBOARD =====\n{BRIGHT_GREEN}Welcome, {name}!")
        for k, (label, _) in menu.items():
            print(f"  {BRIGHT_YELLOW}{k}.{BRIGHT_CYAN} {label}")
        print(f"  {BRIGHT_MAGENTA}0.{BRIGHT_CYAN} Logout")
        
        choice = input(f"{BRIGHT_YELLOW}Choice: ").strip()
        if choice == "0":
            print(f"{BRIGHT_MAGENTA}↩ Logging out...")
            break
        elif choice in menu:
            menu[choice][1]()
        else:
            print(f"{BRIGHT_RED}❌ Invalid choice.")

# ================== PROFILE ==================
def manage_profile(uid):
    df = fetch_df("SELECT name,email,phone,address,city,state,username FROM users WHERE user_id=%s", (uid,))
    if df.empty: return
    print(f"\n{BRIGHT_CYAN}Your Profile:\n{df.iloc[0].to_string()}")
    
    action = input(f"\n{BRIGHT_YELLOW}1=Edit Profile, 2=Change Password, 0=Back: ").strip()
    if action == "1":
        row = df.iloc[0]
        updates = {k: input(f"{k.title()} [{row[k]}]: ").strip() or row[k] for k in ['name','email','phone','address','city','state']}
        exec_sql("UPDATE users SET name=%s,email=%s,phone=%s,address=%s,city=%s,state=%s WHERE user_id=%s",
                 (*updates.values(), uid), success=f"{BRIGHT_GREEN}✅ Profile updated.")
    elif action == "2":
        old = stdiomask.getpass("Old Password: ")
        if fetch_df("SELECT 1 FROM users WHERE user_id=%s AND password=%s", (uid, old)).empty:
            print(f"{BRIGHT_RED}❌ Wrong password.")
        else:
            exec_sql("UPDATE users SET password=%s WHERE user_id=%s", (get_password(), uid), success=f"{BRIGHT_GREEN}✅ Password changed.")

# ================== VEHICLES ==================
def add_vehicle(uid):
    print(f"{BRIGHT_CYAN}\n🚗 ADD VEHICLE")
    data = [input(f"{BRIGHT_YELLOW}{f}: ").strip() for f in ['Vehicle No','Brand','Model','Type']] + [uid]
    exec_sql("INSERT INTO vehicles(vehicle_no,vehicle_brand,model,type,user_id) VALUES(%s,%s,%s,%s,%s)",
             data, success=f"{BRIGHT_GREEN}✅ Vehicle added.")

def manage_vehicles(uid):
    df = fetch_df("SELECT vehicle_no,vehicle_brand,model,type FROM vehicles WHERE user_id=%s", (uid,))
    if df.empty:
        print(f"{BRIGHT_RED}No vehicles.")
        return
    print(f"\n{BRIGHT_CYAN}Your Vehicles:\n{df.to_string(index=False)}")
    vno = input(f"{BRIGHT_YELLOW}Vehicle No (Edit/Delete): ").strip()
    if not vno: return
    
    if input("1=Edit, 2=Delete: ").strip() == "1":
        row = df[df['vehicle_no']==vno].iloc[0] if not df[df['vehicle_no']==vno].empty else {}
        brand = input(f"Brand [{row.get('vehicle_brand','')}]: ").strip() or row.get('vehicle_brand','')
        model = input(f"Model [{row.get('model','')}]: ").strip() or row.get('model','')
        vtype = input(f"Type [{row.get('type','')}]: ").strip() or row.get('type','')
        exec_sql("UPDATE vehicles SET vehicle_brand=%s,model=%s,type=%s WHERE vehicle_no=%s AND user_id=%s",
                 (brand, model, vtype, vno, uid), success=f"{BRIGHT_GREEN}✅ Updated.")
    else:
        exec_sql("DELETE FROM vehicles WHERE vehicle_no=%s AND user_id=%s", (vno, uid), success=f"{BRIGHT_GREEN}✅ Deleted.")

# ================== SERVICES ==================
def browse_services():
    show_table("SELECT service_id,service_name,category,base_price,estimated_hours,warranty_months FROM services WHERE status='Active' ORDER BY category",
               title=f"{BRIGHT_CYAN}Available Services")

def book_service(uid):
    vdf = fetch_df("SELECT vehicle_no,vehicle_brand,model FROM vehicles WHERE user_id=%s", (uid,))
    if vdf.empty:
        print(f"{BRIGHT_RED}Add vehicle first.")
        return
    print(f"\n{BRIGHT_CYAN}Your Vehicles:\n{vdf.to_string(index=False)}")
    vno = input(f"{BRIGHT_YELLOW}Vehicle No: ").strip()
    if not vno: return
    
    show_table("SELECT service_id,service_name,category,base_price FROM services WHERE status='Active'", title=f"{BRIGHT_CYAN}Services")
    sid = input(f"{BRIGHT_YELLOW}Service ID: ").strip()
    if sid:
        exec_sql("INSERT INTO service_bookings(vehicle_no,service_id,booking_date,status) VALUES(%s,%s,NOW(),'Pending')",
                 (vno, sid), success=f"{BRIGHT_GREEN}✅ Booked.")
        exec_sql("INSERT INTO invoices(booking_id,user_id,amount,payment_status) VALUES(LAST_INSERT_ID(),%s,(SELECT base_price FROM services WHERE service_id=%s),'Unpaid')",
                 (uid, sid), success=f"{BRIGHT_GREEN}✅ Invoice created.")

# ================== PAYMENT ==================
def make_payment(uid):
    df = fetch_df("SELECT invoice_id,booking_id,amount FROM invoices WHERE user_id=%s AND payment_status='Unpaid'", (uid,))
    if df.empty:
        print(f"{BRIGHT_RED}No unpaid invoices.")
        return
    print(f"\n{BRIGHT_CYAN}Unpaid Invoices:\n{df.to_string(index=False)}")
    inv = input(f"{BRIGHT_YELLOW}Invoice ID: ").strip()
    if inv:
        method = input("Payment (Cash/Card/UPI/Bank) [Cash]: ").strip() or "Cash"
        exec_sql("UPDATE invoices SET payment_status='Pending',payment_method=%s WHERE invoice_id=%s", (method, inv), success=f"{BRIGHT_GREEN}✅ Payment done.")

# ================== VIEWS ==================
def show_user_view(uid, view_type):
    queries = {
        "history": ("SELECT b.booking_id,b.booking_date,b.status,v.vehicle_no,s.service_name FROM service_bookings b JOIN vehicles v ON b.vehicle_no=v.vehicle_no JOIN services s ON s.service_id=b.service_id WHERE v.user_id=%s ORDER BY b.booking_date DESC", "Booking History"),
        "track": ("SELECT b.booking_id,b.status,s.service_name,COALESCE(m.full_name,'-') mechanic FROM service_bookings b JOIN services s ON s.service_id=b.service_id JOIN vehicles v ON v.vehicle_no=b.vehicle_no LEFT JOIN mechanic_assignments ma ON ma.booking_id=b.booking_id LEFT JOIN mechanics_info m ON ma.mechanic_id=m.mechanic_id WHERE v.user_id=%s ORDER BY b.booking_date DESC", "Order Tracking"),
        "invoices": ("SELECT invoice_id,booking_id,amount,payment_status,payment_method,invoice_date FROM invoices WHERE user_id=%s ORDER BY invoice_date DESC", "Invoices"),
        "payments": ("SELECT invoice_id,amount,payment_status FROM invoices WHERE user_id=%s ORDER BY invoice_id DESC", "Payment Status")
    }
    show_table(queries[view_type][0], (uid,), f"{BRIGHT_CYAN}{queries[view_type][1]}")

def cancel_order(uid):
    show_table("SELECT b.booking_id,b.status,s.service_name,b.booking_date FROM service_bookings b JOIN services s ON b.service_id=s.service_id JOIN vehicles v ON v.vehicle_no=b.vehicle_no WHERE v.user_id=%s AND b.status IN ('Pending','In Progress')",
               (uid,), f"{BRIGHT_CYAN}Cancelable Orders")
    bid = input(f"{BRIGHT_YELLOW}Booking ID: ").strip()
    if bid:
        exec_sql("UPDATE service_bookings SET status='Cancelled' WHERE booking_id=%s", (bid,), success=f"{BRIGHT_GREEN}✅ Cancelled.")

def leave_feedback(uid):
    show_table("SELECT b.booking_id,s.service_name,b.booking_date FROM service_bookings b JOIN services s ON s.service_id=b.service_id JOIN vehicles v ON v.vehicle_no=b.vehicle_no LEFT JOIN feedback f ON f.booking_id=b.booking_id WHERE v.user_id=%s AND b.status='Completed' AND f.booking_id IS NULL",
               (uid,), f"{BRIGHT_CYAN}Pending Feedback")
    bid = input(f"{BRIGHT_YELLOW}Booking ID: ").strip()
    if bid:
        rating = int(input("Rating (1-5): ").strip() or 5)
        comment = input("Comments: ").strip()
        exec_sql("INSERT INTO feedback(booking_id,rating,comments,created_at) VALUES(%s,%s,%s,NOW())", (bid, rating, comment), success=f"{BRIGHT_GREEN}✅ Feedback submitted.")
