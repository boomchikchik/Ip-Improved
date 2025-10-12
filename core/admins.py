# =====================================================
#  Vehicle Garage Management System (CLI)
#  Role: ADMIN
#  Stage-1 Simplified & Styled Version
# =====================================================

import pandas as pd
from db.queries_sql import mycon, cursor, engcon
from styles import *
from core.utils_cli import pause, fetch_df, exec_sql, show_table, menu_box, dashboard_loop


# ================== AUTH ==================
def admin_login():
    while True:
        username = input(f"{BRIGHT_YELLOW}ENTER ADMIN USERNAME: ").strip()
        password = input(f"{BRIGHT_YELLOW}ENTER ADMIN PASSWORD: ").strip()
        if not (username and password):
            print(f"{BRIGHT_RED}❌ Username & Password required.")
            if input(f"{DIM_YELLOW}Press Enter or type 'exit': ").lower() == "exit":
                return
            continue

        df = fetch_df(
            "SELECT * FROM users WHERE username=%s AND password=%s AND user_role='admin'",
            (username, password),
        )
        if not df.empty:
            print(f"\n{BRIGHT_GREEN}✅ ADMIN LOGIN SUCCESSFUL!\n")
            print(df[["user_id", "username", "user_role"]].head(1))
            admin_dashboard(df)
            return
        print(f"{BRIGHT_RED}❌ Invalid credentials.\n")


# ================== USERS ==================
def create_user():
    name = input(f"{BRIGHT_YELLOW}Name: ").strip()
    username = input(f"{BRIGHT_YELLOW}Username: ").strip()
    email = input(f"{BRIGHT_YELLOW}Email: ").strip()
    phone = input(f"{BRIGHT_YELLOW}Phone: ").strip()
    address = input(f"{BRIGHT_YELLOW}Address: ").strip()
    city = input(f"{BRIGHT_YELLOW}City: ").strip()
    state = input(f"{BRIGHT_YELLOW}State: ").strip()
    password = input(f"{BRIGHT_YELLOW}Password: ").strip()
    role = input(f"{BRIGHT_YELLOW}Role (Admin/Mechanic/Customer): ").strip().title()

    if role.lower() == "mechanic":
        exec_sql("INSERT INTO mechanics_info(full_name,email) VALUES(%s,%s)", (name, email),
                 success=f"{BRIGHT_GREEN}✅ Mechanic profile created.")

    exec_sql(
        """INSERT INTO users(name,username,email,phone,address,city,state,password,user_role,registered_at)
           VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,NOW())""",
        (name, username, email, phone, address, city, state, password, role),
        success=f"{BRIGHT_GREEN}✅ User created successfully."
    )


def list_users():
    q = input(f"{DIM_YELLOW}Search (leave empty for all): ").strip()
    sql = """SELECT user_id,name,username,email,phone,user_role,registered_at
             FROM users WHERE name LIKE %s OR username LIKE %s OR email LIKE %s
             ORDER BY registered_at DESC""" if q else \
          """SELECT user_id,name,username,email,phone,user_role,registered_at
             FROM users ORDER BY registered_at DESC"""
    df = fetch_df(sql, (f"%{q}%", f"%{q}%", f"%{q}%") if q else None)
    print(df.to_string(index=False) if not df.empty else f"{BRIGHT_RED}No users found.")
    pause()


def update_user():
    uid = input(f"{BRIGHT_YELLOW}User ID to update: ").strip()
    field = input(f"{BRIGHT_YELLOW}Field (name, email, phone, address, city, state, username, password): ").strip()
    value = input(f"{BRIGHT_YELLOW}New value: ").strip()
    exec_sql(f"UPDATE users SET {field}=%s WHERE user_id=%s", (value, uid),
             success=f"{BRIGHT_GREEN}✅ User updated successfully.")


def delete_user():
    uid = input(f"{BRIGHT_YELLOW}User ID to delete: ").strip()
    exec_sql("DELETE FROM users WHERE user_id=%s", (uid,),
             success=f"{BRIGHT_GREEN}✅ User deleted successfully.")


def change_role():
    uid = input(f"{BRIGHT_YELLOW}User ID: ").strip()
    role = input(f"{BRIGHT_YELLOW}New role (Admin/Mechanic/Customer): ").strip().title()
    exec_sql("UPDATE users SET user_role=%s WHERE user_id=%s", (role, uid),
             success=f"{BRIGHT_GREEN}✅ Role updated successfully.")
    if role.lower() == "mechanic":
        info = fetch_df("SELECT name,email FROM users WHERE user_id=%s", (uid,))
        if not info.empty:
            n, e = info.iloc[0][["name", "email"]]
            exec_sql("INSERT INTO mechanics_info(full_name,email) VALUES(%s,%s)", (n, e),
                     success=f"{BRIGHT_GREEN}✅ Mechanic profile created.")


def reset_password():
    uid = input(f"{BRIGHT_YELLOW}User ID: ").strip()
    pwd = input(f"{BRIGHT_YELLOW}New Password: ").strip()
    exec_sql("UPDATE users SET password=%s WHERE user_id=%s", (pwd, uid),
             success=f"{BRIGHT_GREEN}✅ Password reset successfully.")


# ================== VEHICLES ==================
def add_vehicle():
    vno = input(f"{BRIGHT_YELLOW}Vehicle No: ").strip()
    brand = input(f"{BRIGHT_YELLOW}Brand: ").strip()
    model = input(f"{BRIGHT_YELLOW}Model: ").strip()
    vtype = input(f"{BRIGHT_YELLOW}Type (Car/Bike/...): ").strip().title()
    uid = input(f"{BRIGHT_YELLOW}Owner User ID: ").strip()
    exec_sql("""INSERT INTO vehicles(vehicle_no,vehicle_brand,model,type,user_id)
                VALUES(%s,%s,%s,%s,%s)""", (vno, brand, model, vtype, uid),
             success=f"{BRIGHT_GREEN}✅ Vehicle added successfully.")


def list_vehicles():
    q = input(f"{DIM_YELLOW}Search (vehicle_no/brand/model/owner): ").strip()
    sql = """SELECT v.vehicle_no,v.vehicle_brand,v.model,v.type,u.name AS owner
             FROM vehicles v JOIN users u ON v.user_id=u.user_id
             WHERE v.vehicle_no LIKE %s OR v.vehicle_brand LIKE %s OR v.model LIKE %s OR u.name LIKE %s
             ORDER BY v.vehicle_no""" if q else \
          """SELECT v.vehicle_no,v.vehicle_brand,v.model,v.type,u.name AS owner
             FROM vehicles v JOIN users u ON v.user_id=u.user_id ORDER BY v.vehicle_no"""
    df = fetch_df(sql, (f"%{q}%",)*4 if q else None)
    print(df.to_string(index=False) if not df.empty else f"{BRIGHT_RED}No vehicles found.")
    pause()


# ================== SERVICES ==================
def add_service():
    name = input(f"{BRIGHT_YELLOW}Service Name: ").strip()
    desc = input(f"{BRIGHT_YELLOW}Description: ").strip()
    price = float(input(f"{BRIGHT_YELLOW}Base Price: ") or 0)
    hours = float(input(f"{BRIGHT_YELLOW}Estimated Hours: ") or 0)
    warranty = int(input(f"{BRIGHT_YELLOW}Warranty Months: ") or 0)
    cat = input(f"{BRIGHT_YELLOW}Category: ").strip().title()
    status = input(f"{BRIGHT_YELLOW}Status (Active/Inactive): ").strip().title() or "Active"
    exec_sql("""INSERT INTO services(service_name,description,base_price,estimated_hours,
                warranty_months,category,status,created_at)
                VALUES(%s,%s,%s,%s,%s,%s,%s,NOW())""",
             (name, desc, price, hours, warranty, cat, status),
             success=f"{BRIGHT_GREEN}✅ Service added successfully.")


def list_services():
    show_table("""SELECT service_id,service_name,category,base_price,estimated_hours,
                  warranty_months,status,created_at FROM services ORDER BY created_at DESC""",
                title=f"{BRIGHT_CYAN}Service Catalog")


def update_service():
    sid = input(f"{BRIGHT_YELLOW}Service ID: ").strip()
    field = input(f"{BRIGHT_YELLOW}Field to update: ").strip()
    val = input(f"{BRIGHT_YELLOW}New Value: ").strip()
    exec_sql(f"UPDATE services SET {field}=%s WHERE service_id=%s", (val, sid),
             success=f"{BRIGHT_GREEN}✅ Service updated successfully.")


def toggle_service():
    sid = input(f"{BRIGHT_YELLOW}Service ID: ").strip()
    status = input(f"{BRIGHT_YELLOW}New Status (Active/Inactive): ").strip().title()
    exec_sql("UPDATE services SET status=%s WHERE service_id=%s", (status, sid),
             success=f"{BRIGHT_GREEN}✅ Status updated.")


# ================== MECHANICS ==================
def add_mechanic():
    name = input(f"{BRIGHT_YELLOW}Full Name: ").strip()
    spec = input(f"{BRIGHT_YELLOW}Specialization: ").strip()
    phone = input(f"{BRIGHT_YELLOW}Phone: ").strip()
    email = input(f"{BRIGHT_YELLOW}Email: ").strip()
    exec_sql("""INSERT INTO mechanics_info(full_name,specialization,phone,email)
                VALUES(%s,%s,%s,%s)""", (name, spec, phone, email),
             success=f"{BRIGHT_GREEN}✅ Mechanic added successfully.")
    exec_sql("""INSERT IGNORE INTO users(name,username,email,password,user_role,registered_at)
                VALUES(%s,%s,%s,%s,%s,NOW())""",
             (name, name, email, "mechanic123", "Mechanic"),
             success=f"{BRIGHT_GREEN}✅ Login profile created (Password: mechanic123).")


def list_mechanics():
    show_table("""SELECT mechanic_id,full_name,specialization,phone,email FROM mechanics_info""",
                title=f"{BRIGHT_CYAN}Mechanics List")


# ================== INVENTORY ==================
def add_part():
    name = input(f"{BRIGHT_YELLOW}Part Name: ").strip()
    desc = input(f"{BRIGHT_YELLOW}Description: ").strip()
    price = float(input(f"{BRIGHT_YELLOW}Unit Price: ") or 0)
    qty = int(input(f"{BRIGHT_YELLOW}Stock Quantity: ") or 0)
    supp = input(f"{BRIGHT_YELLOW}Supplier: ").strip()
    exec_sql("""INSERT INTO parts_inventory(part_name,description,unit_price,stock_quantity,supplier)
                VALUES(%s,%s,%s,%s,%s)""", (name, desc, price, qty, supp),
             success=f"{BRIGHT_GREEN}✅ Part added successfully.")


def list_parts():
    show_table("""SELECT part_id,part_name,unit_price,stock_quantity,supplier
                  FROM parts_inventory ORDER BY part_name""",
                title=f"{BRIGHT_CYAN}Parts Inventory")


# ================== INVOICES ==================
def generate_invoice():
    bid = input(f"{BRIGHT_YELLOW}Booking ID: ").strip()
    uid = input(f"{BRIGHT_YELLOW}User ID: ").strip()
    amt = float(input(f"{BRIGHT_YELLOW}Amount: ") or 0)
    pay = input(f"{BRIGHT_YELLOW}Payment Status (Pending/Paid/Failed): ").strip().title() or "Pending"
    method = input(f"{BRIGHT_YELLOW}Payment Method (Cash/Card/UPI/Bank): ").strip().title() or "Cash"
    exec_sql("""INSERT INTO invoices(booking_id,user_id,amount,payment_status,payment_method,invoice_date)
                VALUES(%s,%s,%s,%s,%s,NOW())""", (bid, uid, amt, pay, method),
             success=f"{BRIGHT_GREEN}✅ Invoice generated successfully.")


def list_invoices():
    show_table("""SELECT i.invoice_id,i.amount,i.payment_status,i.payment_method,i.invoice_date,u.name AS customer
                  FROM invoices i JOIN users u ON i.user_id=u.user_id
                  ORDER BY i.invoice_date DESC""",
                title=f"{BRIGHT_CYAN}Invoices List")


# ================== FEEDBACK / REPORTS ==================
def list_feedback():
    show_table("""SELECT f.feedback_id,f.rating,f.comments,f.created_at,
                         s.service_name,b.booking_id
                  FROM feedback f
                  JOIN service_bookings b ON f.booking_id=b.booking_id
                  JOIN services s ON b.service_id=s.service_id
                  ORDER BY f.created_at DESC""",
                title=f"{BRIGHT_CYAN}Customer Feedbacks")


def revenue_report():
    grp = input(f"{BRIGHT_YELLOW}Group by (D/W/M): ").strip().upper() or "D"
    if grp == "W":
        sql = """SELECT YEAR(invoice_date) y, WEEK(invoice_date) w, SUM(amount) revenue
                 FROM invoices GROUP BY y,w ORDER BY y DESC,w DESC"""
    elif grp == "M":
        sql = """SELECT YEAR(invoice_date) y, MONTH(invoice_date) m, SUM(amount) revenue
                 FROM invoices GROUP BY y,m ORDER BY y DESC,m DESC"""
    else:
        sql = """SELECT DATE(invoice_date) d, SUM(amount) revenue
                 FROM invoices GROUP BY d ORDER BY d DESC"""
    show_table(sql, title=f"{BRIGHT_CYAN}Revenue Report")


# ================== GENERIC SUBMENU ==================
def submenu(title, options):
    while True:
        ch = menu_box(title, {k: v[0] for k, v in options.items()})
        fn = options.get(ch, [None, None])[1]
        if fn:
            fn()
        elif ch == "0" or fn is None:
            print(f"{BRIGHT_MAGENTA}↩ Back to previous menu.")
            break


# ================== MAIN ADMIN DASHBOARD ==================
def admin_dashboard(df):
    admin = df.iloc[0]
    name = admin.get("name", "Admin")
    uid = str(admin.get("user_id", ""))
    print(f"{BRIGHT_GREEN}Welcome, {name}!{RESET}")

    dashboard_loop(f"{BRIGHT_CYAN}🚘 ADMIN DASHBOARD (ID: {uid}){RESET}", {
        "1": ("Manage Users", lambda: submenu("👥 USERS MENU", {
            "1": ("Create User", create_user),
            "2": ("List Users", list_users),
            "3": ("Update User", update_user),
            "4": ("Delete User", delete_user),
            "5": ("Change Role", change_role),
            "6": ("Reset Password", reset_password),
            "0": ("Back", None),
        })),
        "2": ("Vehicles", lambda: submenu("🚗 VEHICLES MENU", {
            "1": ("Add Vehicle", add_vehicle),
            "2": ("List Vehicles", list_vehicles),
            "3": ("Add Service", add_service),
            "4": ("List Services", list_services),
            "5": ("Update Service", update_service),
            "6": ("Toggle Service", toggle_service),
            "0": ("Back", None),
        })),
        "3": ("Mechanics", lambda: submenu("🧰 MECHANICS MENU", {
            "1": ("Add Mechanic", add_mechanic),
            "2": ("List Mechanics", list_mechanics),
            "0": ("Back", None),
        })),
        "4": ("Inventory", lambda: submenu("📦 INVENTORY MENU", {
            "1": ("Add Part", add_part),
            "2": ("List Parts", list_parts),
            "0": ("Back", None),
        })),
        "5": ("Invoices", lambda: submenu("🧾 INVOICES MENU", {
            "1": ("Generate Invoice", generate_invoice),
            "2": ("List Invoices", list_invoices),
            "0": ("Back", None),
        })),
        "6": ("Feedback", lambda: submenu("⭐ FEEDBACK MENU", {
            "1": ("View Feedbacks", list_feedback),
            "0": ("Back", None),
        })),
        "7": ("Reports", lambda: submenu("📈 REPORTS MENU", {
            "1": ("Revenue Report", revenue_report),
            "0": ("Back", None),
        })),
        "0": ("Logout", None),
    })
