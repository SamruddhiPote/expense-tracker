# Simple Expense Tracker App
# By a Beginner Programmer

import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import webbrowser

# Database setup
def setup_database():
    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()
    
    # Create expenses table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            description TEXT,
            category TEXT,
            amount REAL,
            payment_method TEXT,
            recurring INTEGER
        )
    ''')
    
    # Create categories table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            name TEXT PRIMARY KEY
        )
    ''')
    
    # Add default categories if they don't exist
    default_categories = ['Food', 'Transport', 'Rent', 'Utilities', 'Entertainment', 'Other']
    for cat in default_categories:
        cursor.execute("INSERT OR IGNORE INTO categories VALUES (?)", (cat,))
    
    conn.commit()
    conn.close()

# Expense functions
def add_expense(desc, cat, amt, date=None, payment="Cash", recurring=False):
    if date is None:
        date = datetime.now().strftime('%Y-%m-%d')
    
    try:
        conn = sqlite3.connect('expenses.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO expenses 
            (date, description, category, amount, payment_method, recurring)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (date, desc, cat, amt, payment, 1 if recurring else 0))
        conn.commit()
        return True
    except Exception as e:
        print("Error adding expense:", e)
        return False
    finally:
        conn.close()

def get_expenses(timeframe='all'):
    try:
        conn = sqlite3.connect('expenses.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if timeframe == 'today':
            today = datetime.now().strftime('%Y-%m-%d')
            cursor.execute("SELECT * FROM expenses WHERE date = ? ORDER BY date DESC", (today,))
        elif timeframe == 'week':
            week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
            cursor.execute("SELECT * FROM expenses WHERE date >= ? ORDER BY date DESC", (week_ago,))
        elif timeframe == 'month':
            month_ago = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            cursor.execute("SELECT * FROM expenses WHERE date >= ? ORDER BY date DESC", (month_ago,))
        else:
            cursor.execute("SELECT * FROM expenses ORDER BY date DESC")
            
        return cursor.fetchall()
    except Exception as e:
        print("Error getting expenses:", e)
        return []
    finally:
        conn.close()

def get_categories():
    try:
        conn = sqlite3.connect('expenses.db')
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM categories ORDER BY name")
        return [row[0] for row in cursor.fetchall()]
    except Exception as e:
        print("Error getting categories:", e)
        return []
    finally:
        conn.close()

def add_category(cat):
    try:
        conn = sqlite3.connect('expenses.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO categories VALUES (?)", (cat,))
        conn.commit()
        return True
    except Exception as e:
        print("Error adding category:", e)
        return False
    finally:
        conn.close()

# Main application
class ExpenseTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("My Expense Tracker")
        self.root.geometry("1000x700")
        
        setup_database()
        
        # Create tabs
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True)
        
        # Add Expense Tab
        self.add_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.add_tab, text="Add Expense")
        self.create_add_tab()
        
        # View Expenses Tab
        self.view_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.view_tab, text="View Expenses")
        self.create_view_tab()
        
        # Reports Tab
        self.reports_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.reports_tab, text="Reports")
        self.create_reports_tab()
        
        # Categories Tab
        self.categories_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.categories_tab, text="Categories")
        self.create_categories_tab()
        
        # Menu
        self.create_menu()
    
    def create_menu(self):
        menubar = tk.Menu(self.root)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Export", command=self.export_data)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)
        menubar.add_cascade(label="Help", menu=help_menu)
        
        self.root.config(menu=menubar)
    
    def create_add_tab(self):
        # Description
        ttk.Label(self.add_tab, text="Description:").grid(row=0, column=0, padx=10, pady=5, sticky='e')
        self.desc_entry = ttk.Entry(self.add_tab, width=40)
        self.desc_entry.grid(row=0, column=1, padx=10, pady=5, sticky='w')
        
        # Category
        ttk.Label(self.add_tab, text="Category:").grid(row=1, column=0, padx=10, pady=5, sticky='e')
        self.cat_combo = ttk.Combobox(self.add_tab, values=get_categories())
        self.cat_combo.grid(row=1, column=1, padx=10, pady=5, sticky='w')
        
        # Amount
        ttk.Label(self.add_tab, text="Amount:").grid(row=2, column=0, padx=10, pady=5, sticky='e')
        self.amt_entry = ttk.Entry(self.add_tab, width=40)
        self.amt_entry.grid(row=2, column=1, padx=10, pady=5, sticky='w')
        
        # Payment Method
        ttk.Label(self.add_tab, text="Payment Method:").grid(row=3, column=0, padx=10, pady=5, sticky='e')
        self.pay_method = ttk.Combobox(self.add_tab, values=["Cash", "Credit Card", "Debit Card", "Bank Transfer"])
        self.pay_method.grid(row=3, column=1, padx=10, pady=5, sticky='w')
        self.pay_method.current(0)
        
        # Recurring
        self.recurring_var = tk.BooleanVar()
        ttk.Checkbutton(self.add_tab, text="Recurring Expense", variable=self.recurring_var).grid(row=4, column=1, padx=10, pady=5, sticky='w')
        
        # Add Button
        ttk.Button(self.add_tab, text="Add Expense", command=self.add_expense).grid(row=5, column=1, padx=10, pady=10, sticky='e')
    
    def create_view_tab(self):
        # Treeview for expenses
        columns = ("ID", "Date", "Description", "Category", "Amount", "Payment", "Recurring")
        self.expense_tree = ttk.Treeview(self.view_tab, columns=columns, show='headings')
        
        for col in columns:
            self.expense_tree.heading(col, text=col)
            self.expense_tree.column(col, width=100)
        
        self.expense_tree.column("Description", width=200)
        self.expense_tree.column("Amount", width=80)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(self.view_tab, orient='vertical', command=self.expense_tree.yview)
        self.expense_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack widgets
        self.expense_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Timeframe filter
        filter_frame = ttk.Frame(self.view_tab)
        filter_frame.pack(fill='x', padx=5, pady=5)
        
        self.timeframe_var = tk.StringVar(value='all')
        
        ttk.Radiobutton(filter_frame, text="All", variable=self.timeframe_var, value='all', command=self.update_expense_list).pack(side='left')
        ttk.Radiobutton(filter_frame, text="Today", variable=self.timeframe_var, value='today', command=self.update_expense_list).pack(side='left')
        ttk.Radiobutton(filter_frame, text="This Week", variable=self.timeframe_var, value='week', command=self.update_expense_list).pack(side='left')
        ttk.Radiobutton(filter_frame, text="This Month", variable=self.timeframe_var, value='month', command=self.update_expense_list).pack(side='left')
        
        # Action buttons
        btn_frame = ttk.Frame(self.view_tab)
        btn_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Button(btn_frame, text="Delete Selected", command=self.delete_expense).pack(side='left')
        ttk.Button(btn_frame, text="Refresh", command=self.update_expense_list).pack(side='right')
        
        # Initial load
        self.update_expense_list()
    
    def create_reports_tab(self):
        # Simple report frame
        self.report_frame = ttk.Frame(self.reports_tab)
        self.report_frame.pack(fill='both', expand=True)
        
        # Timeframe selector
        timeframe_frame = ttk.Frame(self.reports_tab)
        timeframe_frame.pack(fill='x', padx=5, pady=5)
        
        self.report_timeframe = tk.StringVar(value='month')
        
        ttk.Radiobutton(timeframe_frame, text="All", variable=self.report_timeframe, value='all', command=self.update_report).pack(side='left')
        ttk.Radiobutton(timeframe_frame, text="Today", variable=self.report_timeframe, value='today', command=self.update_report).pack(side='left')
        ttk.Radiobutton(timeframe_frame, text="This Week", variable=self.report_timeframe, value='week', command=self.update_report).pack(side='left')
        ttk.Radiobutton(timeframe_frame, text="This Month", variable=self.report_timeframe, value='month', command=self.update_report).pack(side='left')
        
        # Initial report
        self.update_report()
    
    def create_categories_tab(self):
        # Category list
        self.cat_listbox = tk.Listbox(self.categories_tab)
        self.cat_listbox.pack(side='left', fill='both', expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(self.categories_tab, orient='vertical', command=self.cat_listbox.yview)
        self.cat_listbox.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')
        
        # Add category
        add_frame = ttk.Frame(self.categories_tab)
        add_frame.pack(fill='x', padx=5, pady=5)
        
        self.new_cat_entry = ttk.Entry(add_frame)
        self.new_cat_entry.pack(side='left', fill='x', expand=True, padx=5)
        
        ttk.Button(add_frame, text="Add", command=self.add_category).pack(side='left', padx=5)
        ttk.Button(add_frame, text="Delete", command=self.delete_category).pack(side='left', padx=5)
        
        # Load categories
        self.update_category_list()
    
    def add_expense(self):
        desc = self.desc_entry.get()
        cat = self.cat_combo.get()
        amt = self.amt_entry.get()
        pay = self.pay_method.get()
        recurring = self.recurring_var.get()
        
        if not desc or not cat or not amt:
            messagebox.showerror("Error", "Please fill all fields")
            return
        
        try:
            amt = float(amt)
        except ValueError:
            messagebox.showerror("Error", "Amount must be a number")
            return
        
        if add_expense(desc, cat, amt, payment=pay, recurring=recurring):
            messagebox.showinfo("Success", "Expense added successfully")
            self.desc_entry.delete(0, 'end')
            self.amt_entry.delete(0, 'end')
            self.update_expense_list()
            self.update_report()
        else:
            messagebox.showerror("Error", "Failed to add expense")
    
    def update_expense_list(self):
        # Clear existing items
        for item in self.expense_tree.get_children():
            self.expense_tree.delete(item)
        
        # Get expenses for selected timeframe
        expenses = get_expenses(self.timeframe_var.get())
        
        # Add to treeview
        for exp in expenses:
            self.expense_tree.insert('', 'end', values=(
                exp['id'],
                exp['date'],
                exp['description'],
                exp['category'],
                f"${exp['amount']:.2f}",
                exp['payment_method'],
                "Yes" if exp['recurring'] else "No"
            ))
    
    def delete_expense(self):
        selected = self.expense_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an expense to delete")
            return
        
        expense_id = self.expense_tree.item(selected[0])['values'][0]
        
        try:
            conn = sqlite3.connect('expenses.db')
            cursor = conn.cursor()
            cursor.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
            conn.commit()
            messagebox.showinfo("Success", "Expense deleted")
            self.update_expense_list()
            self.update_report()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete expense: {e}")
        finally:
            conn.close()
    
    def update_report(self):
        # Clear previous report
        for widget in self.report_frame.winfo_children():
            widget.destroy()
        
        # Get expenses for selected timeframe
        expenses = get_expenses(self.report_timeframe.get())
        
        if not expenses:
            ttk.Label(self.report_frame, text="No expenses to display").pack()
            return
        
        # Calculate totals
        total = sum(exp['amount'] for exp in expenses)
        count = len(expenses)
        avg = total / count if count > 0 else 0
        
        # Create summary labels
        ttk.Label(self.report_frame, text=f"Total Expenses: ${total:.2f}", font=('Arial', 12, 'bold')).pack(pady=5)
        ttk.Label(self.report_frame, text=f"Number of Expenses: {count}").pack()
        ttk.Label(self.report_frame, text=f"Average Expense: ${avg:.2f}").pack()
        
        # Create pie chart by category
        categories = {}
        for exp in expenses:
            if exp['category'] in categories:
                categories[exp['category']] += exp['amount']
            else:
                categories[exp['category']] = exp['amount']
        
        fig = plt.figure(figsize=(5, 4), dpi=100)
        ax = fig.add_subplot(111)
        ax.pie(categories.values(), labels=categories.keys(), autopct='%1.1f%%')
        ax.set_title('Expenses by Category')
        
        # Embed chart in Tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.report_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)
    
    def update_category_list(self):
        self.cat_listbox.delete(0, 'end')
        for cat in get_categories():
            self.cat_listbox.insert('end', cat)
    
    def add_category(self):
        new_cat = self.new_cat_entry.get()
        if not new_cat:
            messagebox.showerror("Error", "Please enter a category name")
            return
        
        if add_category(new_cat):
            messagebox.showinfo("Success", "Category added")
            self.new_cat_entry.delete(0, 'end')
            self.update_category_list()
            self.cat_combo['values'] = get_categories()
        else:
            messagebox.showerror("Error", "Failed to add category")
    
    def delete_category(self):
        selected = self.cat_listbox.curselection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a category to delete")
            return
        
        cat = self.cat_listbox.get(selected[0])
        
        # Check if category is used in expenses
        try:
            conn = sqlite3.connect('expenses.db')
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM expenses WHERE category = ?", (cat,))
            count = cursor.fetchone()[0]
            
            if count > 0:
                messagebox.showerror("Error", f"Cannot delete '{cat}' as it has {count} expenses")
                return
        except Exception as e:
            messagebox.showerror("Error", f"Database error: {e}")
            return
        finally:
            conn.close()
        
        if messagebox.askyesno("Confirm", f"Delete category '{cat}'?"):
            try:
                conn = sqlite3.connect('expenses.db')
                cursor = conn.cursor()
                cursor.execute("DELETE FROM categories WHERE name = ?", (cat,))
                conn.commit()
                messagebox.showinfo("Success", "Category deleted")
                self.update_category_list()
                self.cat_combo['values'] = get_categories()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete category: {e}")
            finally:
                conn.close()
    
    def export_data(self):
        expenses = get_expenses('all')
        if not expenses:
            messagebox.showwarning("Warning", "No expenses to export")
            return
        
        # Convert to DataFrame
        data = []
        for exp in expenses:
            data.append({
                'Date': exp['date'],
                'Description': exp['description'],
                'Category': exp['category'],
                'Amount': exp['amount'],
                'Payment Method': exp['payment_method'],
                'Recurring': 'Yes' if exp['recurring'] else 'No'
            })
        
        df = pd.DataFrame(data)
        
        # Ask for save location
        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("CSV files", "*.csv"), ("All files", "*.*")],
            title="Save Expense Report"
        )
        
        if not file_path:
            return
        
        try:
            if file_path.endswith('.xlsx'):
                df.to_excel(file_path, index=False)
            else:
                df.to_csv(file_path, index=False)
            
            messagebox.showinfo("Success", f"Data exported to {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export: {e}")
    
    def show_about(self):
        messagebox.showinfo(
            "About",
            "Simple Expense Tracker\n\n"
            "Version 1.0\n"
            "Created by a Beginner Programmer"
        )

# Run the application
if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTracker(root)
    root.mainloop()