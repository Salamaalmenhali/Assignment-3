import tkinter as tk
from tkinter import messagebox, ttk
import pickle
import os
from datetime import date

USER_FILE = 'users.pkl'
SALES_FILE = 'sales.pkl'

# Utility functions
def load_data(file):
    if not os.path.exists(file):
        return {}
    with open(file, 'rb') as f:
        return pickle.load(f)

def save_data(file, data):
    with open(file, 'wb') as f:
        pickle.dump(data, f)

class Ticket:
    def __init__(self, ticket_id, ticket_type, price, validity, features):
        self._ticket_id = ticket_id
        self._ticket_type = ticket_type
        self._price = price
        self._validity = validity
        self._features = features

    def get_price(self):
        return self._price

    def display(self):
        return f"{self._ticket_type} | Price: ${self._price} | Validity: {self._validity} | Features: {self._features}"

class SingleRacePass(Ticket):
    def __init__(self, ticket_id, price, validity, features, race_name, date, seat_number, zone_access):
        super().__init__(ticket_id, 'Single Race Pass', price, validity, features)
        self._race_name = race_name
        self._date = date
        self._seat_number = seat_number
        self._zone_access = zone_access

    def display(self):
        return super().display() + f" | Race: {self._race_name} | Date: {self._date} | Seat: {self._seat_number} | Access: {self._zone_access}"

class SeasonMembership(Ticket):
    def __init__(self, ticket_id, price, validity, features, season_year, races_included, member_benefits, renewal_date):
        super().__init__(ticket_id, 'Season Membership', price, validity, features)
        self._season_year = season_year
        self._races_included = races_included
        self._member_benefits = member_benefits
        self._renewal_date = renewal_date

    def display(self):
        return super().display() + f" | Season: {self._season_year} | Races: {self._races_included} | Benefits: {self._member_benefits} | Renewal: {self._renewal_date}"

class TicketApp:
    def __init__(self, master):
        self.master = master
        self.master.title("F1 Ticketing System")
        self.users = load_data(USER_FILE)
        self.current_user = None
        self.start_login_screen()

    def start_login_screen(self):
        for widget in self.master.winfo_children():
            widget.destroy()
        tk.Label(self.master, text="Welcome to F1 Ticketing System", font=("Arial", 14)).pack(pady=20)
        ttk.Button(self.master, text="Login", command=self.login_menu).pack(pady=10)
        ttk.Button(self.master, text="Register", command=self.customer_register).pack(pady=10)

    def login_menu(self):
        def login():
            username = username_entry.get().strip()
            password = password_entry.get().strip()
            if username == "admin" and password == "admin":
                top.destroy()
                self.admin_dashboard()
                return
            if username in self.users and self.users[username]['password'] == password:
                self.current_user = username
                top.destroy()
                self.customer_dashboard()
            else:
                messagebox.showerror("Error", "Invalid credentials")

        top = tk.Toplevel(self.master)
        top.title("Login")
        tk.Label(top, text="Username:").pack()
        username_entry = tk.Entry(top)
        username_entry.pack()
        tk.Label(top, text="Password:").pack()
        password_entry = tk.Entry(top, show='*')
        password_entry.pack()
        ttk.Button(top, text="Login", command=login).pack(pady=10)

    def customer_register(self):
        def register():
            username = username_entry.get().strip()
            password = password_entry.get().strip()
            if not username or not password:
                messagebox.showerror("Error", "Fields cannot be empty")
                return
            if username == "admin" or username in self.users:
                messagebox.showerror("Error", "Invalid or existing username")
                return
            self.users[username] = {'password': password, 'email': '', 'phone': '', 'city': '', 'orders': []}
            save_data(USER_FILE, self.users)
            messagebox.showinfo("Success", "Account created")
            top.destroy()

        top = tk.Toplevel(self.master)
        top.title("Register")
        tk.Label(top, text="Username:").pack()
        username_entry = tk.Entry(top)
        username_entry.pack()
        tk.Label(top, text="Password:").pack()
        password_entry = tk.Entry(top, show='*')
        password_entry.pack()
        ttk.Button(top, text="Register", command=register).pack(pady=10)

    def customer_dashboard(self):
        top = tk.Toplevel(self.master)
        top.title("Customer Dashboard")
        user = self.users[self.current_user]

        tk.Label(top, text=f"Welcome {self.current_user}", font=("Arial", 14)).pack(pady=10)

        def update(field, entry):
            user[field] = entry.get()
            save_data(USER_FILE, self.users)
            messagebox.showinfo("Updated", f"{field} updated")

        for field in ['email', 'phone', 'city']:
            tk.Label(top, text=f"{field.title()}:").pack()
            entry = tk.Entry(top)
            entry.insert(0, user.get(field, ''))
            entry.pack()
            ttk.Button(top, text=f"Update {field.title()}", command=lambda f=field, e=entry: update(f, e)).pack()

        ttk.Button(top, text="Buy Tickets", command=self.buy_tickets).pack(pady=10)
        ttk.Button(top, text="View Orders", command=lambda: self.view_user_orders(self.current_user)).pack(pady=5)
        ttk.Button(top, text="Delete Last Order", command=lambda: self.delete_last_order(user)).pack(pady=5)

    def delete_last_order(self, user):
        if user['orders']:
            user['orders'].pop()
            save_data(USER_FILE, self.users)
            messagebox.showinfo("Success", "Order deleted")
        else:
            messagebox.showwarning("Warning", "No orders to delete")

    def buy_tickets(self):
        top = tk.Toplevel(self.master)
        top.title("Buy Tickets")
        top.geometry("400x500")

        ticket_types = ["Single Race Pass", "Season Membership"]
        tk.Label(top, text="Select Ticket Type:").pack()
        combo = ttk.Combobox(top, values=ticket_types)
        combo.pack(pady=5)

        tk.Label(top, text="Discount % (if any):").pack()
        discount_entry = tk.Entry(top)
        discount_entry.pack()

        tk.Label(top, text="Payment Method:").pack()
        method_combo = ttk.Combobox(top, values=["Credit Card", "Debit Card"])
        method_combo.pack()

        def confirm():
            t = combo.get()
            method = method_combo.get()
            try:
                discount = float(discount_entry.get()) if discount_entry.get() else 0
            except:
                messagebox.showerror("Error", "Invalid discount input")
                return

            if not t or not method:
                messagebox.showerror("Error", "All fields must be filled")
                return

            today = str(date.today())
            ticket_id = len(self.users[self.current_user]['orders']) + 1

            if t == "Single Race Pass":
                ticket = SingleRacePass(ticket_id, 100, "1 day", "One entry", "Grand Prix", today, "A12", "Main Zone")
            elif t == "Season Membership":
                ticket = SeasonMembership(ticket_id, 250, "Season", "All-access", "2025", 10, "Lounge Access", "2025-12-01")
            else:
                messagebox.showerror("Error", "Invalid ticket type")
                return

            final_price = ticket.get_price() * (1 - discount / 100)

            order = {
                'ticket': ticket.display(),
                'method': method,
                'price': round(final_price, 2),
                'date': today,
                'original_price': ticket.get_price(),
                'discount': discount
            }
            self.users[self.current_user]['orders'].append(order)
            sales = load_data(SALES_FILE)
            sales[today] = sales.get(today, 0) + 1
            save_data(SALES_FILE, sales)
            save_data(USER_FILE, self.users)

            invoice = f"Invoice\n-------\nUser: {self.current_user}\nTicket: {ticket.display()}\nMethod: {method}\nOriginal Price: ${ticket.get_price()}\nDiscount: {discount}%\nFinal Price: ${round(final_price, 2)}\nDate: {today}"
            messagebox.showinfo("Purchase Complete", invoice)

        ttk.Button(top, text="Purchase", command=confirm).pack(pady=10)

    def view_user_orders(self, username):
        orders = self.users[username].get('orders', [])
        formatted = "\n\n".join([
            f"{o.get('date', 'N/A')}: ${o.get('price', 'N/A')} (Original: ${o.get('original_price', 'N/A')} - Discount: {o.get('discount', 0)}%)\nMethod: {o.get('method', 'N/A')}"
            for o in orders
        ])
        messagebox.showinfo(f"{username}'s Orders", formatted if formatted else "No orders found")

    def admin_dashboard(self):
        top = tk.Toplevel(self.master)
        top.title("Admin Dashboard")
        top.geometry("700x800")

        tk.Label(top, text="Ticket Sales Per Day", font=("Arial", 14)).pack(pady=10)
        sales = load_data(SALES_FILE)
        for k, v in sales.items():
            tk.Label(top, text=f"{k}: {v} tickets").pack()

        def reset_and_reload():
            save_data(SALES_FILE, {})
            messagebox.showinfo("Reset", "Ticket sales reset to 0")
            top.destroy()
            self.admin_dashboard()

        ttk.Button(top, text="Reset Ticket Sales", command=reset_and_reload).pack(pady=10)

        tk.Label(top, text="\nCustomer List", font=("Arial", 12)).pack(pady=5)
        for user, info in self.users.items():
            if user != "admin":
                frame = tk.Frame(top)
                frame.pack(pady=2, fill='x')
                left = tk.Frame(frame)
                left.pack(side=tk.LEFT, expand=True, fill='x')
                right = tk.Frame(frame)
                right.pack(side=tk.RIGHT)
                user_info = f"{user} | {info.get('email','')} | {info.get('phone','')} | {info.get('city','')}"
                tk.Label(left, text=user_info, anchor='w').pack(fill='x')
                ttk.Button(right, text="Delete", command=lambda u=user: self.delete_customer(u)).pack(side=tk.LEFT, padx=2)
                ttk.Button(right, text="Modify", command=lambda u=user: self.modify_customer(u)).pack(side=tk.LEFT, padx=2)
                ttk.Button(right, text="View Orders", command=lambda u=user: self.view_user_orders(u)).pack(side=tk.LEFT, padx=2)

    def delete_customer(self, username):
        confirm = messagebox.askyesno("Confirm", f"Delete {username}?")
        if confirm:
            del self.users[username]
            save_data(USER_FILE, self.users)
            messagebox.showinfo("Deleted", f"{username} removed")

    def modify_customer(self, username):
        top = tk.Toplevel(self.master)
        top.title(f"Modify {username}")
        user = self.users[username]

        for field in ['email', 'phone', 'city']:
            tk.Label(top, text=f"{field.title()}:").pack()
            entry = tk.Entry(top)
            entry.insert(0, user.get(field, ''))
            entry.pack()
            ttk.Button(top, text=f"Update {field.title()}", command=lambda f=field, e=entry: self.save_field(username, f, e)).pack()

    def save_field(self, username, field, entry):
        self.users[username][field] = entry.get()
        save_data(USER_FILE, self.users)
        messagebox.showinfo("Updated", f"{field} updated for {username}")

if __name__ == '__main__':
    root = tk.Tk()
    app = TicketApp(root)
    root.mainloop()




