# =====================================================
#  Vehicle Garage Management System (CLI)
#  Role: MECHANIC
#  Stage-1 Simplified & Styled Version
# =====================================================
import pandas as pd
import stdiomask
from tabulate import tabulate
from db.queries_sql import mycon, cursor, engcon
from styles import *
from core.utils_cli import pause, menu_box,fetch_df, exec_sql


# ================== Local Helpers ==================


def pick_from_df(df, title="Select by No.", show_index=True):
    if df.empty:
        print(f"{BRIGHT_RED}No records.")
        return None
    view = df.copy()
    if show_index:
        view.insert(0, "#", range(1, len(df) + 1))
    print(f"\n{BRIGHT_CYAN}{title}")
    print(tabulate(view, headers="keys", tablefmt="fancy_grid", showindex=False))
    try:
        n = int(input(f"{BRIGHT_YELLOW}Enter # (0 to cancel): "))
        if n == 0:
            return None
        if 1 <= n <= len(df):
            return df.iloc[n - 1]
    except ValueError:
        pass
    print(f"{BRIGHT_RED}Invalid choice.")
    return None


# ================== Status Logic ==================
_VALID_STATUSES = ["Pending", "In Progress", "Completed", "Cancelled"]
_ALLOWED_TRANSITIONS = {
    "Pending": {"In Progress", "Cancelled"},
    "In Progress": {"Completed", "Cancelled"},
    "Completed": set(),
    "Cancelled": set(),
}


# ================== LOGIN ==================
def mechanic_login():
    print(f"{BRIGHT_CYAN}🛠️ MECHANIC LOGIN")
    username = input(f"{BRIGHT_YELLOW}Username or Email: ").strip()
    password = stdiomask.getpass(f"{BRIGHT_YELLOW}Password: ").strip()

    if not username or not password:
        print(f"{BRIGHT_RED}❌ Username and password cannot be empty.")
        return

    q = """
        SELECT u.user_id, u.username, u.name, mi.mechanic_id, mi.full_name
          FROM users u
          JOIN mechanics_info mi ON mi.email = u.email
         WHERE (u.username=%s OR u.email=%s)
           AND u.password=%s
           AND u.user_role='Mechanic'
    """

    try:
        df = fetch_df(q, (username, username, password))
        if not df.empty:
            mech_id, full_name = df.iloc[0][["mechanic_id", "full_name"]]
            print(f"{BRIGHT_GREEN}✅ Login successful — Welcome {full_name} (ID: {mech_id})!")
            mechanic_dashboard(pd.DataFrame([{"mechanic_id": mech_id, "full_name": full_name}]))
        else:
            print(f"{BRIGHT_RED}❌ Invalid credentials.")
    except Exception as e:
        print(f"{BRIGHT_RED}DB Error: {e}")


# ================== DASHBOARD ==================
def mechanic_dashboard(logindf: pd.DataFrame):
    mech_id = int(logindf.iloc[0]["mechanic_id"])
    mech_name = str(logindf.iloc[0]["full_name"])

    while True:
        choice = menu_box(
            f"🛠️  MECHANIC DASHBOARD — {mech_name} (ID: {mech_id})",
            [
                "1) ✏️ Edit Profile",
                "2) 🔍 View Assigned Jobs",
                "3) 🔄 Update Job Status",
                "4) 🗂️ Job History",
                "0) 🚪 Logout",
            ],
            "Enter choice: "
        )

        if choice == "1":
            edit_profile(mech_id)
        elif choice == "2":
            view_assigned_jobs(mech_id)
        elif choice == "3":
            update_job_status(mech_id)
        elif choice == "4":
            job_history(mech_id)
        elif choice == "0":
            print(f"{BRIGHT_BLUE}👋 Logged out. See you soon!")
            break
        else:
            print(f"{BRIGHT_RED}Invalid option.")
            pause()


# ================== 1) Edit Profile ==================
def edit_profile(mechanic_id: int):
    print(f"\n{BRIGHT_CYAN}🧾 Edit Profile")
    field = input(f"{BRIGHT_YELLOW}Field (full_name, specialization, phone, email, password): ").strip()
    if field not in ("full_name", "specialization", "phone", "email", "password"):
        print(f"{BRIGHT_RED}Invalid field name.")
        pause()
        return
    value = input(f"{BRIGHT_YELLOW}New value for {field}: ").strip()
    if not value:
        print(f"{BRIGHT_RED}Value cannot be empty.")
        pause()
        return

    if field in ("email", "phone", "password"):
        exec_sql(f"UPDATE users SET {field}=%s WHERE email=(SELECT email FROM mechanics_info WHERE mechanic_id=%s)",
                 (value, mechanic_id),
                 ok=f"✅ Updated {field} in users table.")

    if field != "password":
        exec_sql(f"UPDATE mechanics_info SET {field}=%s WHERE mechanic_id=%s",
                 (value, mechanic_id),
                 ok=f"✅ Updated {field} in mechanic profile.")
    else:
        print(f"{BRIGHT_YELLOW}Note: Password updated in users table only.")
    pause()


# ================== 2) View Assigned Jobs ==================
def view_assigned_jobs(mechanic_id: int):
    q = """
        SELECT ma.assignment_id, sb.booking_id, sb.status, sb.booking_date,
               s.service_name, s.category, v.vehicle_no, v.vehicle_brand, v.model
          FROM mechanic_assignments ma
          JOIN service_bookings sb ON sb.booking_id = ma.booking_id
          JOIN services s ON s.service_id = sb.service_id
          JOIN vehicles v ON v.vehicle_no = sb.vehicle_no
         WHERE ma.mechanic_id = %s
         ORDER BY FIELD(sb.status, 'In Progress','Pending','Completed','Cancelled'),
                  sb.booking_date DESC
    """
    df = fetch_df(q, (mechanic_id,))
    if df.empty:
        print(f"{BRIGHT_RED}No assigned jobs yet.")
    else:
        print(f"\n{BRIGHT_CYAN}🔧 Assigned Jobs")
        print(tabulate(df, headers="keys", tablefmt="fancy_grid", showindex=False))
    pause()


# ================== 3) Update Job Status ==================
def update_job_status(mechanic_id: int):
    q = """
        SELECT sb.booking_id, sb.status, s.service_name,
               v.vehicle_no, v.vehicle_brand, v.model, sb.booking_date
          FROM mechanic_assignments ma
          JOIN service_bookings sb ON sb.booking_id = ma.booking_id
          JOIN services s ON s.service_id = sb.service_id
          JOIN vehicles v ON v.vehicle_no = sb.vehicle_no
         WHERE ma.mechanic_id=%s
         ORDER BY sb.booking_date DESC
    """
    df = fetch_df(q, (mechanic_id,))
    row = pick_from_df(df, title="Your Jobs")
    if row is None:
        return

    booking_id = int(row["booking_id"])
    current = str(row["status"])
    allowed = _ALLOWED_TRANSITIONS.get(current, set())
    if not allowed:
        print(f"{BRIGHT_RED}No valid transitions from '{current}'.")
        pause()
        return

    print(f"{BRIGHT_YELLOW}Current: {current}")
    print(f"{BRIGHT_YELLOW}Allowed → {', '.join(allowed)}")
    new_status = input(f"{BRIGHT_YELLOW}Enter new status: ").strip().title()
    if new_status not in allowed:
        print(f"{BRIGHT_RED}Invalid transition.")
        pause()
        return

    exec_sql("UPDATE service_bookings SET status=%s WHERE booking_id=%s",
             (new_status, booking_id),
             ok=f"✅ Status updated to {new_status} for Booking #{booking_id}")
    pause()


# ================== 4) Job History ==================
def job_history(mechanic_id: int):
    print(f"\n{BRIGHT_CYAN}🗂️ Job History")
    choice = menu_box(
        "Filter Options",
        ["1) ✅ Completed", "2) ⏳ Pending / In Progress", "3) ❌ Cancelled", "0) Back"],
        "Select: "
    )

    if choice == "0":
        return
    filters = {
        "1": ("Completed",),
        "2": ("Pending", "In Progress"),
        "3": ("Cancelled",)
    }
    status_filter = filters.get(choice)
    if not status_filter:
        print(f"{BRIGHT_RED}Invalid selection.")
        pause()
        return

    if len(status_filter) == 1:
        q = """
            SELECT sb.booking_id, sb.status, s.service_name, v.vehicle_no,
                   v.vehicle_brand, v.model, sb.booking_date
              FROM mechanic_assignments ma
              JOIN service_bookings sb ON sb.booking_id = ma.booking_id
              JOIN services s ON s.service_id = sb.service_id
              JOIN vehicles v ON v.vehicle_no = sb.vehicle_no
             WHERE ma.mechanic_id=%s AND sb.status=%s
             ORDER BY sb.booking_date DESC
        """
        df = fetch_df(q, (mechanic_id, status_filter[0]))
    else:
        placeholders = ",".join(["%s"] * len(status_filter))
        q = f"""
            SELECT sb.booking_id, sb.status, s.service_name, v.vehicle_no,
                   v.vehicle_brand, v.model, sb.booking_date
              FROM mechanic_assignments ma
              JOIN service_bookings sb ON sb.booking_id = ma.booking_id
              JOIN services s ON s.service_id = sb.service_id
              JOIN vehicles v ON v.vehicle_no = sb.vehicle_no
             WHERE ma.mechanic_id=%s AND sb.status IN ({placeholders})
             ORDER BY sb.booking_date DESC
        """
        df = fetch_df(q, (mechanic_id, *status_filter))

    if df.empty:
        print(f"{BRIGHT_RED}No jobs found for selected filter.")
    else:
        print(tabulate(df, headers="keys", tablefmt="fancy_grid", showindex=False))
    pause()
