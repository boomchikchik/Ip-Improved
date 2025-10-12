
import tkinter as tk

# Create a window
window = tk.Tk()

# Set title
window.title("My First GUI")

# Set window size
window.geometry("300x200")

# Run the application
window.mainloop()


# | Function                     | Purpose             | Common Arguments   |
# | ---------------------------- | ------------------- | ------------------ |
# | `tk.Tk()`                    | Creates main window | None               |
# | `window.title("...")`        | Title of the window | string             |
# | `window.geometry("300x200")` | Width x Height      | "widthxheight"     |
# | `window.mainloop()`          | Runs the window     | Must be at the end |
# ==============================================================================


# 🧱 Add Widgets (Buttons, Labels, Entry...)
# 📌 Label (text display)
# python
label = tk.Label(window, text="Hello, World!")
label.pack()

# | Argument             | Purpose              |
# | -------------------- | -------------------- |
# | `text="..."`         | What text to display |
# | `fg="red"`           | Text color           |
# | `bg="yellow"`        | Background color     |
# | `font=("Arial", 14)` | Font name and size   |


=================================================================

#📌 Button (clickable)

def on_click():
    print("Button clicked!")

button = tk.Button(window, text="Click Me", command=on_click)
button.pack()

# | Argument           | Purpose                  |
# | ------------------ | ------------------------ |
# | `text="..."`       | Button label             |
# | `command=...`      | Function to run on click |
# | `fg`, `bg`, `font` | Same as Label            |

=======================================================================
#📌 Entry (text input)

entry = tk.Entry(window)
entry.pack()

# To get text:
def show_text():
    print(entry.get())

btn = tk.Button(window, text="Show Entry", command=show_text)
btn.pack()
===============================================================

# 📌 Layout Management
# You can place widgets using:

pack() – simple, vertical

grid(row=0, column=0) – like a table

place(x=50, y=100) – absolute position


#SAMPLE PROGRAM 

import tkinter as tk

def greet():
    name = entry.get()
    label.config(text=f"Hello, {name}!")

window = tk.Tk()
window.title("Simple App")
window.geometry("300x150")

label = tk.Label(window, text="Enter your name:")
label.pack()

entry = tk.Entry(window)
entry.pack()

button = tk.Button(window, text="Greet", command=greet)
button.pack()

window.mainloop()


#--------------------------------------------------------






# | Widget        | Purpose               | Common Methods                  |
# | ------------- | --------------------- | ------------------------------- |
# | `Label`       | Display text          | `Label(...).config(text="New")` |
# | `Entry`       | Single-line input     | `.get()`                        |
# | `Button`      | Click to run function | `command=function_name`         |
# | `Text`        | Multi-line input      | `.get("1.0", tk.END)`           |
# | `Checkbutton` | Checkbox              | `IntVar().get()`                |
# | `Radiobutton` | Select one option     | `StringVar().get()`             |
# | `Listbox`     | Select from list      | `.get(tk.ACTIVE)`               |
# | `messagebox`  | Popup                 | `showinfo(title, message)`      |



# TIPS

# Always end with window.mainloop().

# Use pack() for simple layout, or grid() for rows/columns.

# Use pady and padx to give space.

# Use command=your_function to connect buttons.

def most_main_thing_here():
  pass #VIEW EXAMPLE BELOW TO UNDERSTAND TKINTER FULLY

# Import the tkinter module to create GUI apps
import tkinter as tk
from tkinter import messagebox  # Import messagebox to show popup messages

# --------------------- Create Main Window -----------------------
# This is your main application window (like a blank canvas)
window = tk.Tk()  # Create the main window
window.title("Tkinter Basics")  # Set the title (shown at top of window)
window.geometry("400x650")  # Set the size of the window (width x height)

# --------------------- 1. Label -----------------------
# Label is used to display static text (you can't type into it)
label = tk.Label(window, text="This is a Label", font=("Arial", 14), fg="blue")
label.pack(pady=10)  # 'pack()' places the label in the window, pady adds vertical space

# --------------------- 2. Entry (Single-line Input) -----------------------
# Entry allows users to type a single line of text
entry = tk.Entry(window, width=30)  # width sets how wide the input box will be
entry.pack()  # Place it in the window

# Function to run when button is clicked
def show_entry_text():
    text = entry.get()  # .get() gets the text user typed in Entry box
    messagebox.showinfo("Entry Text", f"You entered: {text}")  # Show it in popup

# Button to show the Entry text
btn_entry = tk.Button(window, text="Show Entry Text", command=show_entry_text)
btn_entry.pack(pady=5)

# --------------------- 3. Button (Click Action) -----------------------
# This button changes the label text when clicked
def on_button_click():
    label.config(text="Button Clicked!")  # Change text of the label

btn = tk.Button(window, text="Click Me", command=on_button_click, bg="lightgreen")
btn.pack(pady=5)

# --------------------- 4. Text (Multi-line Input with Scrollbar) -----------------------
# Text widget allows the user to enter multiple lines of text

# Frame groups widgets together (Text + Scrollbar)
frame = tk.Frame(window)
frame.pack()

# Create a scrollbar inside the frame
scrollbar = tk.Scrollbar(frame)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)  # Place on the right side of the frame

# Create Text widget (multi-line input box)
text_box = tk.Text(frame, height=5, width=40, yscrollcommand=scrollbar.set)
text_box.pack(side=tk.LEFT)

# Link scrollbar with the text box
scrollbar.config(command=text_box.yview)

# Insert some default text in the text box
text_box.insert(tk.END, "Type here...\nTry typing more to see the scroll in action.")

# Function to show content of the text box
def show_textbox_content():
    content = text_box.get("1.0", tk.END)  # Get all text from line 1, character 0 to end
    messagebox.showinfo("Text Content", content)

btn_text = tk.Button(window, text="Show Text Box Content", command=show_textbox_content)
btn_text.pack(pady=5)

# --------------------- 5. Checkbutton (Checkbox) -----------------------
# Checkbutton lets users choose True/False or Yes/No options

check_var = tk.IntVar()  # Variable to store checkbox state: 0 (unchecked), 1 (checked)

# Create the checkbox
check_btn = tk.Checkbutton(window, text="Check Me", variable=check_var)
check_btn.pack()

# Function to show checkbox state
def check_status():
    if check_var.get() == 1:
        messagebox.showinfo("Checkbutton", "Checkbox is Checked")
    else:
        messagebox.showinfo("Checkbutton", "Checkbox is NOT Checked")

btn_check = tk.Button(window, text="Check Status", command=check_status)
btn_check.pack(pady=5)

# --------------------- 6. Radiobutton (Choose One Option) -----------------------
# Radiobuttons allow only one option to be selected at a time

radio_var = tk.StringVar(value="None")  # Store which radio option is selected

# Label for this section
tk.Label(window, text="Choose an Option:").pack()

# Two radiobuttons
radio1 = tk.Radiobutton(window, text="Option A", variable=radio_var, value="A")
radio2 = tk.Radiobutton(window, text="Option B", variable=radio_var, value="B")
radio1.pack()
radio2.pack()

# Function to show selected option
def show_radio_selection():
    selected = radio_var.get()
    messagebox.showinfo("Radiobutton", f"Selected: {selected}")

btn_radio = tk.Button(window, text="Show Selected Option", command=show_radio_selection)
btn_radio.pack(pady=5)

# --------------------- 7. Listbox (Select From a List) -----------------------
# Listbox displays multiple items; user can select one

tk.Label(window, text="Select Item from List:").pack()

listbox = tk.Listbox(window)  # Create the listbox
items = ["Apple", "Banana", "Cherry", "Date"]  # Items to add

# Insert each item into the listbox
for item in items:
    listbox.insert(tk.END, item)  # tk.END means insert at the end

listbox.pack()

# Function to show selected item
def show_selected_item():
    selected = listbox.get(tk.ACTIVE)  # Get the item currently selected
    messagebox.showinfo("Listbox", f"You selected: {selected}")

btn_list = tk.Button(window, text="Show Selected Item", command=show_selected_item)
btn_list.pack(pady=5)

# --------------------- 8. MessageBox (Simple Popup) -----------------------
# Function to show a simple message popup
def show_popup():
    messagebox.showinfo("Hello", "This is a message box!")

btn_popup = tk.Button(window, text="Show Popup", command=show_popup)
btn_popup.pack(pady=10)

# --------------------- Start the GUI -----------------------
# This keeps the window open and waits for user actions (click, type, etc.)
window.mainloop()

#----------------------------------------------------------------------------------------
def multiple_frames_tkinter():
  pass # VIEW BELOW EXAMPLE GIVEN

import tkinter as tk

# -------------------- Setup Main Window --------------------
root = tk.Tk()
root.title("Page Navigation Example")
root.geometry("400x300")

# -------------------- Define Pages as Frames --------------------
# Main Page Frame
main_frame = tk.Frame(root)

# User Page Frame
user_frame = tk.Frame(root)

# -------------------- MAIN PAGE CONTENT --------------------
def show_main():
    user_frame.pack_forget()  # Hide user page
    main_frame.pack(fill="both", expand=True)  # Show main page

label_main = tk.Label(main_frame, text="Main Page", font=("Arial", 16))
label_main.pack(pady=20)

btn_to_user = tk.Button(main_frame, text="Go to User Page", command=lambda: show_user())
btn_to_user.pack()

# -------------------- USER PAGE CONTENT --------------------
def show_user():
    main_frame.pack_forget()  # Hide main page
    user_frame.pack(fill="both", expand=True)  # Show user page

label_user = tk.Label(user_frame, text="User Page", font=("Arial", 16))
label_user.pack(pady=20)

btn_back = tk.Button(user_frame, text="Back to Main", command=lambda: show_main())
btn_back.pack()

# -------------------- Start with Main Page --------------------
show_main()

# -------------------- Run the Window --------------------
root.mainloop()

