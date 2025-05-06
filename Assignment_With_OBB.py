import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
import os

class CSV_Viewer:
    def __init__(self, root):
        self.root = root
        self.root.geometry("700x700")
        self.root.iconbitmap(os.path.join(os.getcwd(), "Logo.ico"))
        self.root.title("CSV Table Viewer")
        self.FILE_PATH = os.path.join(os.getcwd(), "music.csv")
        self.entries = []
        self.search_column_var = tk.StringVar(self.root)
        self.search_column_var.set("All Fields")

        self._create_widgets()
        self._load_data()

    def _create_widgets(self):
        tk.Label(self.root, text="CSV TABLE VIEWER", font=("Arial", 14)).pack(pady=5)

        # Search bar
        search_frame = tk.Frame(self.root)
        search_frame.pack(pady=5)
        search_label = tk.Label(search_frame, text="Search in:")
        search_label.pack(side="left")
        search_column_menu = ttk.Combobox(search_frame, textvariable=self.search_column_var, values=["All Fields"])
        search_column_menu.pack(side="left", padx=5)
        self.search_entry = tk.Entry(search_frame)
        self.search_entry.pack(side="left", padx=5)
        search_button = tk.Button(search_frame, text="Search", command=self._search_data)
        search_button.pack(side="left")

        # Treeview + Scrollbars
        tree_frame = tk.Frame(self.root)
        tree_frame.pack(fill="both", padx=10, pady=5)

        vsb = tk.Scrollbar(tree_frame, orient="vertical")
        vsb.pack(side="right", fill="y")
        hsb = tk.Scrollbar(tree_frame, orient="horizontal")
        hsb.pack(side="bottom", fill="x")

        self.tree = ttk.Treeview(tree_frame, height=10, yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.tree.pack(side="left", fill="both", expand=True)

        vsb.config(command=self.tree.yview)
        hsb.config(command=self.tree.xview)

        # Entry form
        self.form_frame = tk.Frame(self.root)
        self.form_frame.pack(pady=10)

        # Buttons
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="Add", command=self._add_row).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Update", command=self._update_row).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Delete", command=self._delete_row).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Refresh", command=self._load_data).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Exit", command=self.root.destroy).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Open File", command=self._open_file).pack(side="left", padx=5) # Added Open File button

        self.tree.bind("<<TreeviewSelect>>", self._fill_form)

    def _clear_form(self):
        for entry in self.entries:
            entry.delete(0, tk.END)

    def _load_data(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        if not os.path.exists(self.FILE_PATH):
            messagebox.showerror("Error", f"File not found:\n{self.FILE_PATH}")
            return

        with open(self.FILE_PATH, newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            try:
                headers = next(reader)
            except StopIteration:
                messagebox.showinfo("Info", "CSV file is empty.")
                return

            self.tree["columns"] = headers
            self.tree["show"] = "headings"

            # Update search column dropdown
            self.search_column_var.set("All Fields")
            search_values = ["All Fields"] + list(headers)
            self.search_column_var.set(search_values[0]) # Reset to default
            search_menu = self.search_column_var.get()
            if isinstance(search_menu, str):
                self.search_column_var.set(search_values[0])
            else:
                self.search_column_var.set(search_values[0])

            # Destroy existing form entries
            for widget in self.form_frame.winfo_children():
                widget.destroy()
            self.entries.clear()

            for col in self.tree["columns"]:
                self.tree.heading(col, text=col)
                self.tree.column(col, anchor="center", width=100, stretch=True)

                # Generate entry fields
                tk.Label(self.form_frame, text=col + ":", anchor="w", width=20).grid(row=headers.index(col), column=0, sticky="w", padx=5, pady=3)
                entry = tk.Entry(self.form_frame, width=50)
                entry.grid(row=headers.index(col), column=1, padx=5, pady=3)
                self.entries.append(entry)

            for row in reader:
                self.tree.insert("", tk.END, values=row)

    def _add_row(self):
        new_data = [entry.get().strip() for entry in self.entries]
        if not all(new_data):
            messagebox.showwarning("Warning", "All fields must be filled.")
            return

        with open(self.FILE_PATH, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(new_data)
        self._load_data()
        self._clear_form()

    def _delete_row(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Info", "Select a row to delete.")
            return

        values = [str(v).strip() for v in self.tree.item(selected[0])["values"]]
        new_rows = []
        with open(self.FILE_PATH, newline='', encoding='utf-8') as f:
            reader = list(csv.reader(f))
            headers = reader[0]
            for row in reader[1:]:
                if [cell.strip() for cell in row] != values:
                    new_rows.append(row)

        with open(self.FILE_PATH, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(new_rows)

        self._load_data()

    def _fill_form(self, event):
        selected = self.tree.selection()
        if selected:
            values = self.tree.item(selected[0])["values"]
            for i, value in enumerate(values):
                self.entries[i].delete(0, tk.END)
                self.entries[i].insert(0, value)

    def _clean_data(self, data):
        return [str(d).strip().replace("()", "") for d in data]

    def _update_row(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Info", "Select a row to update.")
            return

        new_data = [entry.get().strip() for entry in self.entries]
        if not all(new_data):
            messagebox.showwarning("Warning", "All fields must be filled.")
            return

        old_values = self.tree.item(selected[0])["values"]
        old_values_clean = self._clean_data(old_values)
        new_data_clean = self._clean_data(new_data)

        if old_values_clean == new_data_clean:
            messagebox.showinfo("Info", "No changes detected.")
            return

        updated_rows = []
        with open(self.FILE_PATH, newline='', encoding='utf-8') as f:
            reader = list(csv.reader(f))
            headers = reader[0]
            for row in reader[1:]:
                if self._clean_data(row) == old_values_clean:
                    updated_rows.append(new_data)
                else:
                    updated_rows.append(row)

        if updated_rows:
            with open(self.FILE_PATH, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(headers)
                writer.writerows(updated_rows)
            self._load_data()
            self._clear_form()
        else:
            messagebox.showinfo("Info", "No matching rows to update.")

    def _search_data(self):
        keyword = self.search_entry.get().strip().lower()
        search_column = self.search_column_var.get()
        if not keyword:
            return self._load_data()

        for row in self.tree.get_children():
            self.tree.delete(row)

        with open(self.FILE_PATH, newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            try:
                headers = next(reader)
                for row in reader:
                    if search_column == "All Fields":
                        if any(keyword in cell.lower() for cell in row):
                            self.tree.insert("", tk.END, values=row)
                    else:
                        try:
                            col_index = headers.index(search_column)
                            if keyword in row[col_index].lower():
                                self.tree.insert("", tk.END, values=row)
                        except ValueError:
                            messagebox.showerror("Error", f"Column '{search_column}' not found.")
                            return
            except StopIteration:
                messagebox.showinfo("Info", "CSV file is empty.")
                return

    def _open_file(self):
        file_path = filedialog.askopenfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if file_path:
            self.FILE_PATH = file_path
            self._load_data()

if __name__ == "__main__":
    root = tk.Tk()
    app = CSV_Viewer(root)
    root.mainloop()