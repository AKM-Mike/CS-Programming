import tkinter as tk
from tkinter import ttk, messagebox
import csv
import os

FILE_PATH = os.path.join(os.getcwd(),"music.csv") ###This is file path###

###This is main window###
root = tk.Tk()
root.geometry("600x800")
root.iconbitmap(os.path.join(os.getcwd(),"Logo.ico"))
root.title("CSV Table Viewer")

tk.Label(root, text="CSV TABLE VIEWER", font=("Arial", 14)).pack(pady=5)

# Search bar
search_frame = tk.Frame(root)  ###Create a container###
search_frame.pack(pady=5)
search_label = tk.Label(search_frame, text="Search:")
search_label.pack(side="left")
search_entry = tk.Entry(search_frame)
search_entry.pack(side="left", padx=5)
search_button = tk.Button(search_frame, text="Search")
search_button.pack(side="left")

# Treeview + Scrollbars
tree_frame = tk.Frame(root)
tree_frame.pack(fill="both", padx=10, pady=5)

vsb = tk.Scrollbar(tree_frame, orient="vertical")
vsb.pack(side="right", fill="y")
hsb = tk.Scrollbar(tree_frame, orient="horizontal")
hsb.pack(side="bottom", fill="x")

tree = ttk.Treeview(tree_frame,height=10, yscrollcommand=vsb.set, xscrollcommand=hsb.set)
tree.pack(side="left", fill="both", expand=True)

vsb.config(command=tree.yview)
hsb.config(command=tree.xview)

# Entry form
form_frame = tk.Frame(root)
form_frame.pack(pady=10)

entries = []

def clear_form():  ###For clearing things in entry###
    for entry in entries:
        entry.delete(0, tk.END)

def load():  ###read file and load it in,Let's go!###
    for row in tree.get_children():
        tree.delete(row)

    if not os.path.exists(FILE_PATH):
        messagebox.showerror("Error", f"File not found:\n{FILE_PATH}")
        return

    with open(FILE_PATH, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        try:
            headers = next(reader)
        except StopIteration:
            messagebox.showinfo("Info", "CSV file is empty.")
            return

        tree["columns"] = headers
        tree["show"] = "headings"

        for col in tree["columns"]:
            tree.heading(col, text=col)
            tree.column(col, anchor="center", width=100, stretch=True)

        for row in reader:
            tree.insert("", tk.END, values=row)

    # Generate entry fields
    for widget in form_frame.winfo_children():
        widget.destroy()
    entries.clear()

    for i, header in enumerate(headers):
        tk.Label(form_frame, text=header + ":", anchor="w", width=20).grid(row=i, column=0, sticky="w", padx=5, pady=3)
        entry = tk.Entry(form_frame, width=50)
        entry.grid(row=i, column=1, padx=5, pady=3)
        entries.append(entry)

    search_label.config(text=f"Search by any field (e.g. {', '.join(tree['columns'][:2])}):")

load()

def add_row():
    new_data = [entry.get().strip() for entry in entries]
    if not all(new_data):
        messagebox.showwarning("Warning", "All fields must be filled.")
        return

    with open(FILE_PATH, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(new_data)
    load()
    clear_form()

def delete_row():
    selected = tree.selection()
    if not selected:
        return messagebox.showinfo("Info", "Select a row to delete.")

    # Get selected row values and convert to strings for safe comparison
    values = [str(v).strip() for v in tree.item(selected[0])["values"]]

    new_rows = []
    with open(FILE_PATH, newline='', encoding='utf-8') as f:
        reader = list(csv.reader(f))
        headers = reader[0]
        for row in reader[1:]:
            # Compare normalized strings
            if [cell.strip() for cell in row] != values:
                new_rows.append(row)

    # Write updated rows back to file
    with open(FILE_PATH, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(new_rows)

    load()  # Refresh the treeview


def fill_form(event):
    selected = tree.selection()
    if selected:
        values = tree.item(selected[0])["values"]
        for i, value in enumerate(values):
            entries[i].delete(0, tk.END)
            entries[i].insert(0, value)

def update_row():
    selected = tree.selection()
    if not selected:
        return messagebox.showinfo("Info", "Select a row to update.")

    new_data = [entry.get().strip() for entry in entries]
    if not all(new_data):
        return messagebox.showwarning("Warning", "All fields must be filled.")

    old_values = tree.item(selected[0])["values"]

    updated_rows = []
    with open(FILE_PATH, newline='', encoding='utf-8') as f:
        reader = list(csv.reader(f))
        headers = reader[0]
        for row in reader[1:]:
            if row == old_values:
                updated_rows.append(new_data)
            else:
                updated_rows.append(row)

    with open(FILE_PATH, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(updated_rows)

    load()
    clear_form()

def search_data():
    keyword = search_entry.get().strip().lower()
    if not keyword:
        return load()

    for row in tree.get_children():
        tree.delete(row)

    with open(FILE_PATH, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        headers = next(reader)
        tree["columns"] = headers
        tree["show"] = "headings"

        for col in tree["columns"]:
            tree.heading(col, text=col)
            tree.column(col, anchor="center", width=100, stretch=True)

        for row in reader:
            if any(keyword in cell.lower() for cell in row):
                tree.insert("", tk.END, values=row)

# Buttons
btn_frame = tk.Frame(root)
btn_frame.pack(pady=10)
tk.Button(btn_frame, text="Add", command=add_row).pack(side="left", padx=5)
tk.Button(btn_frame, text="Update", command=update_row).pack(side="left", padx=5)
tk.Button(btn_frame, text="Delete", command=delete_row).pack(side="left", padx=5)
tk.Button(btn_frame, text="Refresh", command=load).pack(side="left", padx=5)
tk.Button(btn_frame, text="Exit", command=root.destroy).pack(side="left", padx=5)

tree.bind("<<TreeviewSelect>>", fill_form)
search_button.config(command=search_data)

root.mainloop()
