# =====================================================
#  Vehicle Garage Management System (CLI)
#  Role: USER
#  Stage-1 Simplified & Styled (no RESET)
# =====================================================

import pandas as pd
import stdiomask
from db.queries_sql import mycon, cursor, engcon
from styles import *
from core.utils_cli import pause, fetch_df, exec_sql, show_table, menu_box


# ================== 1️⃣ USER REGISTRATION ==================
def user_registration():
    print(f"{BRIGHT_CYAN}\n🧾 USER REGISTRATION")

    while True:
        name = input(f"{BRIGHT_YELLOW}Enter your Name: ").strip()
        if name.replace(" ", "").isalpha():
            break
        print(f"{BRIGHT_RED}❌ Invalid name. Use letters only.")

    while True:
        email = input(f"{BRIGHT_YELLOW}Enter your Email: ").strip()
        if "@" in email and "." in email:
            break
        print(f"{BRIGHT_RED}❌ Invalid email format.")

    while True:
        phone = input(f"{BRIGHT_YELLOW}Enter Phone (10-12 digits): ").strip()
        if phone.isdigit() and len(phone) in [10, 11, 12]:
            break
        print(f"{BRIGHT_RED}❌ Invalid phone number.")

    address = input(f"{BRIGHT_YELLOW}Enter Address: ").strip()
    city = input(f"{BRIGHT_YELLOW}Enter City: ").strip()
    state = input(f"{BRIGHT_YELLOW}Enter State: ").strip()
    username = input(f"{BRIGHT_YELLOW}Create Username: ").strip()

    while True:
        password = stdiomask.getpass(f"{BRIGHT_YELLOW}Create Password: ")
        confirm = stdiomask.getpass(f"{BRIGHT_YELLOW}Confirm Password: ")
        if len(password) < 6:
            print(f"{BRIGHT_RED}❌ Password too short (min 6 chars).")
        elif password != confirm:
            print(f"{BRIGHT_RED}❌ Passwords don’t match.")
        else:
            break

    df = pd.DataFrame([{
        "name": name, "email": email, "phone": phone,
        "address": address, "city": city, "state": state,
        "username": username, "password": password,
        "user_role": "Customer"
    }])
    try:
        df.to_sql("users", con=engcon, if_exists="append", index=False)
        print(f"{BRIGHT_GREEN}✅ Registration successful! You can now log in.")
    except Exception as e:
        print(f"{BRIGHT_RED}❌ Registration failed: {e}")


# ================== 2️⃣ USER LOGIN ==================
def user_login():
    print(f"{BRIGHT_CYAN}\n🔐 USER LOGIN")
    while True:
        username = input(f"{BRIGHT_YELLOW}Username or Email: ").strip()
        password = stdiomask.getpass(f"{BRIGHT_YELLOW}Password: ")

        if not (username and password):
            print(f"{BRIGHT_RED}❌ Both fields required.")
            continue

        q = """SELECT * FROM users WHERE (username=%s OR email=%s) AND password=%s"""
        df = fetch_df(q, (username, username, password))
        if df.empty:
            print(f"{BRIGHT_RED}❌ Invalid credentials.")
            if input(f"{DIM_YELLOW}Press Enter to retry or type 'exit': ").lower() == "exit":
                return
        else:
            print(f"{BRIGHT_GREEN}✅ Login successful!")
            print(df[["user_id", "username", "user_role"]].head(1))
            user_dashboard(df)
            return


# ================== 3️⃣ USER DASHBOARD ==================
def user_dashboard(df):
    user = df.iloc[0]
    uid = int(user["user_id"])
    uname = user["name"]

    while True:
        print(f"\n{BRIGHT_CYAN}===== USER DASHBOARD =====")
        print(f"{BRIGHT_GREEN}Welcome, {uname}!")

        print(f"""
{BRIGHT_YELLOW}1.{BRIGHT_CYAN} View / Update Profile
{BRIGHT_YELLOW}2.{BRIGHT_CYAN} Add Vehicle
{BRIGHT_YELLOW}3.{BRIGHT_CYAN} Manage Vehicles
{BRIGHT_YELLOW}4.{BRIGHT_CYAN} Browse Services
{BRIGHT_YELLOW}5.{BRIGHT_CYAN} Book Service
{BRIGHT_YELLOW}6.{BRIGHT_CYAN} Make Payment
{BRIGHT_YELLOW}7.{BRIGHT_CYAN} View Booking History
{BRIGHT_YELLOW}8.{BRIGHT_CYAN} Track Order
{BRIGHT_YELLOW}9.{BRIGHT_CYAN} Cancel Order
{BRIGHT_YELLOW}10.{BRIGHT_CYAN} View / Download Invoice
{BRIGHT_YELLOW}11.{BRIGHT_CYAN} Check Payment Status
{BRIGHT_YELLOW}12.{BRIGHT_CYAN} Leave Feedback
{BRIGHT_MAGENTA}0.{BRIGHT_CYAN} Logout
{BRIGHT_RED}Q.{BRIGHT_CYAN} Exit
""")

        choice = input(f"{BRIGHT_YELLOW}Enter your choice: ").strip().lower()

        if choice == "q":
            print(f"{BRIGHT_RED}Exiting dashboard.")
            break
        elif choice == "0":
            print(f"{BRIGHT_MAGENTA}↩ Logging out...")
            break
        elif choice == "1":
            view_or_update_profile(uid)
        elif choice == "2":
            add_vehicle(uid)
        elif choice == "3":
            manage_vehicles(uid)
        elif choice == "4":
            browse_services()
        elif choice == "5":
            book_service(uid)
        elif choice == "6":
            make_payment(uid)
        elif choice == "7":
            view_booking_history(uid)
        elif choice == "8":
            track_order(uid)
        elif choice == "9":
            cancel_order(uid)
        elif choice == "10":
            view_or_download_invoice(uid)
        elif choice == "11":
            check_payment_status(uid)
        elif choice == "12":
            leave_feedback(uid)
        else:
            print(f"{BRIGHT_RED}❌ Invalid choice. Try again.")


# ================== 4️⃣ VIEW / UPDATE PROFILE ==================
def view_or_update_profile(uid):
    q = """SELECT user_id,name,email,phone,address,city,state,username,password FROM users WHERE user_id=%s"""
    df = fetch_df(q, (uid,))
    if df.empty:
        print(f"{BRIGHT_RED}❌ User not found.")
        return

    row = df.iloc[0]
    print(f"\n{BRIGHT_CYAN}Your Profile:")
    print(row[['user_id', 'name', 'email', 'phone', 'address', 'city', 'state', 'username']].to_string())

    print(f"\n{BRIGHT_YELLOW}1) Edit Profile   2) Change Password   3) Back")
    ch = input("Enter choice: ").strip()
    if ch == "1":
        name = input(f"New Name [{row['name']}]: ").strip() or row['name']
        email = input(f"New Email [{row['email']}]: ").strip() or row['email']
        phone = input(f"New Phone [{row['phone']}]: ").strip() or row['phone']
        address = input(f"New Address [{row['address']}]: ").strip() or row['address']
        city = input(f"New City [{row['city']}]: ").strip() or row['city']
        state = input(f"New State [{row['state']}]: ").strip() or row['state']
        exec_sql("""UPDATE users SET name=%s,email=%s,phone=%s,address=%s,city=%s,state=%s WHERE user_id=%s""",
                 (name, email, phone, address, city, state, uid),
                 ok=f"{BRIGHT_GREEN}✅ Profile updated.")
    elif ch == "2":
        old = stdiomask.getpass("Old Password: ")
        check = fetch_df("SELECT user_id FROM users WHERE user_id=%s AND password=%s", (uid, old))
        if check.empty:
            print(f"{BRIGHT_RED}❌ Incorrect old password.")
            return
        while True:
            new = stdiomask.getpass("New Password: ")
            conf = stdiomask.getpass("Confirm Password: ")
            if new != conf:
                print(f"{BRIGHT_RED}❌ Mismatch. Try again.")
            elif len(new) < 6:
                print(f"{BRIGHT_RED}❌ Too short.")
            else:
                break
        exec_sql("UPDATE users SET password=%s WHERE user_id=%s", (new, uid),
                 ok=f"{BRIGHT_GREEN}✅ Password changed.")


# ================== 5️⃣ ADD VEHICLE ==================
def add_vehicle(uid):
    print(f"{BRIGHT_CYAN}\n🚗 ADD VEHICLE")
    vno = input("Vehicle No: ").strip()
    brand = input("Brand: ").strip()
    model = input("Model: ").strip()
    vtype = input("Type (Car/Bike/Truck/Bus/Tractor/Other): ").strip().title()
    df = pd.DataFrame([{"vehicle_no": vno, "vehicle_brand": brand, "model": model, "type": vtype, "user_id": uid}])
    try:
        df.to_sql("vehicles", con=engcon, if_exists="append", index=False)
        print(f"{BRIGHT_GREEN}✅ Vehicle added successfully.")
    except Exception as e:
        print(f"{BRIGHT_RED}❌ Failed to add vehicle: {e}")


# ================== 6️⃣ MANAGE VEHICLES ==================
def manage_vehicles(uid):
    df = fetch_df("SELECT vehicle_no,vehicle_brand,model,type FROM vehicles WHERE user_id=%s", (uid,))
    if df.empty:
        print(f"{BRIGHT_RED}No vehicles found.")
        return
    print(f"\n{BRIGHT_CYAN}Your Vehicles")
    print(df.to_string(index=False))
    vno = input("Enter Vehicle No to edit/delete (blank cancel): ").strip()
    if not vno:
        return
    print("1) Edit  2) Delete")
    act = input("Choose: ").strip()
    if act == "1":
        brand = input("New Brand: ").strip() or df.iloc[0]['vehicle_brand']
        model = input("New Model: ").strip() or df.iloc[0]['model']
        vtype = input("New Type: ").strip() or df.iloc[0]['type']
        exec_sql("UPDATE vehicles SET vehicle_brand=%s,model=%s,type=%s WHERE vehicle_no=%s AND user_id=%s",
                 (brand, model, vtype, vno, uid),
                 ok=f"{BRIGHT_GREEN}✅ Vehicle updated.")
    elif act == "2":
        exec_sql("DELETE FROM vehicles WHERE vehicle_no=%s AND user_id=%s", (vno, uid),
                 ok=f"{BRIGHT_GREEN}✅ Vehicle deleted.")


# ================== 7️⃣ BROWSE SERVICES ==================
def browse_services():
    show_table("""SELECT service_id,service_name,category,base_price,estimated_hours,warranty_months
                  FROM services WHERE status='Active' ORDER BY category,service_name""",
                title=f"{BRIGHT_CYAN}Available Services")


# ================== 8️⃣ BOOK SERVICE ==================
def book_service(uid):
    vdf = fetch_df("SELECT vehicle_no,vehicle_brand,model FROM vehicles WHERE user_id=%s", (uid,))
    if vdf.empty:
        print(f"{BRIGHT_RED}No vehicles. Add one first.")
        return
    print(f"\n{BRIGHT_CYAN}Your Vehicles")
    print(vdf.to_string(index=False))
    vno = input("Vehicle No: ").strip()
    if not vno:
        return
    show_table("SELECT service_id,service_name,category,base_price FROM services WHERE status='Active'",
               title=f"{BRIGHT_CYAN}Services List")
    sid = input("Enter Service ID: ").strip()
    if not sid:
        return
    exec_sql("INSERT INTO service_bookings(vehicle_no,service_id,booking_date,status) VALUES(%s,%s,NOW(),'Pending')",
             (vno, sid),
             ok=f"{BRIGHT_GREEN}✅ Service booked (Pending).")


# ================== 9️⃣ PAYMENT ==================
def make_payment(uid):
    df = fetch_df("SELECT invoice_id,booking_id,amount,payment_status FROM invoices WHERE user_id=%s AND payment_status='Pending'",
                  (uid,))
    if df.empty:
        print(f"{BRIGHT_RED}No pending invoices.")
        return
    print(f"\n{BRIGHT_CYAN}Pending Invoices")
    print(df.to_string(index=False))
    inv = input("Invoice ID to pay: ").strip()
    if not inv:
        return
    method = input("Payment Method (Cash/Card/UPI/Bank): ").strip() or "Cash"
    exec_sql("UPDATE invoices SET payment_status='Paid',payment_method=%s,invoice_date=NOW() WHERE invoice_id=%s AND user_id=%s",
             (method, inv, uid),
             ok=f"{BRIGHT_GREEN}✅ Payment successful.")


# ================== 10️⃣ HISTORY / TRACK / CANCEL / INVOICE / FEEDBACK ==================
def view_booking_history(uid):
    show_table("""SELECT b.booking_id,b.booking_date,b.status,v.vehicle_no,s.service_name
                  FROM service_bookings b JOIN vehicles v ON b.vehicle_no=v.vehicle_no
                  JOIN services s ON s.service_id=b.service_id
                  WHERE v.user_id=%s ORDER BY b.booking_date DESC""",
                (uid,), f"{BRIGHT_CYAN}Booking History")


def track_order(uid):
    show_table("""SELECT b.booking_id,b.status,s.service_name,COALESCE(m.full_name,'-') mechanic
                  FROM service_bookings b JOIN services s ON s.service_id=b.service_id
                  JOIN vehicles v ON v.vehicle_no=b.vehicle_no
                  LEFT JOIN mechanic_assignments ma ON ma.booking_id=b.booking_id
                  LEFT JOIN mechanics_info m ON ma.mechanic_id=m.mechanic_id
                  WHERE v.user_id=%s ORDER BY b.booking_date DESC""",
                (uid,), f"{BRIGHT_CYAN}Order Tracking")


def cancel_order(uid):
    show_table("""SELECT b.booking_id,b.status,s.service_name,b.booking_date
                  FROM service_bookings b JOIN services s ON b.service_id=s.service_id
                  JOIN vehicles v ON v.vehicle_no=b.vehicle_no
                  WHERE v.user_id=%s AND b.status IN ('Pending','In Progress')""",
                (uid,), f"{BRIGHT_CYAN}Cancelable Orders")
    bid = input("Booking ID to cancel: ").strip()
    if not bid:
        return
    exec_sql("UPDATE service_bookings SET status='Cancelled' WHERE booking_id=%s", (bid,),
             ok=f"{BRIGHT_GREEN}✅ Booking cancelled.")


def view_or_download_invoice(uid):
    show_table("""SELECT invoice_id,booking_id,amount,payment_status,payment_method,invoice_date
                  FROM invoices WHERE user_id=%s ORDER BY invoice_date DESC""",
                (uid,), f"{BRIGHT_CYAN}Invoices")


def check_payment_status(uid):
    show_table("SELECT invoice_id,amount,payment_status FROM invoices WHERE user_id=%s ORDER BY invoice_id DESC",
               (uid,), f"{BRIGHT_CYAN}Payment Status")


def leave_feedback(uid):
    show_table("""SELECT b.booking_id,s.service_name,b.booking_date
                  FROM service_bookings b JOIN services s ON s.service_id=b.service_id
                  JOIN vehicles v ON v.vehicle_no=b.vehicle_no
                  LEFT JOIN feedback f ON f.booking_id=b.booking_id
                  WHERE v.user_id=%s AND b.status='Completed' AND f.booking_id IS NULL""",
                (uid,), f"{BRIGHT_CYAN}Feedback Pending")
    bid = input("Booking ID to review: ").strip()
    if not bid:
        return
    rating = int(input("Rating (1-5): ").strip() or 5)
    comment = input("Comments: ").strip()
    exec_sql("INSERT INTO feedback(booking_id,rating,comments,created_at) VALUES(%s,%s,%s,NOW())",
             (bid, rating, comment),
             ok=f"{BRIGHT_GREEN}✅ Feedback submitted.")
