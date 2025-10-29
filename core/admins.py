
import pandas as pd
from db.queries_sql import mycon, cursor, engcon
from styles import *
from core.graph import plot_from_sql
from core.utils_cli import pause, fetch_df, exec_sql, show_table, menu_box, dashboard_loop,dashboard_loop as submenu

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
    
def assign_mechanic():
    sql = """SELECT b.booking_id, s.service_name, v.vehicle_no, b.booking_date
             FROM service_bookings b
             JOIN services s ON b.service_id=s.service_id
             JOIN vehicles v ON b.vehicle_no=v.vehicle_no
             LEFT JOIN mechanic_assignments m ON b.booking_id=m.booking_id
             WHERE b.status='Pending' AND m.assignment_id IS NULL
             ORDER BY b.booking_date"""
    df = fetch_df(sql)
    if df.empty:
        print(f"{BRIGHT_RED}❌ No pending jobs."); return
    print(df.to_string(index=False))

    bid = input(f"{BRIGHT_YELLOW}Enter Booking ID: ").strip()
    mid = input(f"{BRIGHT_YELLOW}Enter Mechanic ID: ").strip()
    if not (bid and mid): return

    exec_sql("INSERT INTO mechanic_assignments(booking_id, mechanic_id, assigned_date) VALUES(%s,%s,NOW())",
             (bid, mid), success=f"{BRIGHT_GREEN}✅ Assigned.")
    exec_sql("UPDATE service_bookings SET status='In Progress' WHERE booking_id=%s",
             (bid,), success=f"{BRIGHT_GREEN}✅ Status → In Progress.")

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


def search_edit_invoice():
    inv = input(f"{BRIGHT_YELLOW}Invoice ID (blank to search): ").strip()
    if inv:
        sql = """SELECT i.invoice_id,i.booking_id,i.user_id,i.amount,i.payment_status,i.payment_method,i.invoice_date
                 FROM invoices i WHERE i.invoice_id=%s"""
        df = fetch_df(sql, (inv,))
    else:
        st = (input(f"{BRIGHT_YELLOW}Filter status [Unpaid/Paid/Pending/Failed/All]: ").strip().title() or "All")
        where = "" if st == "All" else "WHERE i.payment_status=%s"
        params = () if st == "All" else (st,)
        sql = f"""SELECT i.invoice_id,i.booking_id,i.user_id,i.amount,i.payment_status,i.payment_method,i.invoice_date
                  FROM invoices i {where} ORDER BY i.invoice_date DESC"""
        df = fetch_df(sql, params)

    if df.empty:
        print(f"{BRIGHT_RED}No invoices found."); pause(); return
    print(df.to_string(index=False))

    tid = input(f"{BRIGHT_YELLOW}Enter Invoice ID to edit status (blank to exit): ").strip()
    if not tid: 
        return
    val = input(f"{BRIGHT_YELLOW}New status [Unpaid,Paid/Pending/Failed]: ").strip().title()
    if val not in ('Unpaid',"Paid", "Pending", "Failed"):
        print(f"{BRIGHT_RED}Invalid status.") 
        pause()
        return
    exec_sql("UPDATE invoices SET payment_status=%s WHERE invoice_id=%s", (val, tid),
                success=f"{BRIGHT_GREEN}✅ Status updated.")




# ================== FEEDBACK / REPORTS ==================
def list_feedback():
    show_table("""SELECT f.feedback_id,f.rating,f.comments,f.created_at,
                         s.service_name,b.booking_id
                  FROM feedback f
                  JOIN service_bookings b ON f.booking_id=b.booking_id
                  JOIN services s ON b.service_id=s.service_id
                  ORDER BY f.created_at DESC""",
                title=f"{BRIGHT_CYAN}Customer Feedbacks")

def service_revenue_graph():
    """Show top 10 services by total revenue from invoices."""
    sql = """
        SELECT s.service_name, 
               COALESCE(SUM(i.amount), 0) AS total_revenue
        FROM services s
        LEFT JOIN service_bookings b ON s.service_id = b.service_id
        LEFT JOIN invoices i ON b.booking_id = i.booking_id
        GROUP BY s.service_name
        ORDER BY total_revenue DESC
        LIMIT 10
    """
    plot_from_sql(sql, "service_name", "total_revenue", "Top 10 Services by Revenue")

def top_service_bookings_graph():
    sql = """SELECT s.service_name, COUNT(b.booking_id) AS total_bookings
                FROM services s
                LEFT JOIN service_bookings b ON s.service_id=b.service_id
                GROUP BY s.service_name ORDER BY total_bookings DESC LIMIT 10"""
    plot_from_sql(sql, "service_name", "total_bookings", "Top 10 Services by Bookings")


vehicles_menu = {
    "1": ("Add Vehicle", add_vehicle),
    "2": ("List Vehicles", list_vehicles),
    "3": ("Add Service", add_service),
    "4": ("List Services", list_services),
    "5": ("Update Service", update_service),
    "6": ("Top Services by Revenue (Graph)", service_revenue_graph),
    "7": ("Top Services by Bookings (Graph)", top_service_bookings_graph),
    "0": ("Back", None),
}

# ================== MAIN ADMIN DASHBOARD ==================
def admin_dashboard(df):
    """Displays the main admin dashboard and handles navigation."""
    admin = df.iloc[0]  # Get info of logged-in admin
    name = admin.get("name", "Admin")
    uid = str(admin.get("user_id", ""))
    print(f"{BRIGHT_GREEN}Welcome, {name}!{RESET}")

    # --- Submenu Definitions ---
    user_menu = {
        "1": ("Create User", create_user), "2": ("List Users", list_users),
        "3": ("Update User", update_user), "4": ("Delete User", delete_user),
        "5": ("Change Role", change_role), "6": ("Reset Password", reset_password),
        "0": ("Back", None),
    }
    mechanics_menu = {
        "1": ("Add Mechanic", add_mechanic), "2": ("List Mechanics", list_mechanics),
        "3": ("Assign Mechanic to Booking", assign_mechanic),
        "0": ("Back", None),
    }
    inventory_menu = {
        "1": ("Add Part", add_part), "2": ("List Parts", list_parts),
        "0": ("Back", None),
    }
    invoices_menu = {
    "1": ("Generate Invoice", generate_invoice),"2": ("Search/Edit Invoice", search_edit_invoice),
    "0": ("Back", None),
    }
    feedback_menu = {
        "1": ("View Feedbacks", list_feedback), "0": ("Back", None),
    }
    reports_menu = {
        "1": ("Revenue Report (Table)", revenue_report),
        "2": ("Revenue Graph", revenue_graph),
        "3": ("Payment Status Graph", payment_status_graph),
        "4": ("Top Services by Revenue", service_revenue_graph),
        "0": ("Back", None),
    }
  # --- Main Dashboard Menu ---

    """lambda is necessary here to delay or defer the execution of the submenu function until the user explicitly chooses that option from the menu. It wraps the function call so it can be stored and executed later, rather than immediately"""
    
    main_menu = {
        "1": ("Manage Users", lambda: submenu("👥 USERS MENU", user_menu)),
        "2": ("Vehicles & Services", lambda: submenu("🚗 VEHICLES & SERVICES MENU", vehicles_menu)),
        "3": ("Mechanics", lambda: submenu("🧰 MECHANICS MENU", mechanics_menu)),
        "4": ("Inventory", lambda: submenu("📦 INVENTORY MENU", inventory_menu)),
        "5": ("Invoices", lambda: submenu("🧾 INVOICES MENU", invoices_menu)),
        "6": ("Feedback", lambda: submenu("⭐ FEEDBACK MENU", feedback_menu)),
        "7": ("Reports", lambda: submenu("📈 REPORTS MENU", reports_menu)),
        "0": ("Logout", None),
    }

    dashboard_loop(f"{BRIGHT_CYAN}🚘 ADMIN DASHBOARD (ID: {uid}){RESET}", main_menu)


def revenue_report(): 
    grp = input(f"{BRIGHT_YELLOW}Group by (D/W/M): ").strip().upper() or "D" 
    if grp == "W": 
        sql = """SELECT YEAR(invoice_date) y, WEEK(invoice_date) w, SUM(amount) revenue FROM invoices GROUP BY y,w ORDER BY y DESC,w DESC""" 
    elif grp == "M": 
        sql = """SELECT YEAR(invoice_date) y, MONTH(invoice_date) m, SUM(amount) revenue FROM invoices GROUP BY y,m ORDER BY y DESC,m DESC""" 
    else: 
        sql = """SELECT DATE(invoice_date) d, SUM(amount) revenue FROM invoices GROUP BY d ORDER BY d DESC""" 
    show_table(sql, title=f"{BRIGHT_CYAN}Revenue Report")

def revenue_graph():
    grp = input(f"{BRIGHT_YELLOW}Group by (D/M): ").strip().upper() or "D"
    kind = "barh" if grp == "D" else "bar"# You can change this to "bar" if you prefer

    if grp == "M":
        # Monthly revenue (strict-mode safe)
        sql = """
        SELECT DATE_FORMAT(invoice_date,'%%Y-%%m') AS period,
            SUM(amount) AS revenue
        FROM invoices
        GROUP BY period
        ORDER BY period;
        """

        title = f"{BRIGHT_CYAN}Monthly Revenue Trend"
    else:
        # Daily revenue
        sql = """
            SELECT DATE(invoice_date) AS period,
                   SUM(amount) AS revenue
            FROM invoices
            GROUP BY DATE(invoice_date)
            ORDER BY period
        """
        title = f"{BRIGHT_CYAN}Daily Revenue Trend"

    # Plot it
    plot_from_sql(sql, x_col="period", y_col="revenue", title=title, kind=kind)

def payment_status_graph():
    sql = """SELECT payment_status, COUNT(*) AS count
             FROM invoices GROUP BY payment_status"""
    plot_from_sql(sql, "payment_status", "count", "Payment Status", kind="pie")


def service_revenue_graph():
    sql = """SELECT s.service_name, COALESCE(SUM(i.amount),0) AS total_revenue
             FROM services s
             LEFT JOIN service_bookings b ON s.service_id=b.service_id
             LEFT JOIN invoices i ON b.booking_id=i.booking_id
             GROUP BY s.service_name ORDER BY total_revenue DESC LIMIT 10"""
    plot_from_sql(sql, "service_name", "total_revenue", "Top 10 Services by Revenue")
