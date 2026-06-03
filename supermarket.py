# COMPUTER SCIENCE PROJECT

import mysql.connector
from datetime import date, datetime
import tkinter as tk
from tkinter import messagebox
import sys

#============================================================#
#                    DATA BASE CONNECTION
#============================================================#

while True:
    try:
        database = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="super_market"
        )
        c = database.cursor()
        print(" Database connected successfully")
        break
    except mysql.connector.Error as e:
		messagebox.showerror("Database Error", f"Unable to connect to the database\n\n{e}")
        x = ""
        while x not in ["YES", "NO"]:
            x = input("Do you want to try again (YES/NO) : ").upper().strip()
            if x not in ["YES", "NO"]:
                print("Please enter YES or NO.")
        if x == "NO":
            sys.exit()
            
#============================================================#
#               INPUT VALIDATION FUNCTION
#============================================================#

def get_integer(message):
    while True:
        try:
            return int(input(message))
        except ValueError:
            print("Enter a valid integer")

def get_yes_no(message):
    while True:
        answer = input(message).lower().strip()
        if answer in ["yes", "no"]:
            return answer
        print("Enter YES or NO")

def get_expiry_date():
    while True:
        expiry = input("Enter expiry date (YYYY-MM-DD) : ")
        if expiry == "":
            return None
        try:
            return datetime.strptime(expiry, "%Y-%m-%d").date()
        except ValueError:
            print("Invalid date format. Use YYYY-MM-DD")
 
#============================================================#
#                 PRODUCT LOOKUP FUNCTION
#============================================================#

def get_product(product_id):
    c.execute("SELECT * FROM products WHERE Product_ID=%s",(product_id,))
    return c.fetchone()

def get_product_by_name(product_name):
    c.execute("SELECT * FROM products WHERE Product_Name=%s",
        (product_name,))
    return c.fetchone()

def find_product(search_value):
    if search_value.isdigit():
        c.execute("SELECT * FROM products WHERE Product_ID=%s",
            (int(search_value),))
    else:
        c.execute("SELECT * FROM products WHERE Product_Name=%s",
            (search_value.title(),))
    return c.fetchone()

def display_product(product):
    print(product[0], "\t", product[1], "\t", product[2], "\t", product[3], "\t",
        product[4])
        
#============================================================#
#                      EXPIRY FUNCTION
#============================================================#
    
def show_expired_products():
    c.execute("SELECT * FROM products WHERE Expire_Date < CURDATE()")
    products = c.fetchall()
    if not products:
        print("\nNo expired products\n")
        return
    print("\nExpired Products\n")
    for product in products:
        display_product(product)

def show_all_expiry_status():
    c.execute("SELECT * FROM products")
    products = c.fetchall()
    if not products:
        print("\nNo products\n")
        return
    print()
    for product in products:
        print(product[0], "\t", product[1], "\t", get_expiry_status(product[0]))

def expiry_checker():
    print("\n1. Show Expired Products")
    print("2. Show Expiry Status")
    choice = get_integer("\nEnter your choice : ")
    if choice == 1:
        show_expired_products()
    elif choice == 2:
        show_all_expiry_status()
    else:
        print("\nInvalid choice\n")
        
#============================================================#
#                    BILLING FUNCTION
#============================================================#

def display_bill_item(product, quantity):
    print(product[0], "\t", product[1], "\t", product[2], "\t", quantity, "\t",
        get_expiry_status(product[0]))

def get_expiry_status(product_id):
    c.execute("SELECT Expire_Date FROM products WHERE Product_ID=%s",
    (product_id,))
    result = c.fetchone()
    if result is None or result[0] is None:
        return "No Expiry"
    if result[0] < date.today():
        return "Expired"
    return "Not Expired"
	
def add_item_to_cart(cart, product, requested_quantity):
    available_quantity = product[3]
    if available_quantity == 0:
        print("\nProduct out of stock")
        return
    if requested_quantity > available_quantity:
        print(f"\nOnly {available_quantity} items available")
        requested_quantity = available_quantity
    cart.append(
        {
            "product": product,
            "quantity": requested_quantity
        })
    display_bill_item(product, requested_quantity)
	
def calculate_total(cart):
	total = 0
	for item in cart:
		product = item["product"]
		quantity = item["quantity"]
		total += product[2] * quantity
	return total
	
def update_inventory(cart):
	for item in cart:
		product = item["product"]
		quantity = item["quantity"]
		c.execute("UPDATE products SET Quantity=%s WHERE Product_ID=%s", (product[3] - quantity, product[0]))
	database.commit()
	
def print_final_bill(cart):
    print("\nFinal Bill\n")
    for item in cart:
        display_bill_item(
            item["product"],
            item["quantity"]
        )
    print("\nTotal Amount : ₹", calculate_total(cart))
	
# Billing Main Function
def billing_system():
	cart = [ ]
	while True:
		product_id = get_integer("\nEnter the product ID : ")
		quantity = get_integer(" Enter the quantity : ")
		product = get_product(product_id)		
		if product is None:
			print("\nProduct not available")
		else:
			add_item_to_cart(cart, product, quantity)			
		if get_yes_no("\nDo you want to add another product (YES/NO) : ")=="no":
			break				
	if cart:
		print_final_bill(cart)
		update_inventory(cart)
	else:
		print("\nCart is empty\n")

#============================================================#
#                 ADD PRODUCT FUNCTION
#============================================================#
	
def increase_stock(product_name, quantity):
	c.execute("UPDATE products SET Quantity = Quantity + %s WHERE Product_Name = %s", (quantity, product_name))
	database.commit()
	
def insert_product(product_name, quantity, price, expire_date):
    c.execute(
        """
        INSERT INTO products(
            Product_Name,
            Price,
            Quantity,
            Expire_Date
        )
        VALUES(%s,%s,%s,%s)
        """, (product_name, quantity, price, expire_date))
    database.commit()
                       
def add_product():
    while True:
        product_name = input("\nEnter product name : ").title()
        product = get_product_by_name(product_name)
        if product:
            print("\nProduct already available")
            if get_yes_no(
                "Increase stock instead (YES/NO) : ") == "yes":
                quantity = get_integer(" Enter quantity : ")
                increase_stock(product_name, quantity)
                print("\nStock updated successfully")
        else:
            quantity = get_integer(" Enter quantity : ")
            price = float(input(" Enter product price : "))
            expiry_date = get_expiry_date()
            insert_product(product_name, quantity, price, expiry_date)
            print(f"\nProduct {product_name} added successfully")
        if get_yes_no("\nAdd another product (YES/NO) : ") == "no":
            break
            
#============================================================#
#                  SEARCH PRODUCT FUNCTION
#============================================================#

def search_product():
    search_value = input("\nEnter product name or ID : ")
    product = find_product(search_value)
    if product:
        display_product(product)
    else:
        print("\nProduct not available\n")

#============================================================#
#                DELETE PRODUCT FUNCTION
#============================================================#

def delete_product(product_id):
    c.execute("DELETE FROM products WHERE Product_ID=%s", (product_id,))
    database.commit()
    
def remove_product():
    while True:
        search_value = input("\nEnter product name or ID : ")
        product = find_product(search_value)
        if product:
            delete_product(product[0])
            print(f"\nProduct '{product[1]}' removed successfully\n")
        else:
            print("\nProduct not available\n")
        if get_yes_no("Remove another product (YES/NO) : ") == "no":
            break
            
#============================================================#
#                  PRODUCT UPDATE PRODUCTS
#============================================================#

def product_data_update():
    search_value = input("\nEnter Product Name or ID : ")
    product = find_product(search_value)
    if not product:
        print("\nProduct not available\n")
        return
    print("\n1. Update Name")
    print("2. Update Price")
    print("3. Update Quantity")
    print("4. Update Expiry Date")
    choice = get_integer("\nEnter choice : ")
    if choice == 1:
        new_name = input(" Enter new name : ").title()
        c.execute(
            """
            UPDATE products
            SET Product_Name=%s
            WHERE Product_ID=%s
            """, (new_name, product[0]))
    elif choice == 2:
        new_price = float(input(" Enter new price : "))
        c.execute(
            """
            UPDATE products
            SET Price=%s
            WHERE Product_ID=%s
            """, (new_price, product[0]))
    elif choice == 3:
        new_quantity = get_integer(" Enter new quantity : ")
        c.execute(
            """
            UPDATE products
            SET Quantity=%s
            WHERE Product_ID=%s
            """, (new_quantity, product[0]))
    elif choice == 4:
        new_date = get_expiry_date()
        c.execute(
            """
            UPDATE products
            SET Expire_Date=%s
            WHERE Product_ID=%s
            """, (new_date, product[0]))
    else:
        print("\nInvalid choice\n")
        return
    database.commit()
    print("\nProduct updated successfully\n")
    
#============================================================#
#                VIEW PRODUCTS FUNCTION
#============================================================#

def view_products():
    c.execute("SELECT * FROM products")
    products = c.fetchall()
    if not products:
        print("\nNo products\n")
        return
    print()
    for product in products:
        display_product(product)
    print()
    
#============================================================#
# 										EXIT SUPER MARKET
#============================================================#
    
def close_application():
    print("\nThank you for using the Super Market Application")
    c.close()
    database.close()
    
#============================================================#
#                                  SUPER MARKET MAIN WINDOW
#============================================================#

root = tk.Tk()
root.title("Dheekshith Super Market")
root.geometry("500x500")

# Heading

title = tk.Label(root, text="DHEEKSHITH SUPER MARKET", font=("Arial", 18, "bold"))
title.pack(pady=20)

#============================================================#
#                                     ADD PRODUCTS WINDOW
#============================================================#

def open_add_product():
    add_window = tk.Toplevel(root)
    add_window.title("Add Product")
    add_window.geometry("350x450")
    
    tk.Label(add_window, text="Product Name").pack(pady=5)
    entry_name = tk.Entry(add_window, width=25)
    entry_name.pack()
    
    tk.Label(add_window, text="Price").pack(pady=5)
    entry_price = tk.Entry(add_window, width=25)
    entry_price.pack()
    
    tk.Label(add_window, text="Quantity").pack(pady=5)
    entry_quantity = tk.Entry(add_window, width=25)
    entry_quantity.pack()
    
    tk.Label(add_window, text="Expiry Date").pack(pady=5)
    entry_expiry = tk.Entry(add_window, width=25)
    entry_expiry.pack()
    
    def save_product():
    	product_name = entry_name.get()
    	price = float(entry_price.get())
    	quantity = int(entry_quantity.get())
    	expiry = entry_expiry.get()
    	
    	c.execute("INSERT INTO products (Product_Name, Price, Quantity, Expire_Date) VALUES (%s, %s,%s, %s)",
    	(product_name, price, quantity, expiry))
    	database.commit()
    	messagebox.showinfo("Success", "Product added successfully")
    	
    	entry_name.delete(0, tk.END)
    	entry_price.delete(0, tk.END)
    	entry_quantity.delete(0, tk.END)
    	entry_expiry.delete(0, tk.END)
    	
    tk.Button(add_window,text="Save Product", command=save_product).pack(pady=10)

btn_add = tk.Button(root, text="Add Product", width=20, command=open_add_product)
btn_add.pack(pady=5)

#============================================================#
#                                    VIEW PRODUCTS WINDOW
#============================================================#

def open_view_products():
    view_window = tk.Toplevel(root)
    view_window.title("View Products")
    view_window.geometry("700x800")
    tk.Label(view_window, text="All Products", font=("Arial", 16, "bold")).pack(pady=10)
    c.execute("SELECT * FROM products")
    products = c.fetchall()
    for product in products:
        text = f"{product[0]}   {product[1]}   ₹{product[2]}   Qty:{product[3]}   {product[4]}"
        tk.Label(view_window, text=text).pack()
btn_view = tk.Button(root, text="View Products", width=20, command=open_view_products)
btn_view.pack(pady=5)

#============================================================#
#                                 SEARCH PRODUCTS WINDOW
#============================================================#

def open_search_product():
    search_window = tk.Toplevel(root)
    search_window.title("Search Product")
    search_window.geometry("900x300")
    tk.Label(search_window, text="Enter Product ID or Name").pack(pady=10)

    entry_search = tk.Entry(search_window, width=25)
    entry_search.pack()

    result_label = tk.Label(search_window, text="")
    result_label.pack(pady=20)

    def search_product_gui():
        search_value = entry_search.get()
        if search_value.isdigit():
            c.execute("SELECT * FROM products WHERE Product_ID=%s",
                (int(search_value),))
        else:
            c.execute("SELECT * FROM products WHERE Product_Name=%s",
                (search_value.title(),))
        product = c.fetchone()
        if product:
            result_label.config(
                text=f"ID : {product[0]} Name : {product[1]} Price : ₹{product[2]} Quantity : {product[3]} Expiry : {product[4]}")
        else:
            result_label.config(text="Product Not Found")
    tk.Button(search_window, text="Search", command=search_product_gui).pack(pady=10)
btn_search = tk.Button(root, text="Search Product", width=20, command=open_search_product)
btn_search.pack(pady=5)

#============================================================#
#                                  UPDATE PRODUCT WINDOW
#============================================================#

def open_update_product():
    update_window = tk.Toplevel(root)
    update_window.title("Update Product")
    update_window.geometry("400x500")
    
    tk.Label(update_window, text="Product ID").pack(pady=5)
    entry_id = tk.Entry(update_window)
    entry_id.pack()

    tk.Label(update_window, text="New Name").pack(pady=5)
    entry_name = tk.Entry(update_window)
    entry_name.pack()

    tk.Label(update_window, text="New Price").pack(pady=5)
    entry_price = tk.Entry(update_window)
    entry_price.pack()

    tk.Label(update_window, text="New Quantity").pack(pady=5)
    entry_quantity = tk.Entry(update_window)
    entry_quantity.pack()

    tk.Label(update_window, text="New Expiry Date").pack(pady=5)
    entry_expiry = tk.Entry(update_window)
    entry_expiry.pack()
    
    def update_product_gui():
        try:
            product_id = int(entry_id.get())
            c.execute("SELECT * FROM products WHERE Product_ID=%s",
                (product_id,))
            product = c.fetchone()
            if product is None:
                messagebox.showerror("Error", "Product Not Found")
                return
            c.execute("UPDATE products SET Product_Name=%s, Price=%s, Quantity=%s, Expire_Date=%s WHERE Product_ID=%s",(entry_name.get(), float(entry_price.get()), int(entry_quantity.get()), entry_expiry.get(), product_id))
            database.commit()
            messagebox.showinfo("Success", "Product Updated Successfully")
        except ValueError:
            messagebox.showerror("Error", "Invalid Input")
    tk.Button(update_window, text="Update Product", command=update_product_gui).pack(pady=20)
btn_update = tk.Button(root, text="Update Product", width=20, command=open_update_product)
btn_update.pack(pady=5)
#============================================================#
#                                 DELETE PRODUCT WINDOW
#============================================================#

def open_delete_product():
    delete_window = tk.Toplevel(root)
    delete_window.title("Delete Product")
    delete_window.geometry("400x250")
    tk.Label(delete_window, text="Enter Product ID").pack(pady=10)

    entry_id = tk.Entry(delete_window, width=20)
    entry_id.pack()

    result_label = tk.Label(delete_window, text="")
    result_label.pack(pady=10)

    def delete_product_gui():
        try:
            product_id = int(entry_id.get())
            c.execute("SELECT * FROM products WHERE Product_ID=%s",
                (product_id,))
            product = c.fetchone()
            if product is None:
                result_label.config(text="Product Not Found")
                return
            c.execute("DELETE FROM products WHERE Product_ID=%s",
                (product_id,))
            database.commit()
            result_label.config(text=f"{product[1]} Deleted Successfully")
            entry_id.delete(0, tk.END)
        except ValueError:
            result_label.config(text="Enter Valid Product ID")
    tk.Button(delete_window, text="Delete Product", command=delete_product_gui).pack(pady=10)
btn_delete = tk.Button(root, text="Delete Product", width=20, command=open_delete_product)
btn_delete.pack(pady=5)

#============================================================#
#                              BILLING PRODUCT WINDOW
#============================================================#

def open_billing():
    bill_window = tk.Toplevel(root)
    bill_window.title("Billing")
    bill_window.geometry("500x500")
    cart = []

    tk.Label(bill_window, text="Product ID").pack()
    entry_id = tk.Entry(bill_window)
    entry_id.pack()

    tk.Label(bill_window, text="Quantity").pack()
    entry_quantity = tk.Entry(bill_window)
    entry_quantity.pack()

    bill_area = tk.Text(bill_window, height=15, width=50)
    bill_area.pack(pady=10)

    def add_to_cart():
        try:
            product_id = int(entry_id.get())
            quantity = int(entry_quantity.get())
            c.execute("SELECT * FROM products WHERE Product_ID=%s",
                (product_id,))
            product = c.fetchone()
            if product is None:
                messagebox.showerror("Error", "Product Not Found")
                return
            if quantity > product[3]:
                messagebox.showerror("Error", "Not Enough Stock")
                return
            cart.append((product, quantity))
            subtotal = product[2] * quantity
            status = get_expiry_status(product_id)
			bill_area.insert(tk.END, f"{product[1]} x {quantity} = ₹{subtotal}    [{status}]\n")
            entry_id.delete(0, tk.END)
            entry_quantity.delete(0, tk.END)
        except ValueError:
            messagebox.showerror("Error", "Enter Valid Data")

    def generate_bill():
        total = 0
        for item in cart:
            product = item[0]
            quantity = item[1]
            total += product[2] * quantity
            c.execute("UPDATE products SET Quantity=%s WHERE Product_ID=%s",
                (product[3] - quantity, product[0]))
        database.commit()
        bill_area.insert(tk.END, "\n--------------------\n")
        bill_area.insert(tk.END, f"TOTAL = ₹{total}\n")
        messagebox.showinfo("Success", "Bill Generated Successfully")

    tk.Button(bill_window, text="Add To Cart", command=add_to_cart).pack(pady=5)

    tk.Button(bill_window, text="Generate Bill", command=generate_bill).pack(pady=5)
btn_billing = tk.Button(root, text="Billing", width=20, command=open_billing)
btn_billing.pack(pady=5)

#============================================================#
#                                EXPIRY PRODUCT WINDOW
#============================================================#
    
def open_expiry_checker():
    expiry_window = tk.Toplevel(root)
    expiry_window.title("Expiry Checker")
    expiry_window.geometry("800x900")
    result_area = tk.Text(expiry_window, height=15, width=70)
    result_area.pack(pady=10)
    def show_expired():
        result_area.delete(1.0, tk.END)
        c.execute("SELECT * FROM products WHERE Expire_Date < CURDATE()")
        products = c.fetchall()
        if not products:
            result_area.insert(tk.END, "No Expired Products")
            return
        result_area.insert(tk.END, "Expired Products\n\n")
        for product in products:
            result_area.insert(tk.END, f"ID: {product[0]}   " f"Name: {product[1]}   "
                f"Expiry: {product[4]}\n")
    def show_all_status():
        result_area.delete(1.0, tk.END)
        c.execute("SELECT * FROM products")
        products = c.fetchall()
        if not products:
            result_area.insert(tk.END, "No Products Available")
            return
        for product in products:
            if product[4] is None:
                status = "No Expiry"
            elif product[4] < date.today():
                status = "Expired"
            else:
                status = "Not Expired"
            result_area.insert(tk.END, f"ID: {product[0]}   " f"Name: {product[1]}   "
                f"Status: {status}\n")

    tk.Button(expiry_window, text="Show Expired Products", command=show_expired).pack(pady=5)
    tk.Button(expiry_window, text="Show Expiry Status", command=show_all_status).pack(pady=5)

btn_expiry = tk.Button(root, text="Expiry Checker", width=20, command=open_expiry_checker)
btn_expiry.pack(pady=5)

#============================================================#
#                                        EXIT WINDOW
#============================================================#

def close_application():
	c.close()
	database.close()
	root.destroy()
btn_exit = tk.Button(root, height=1, width=20,text = "Exit",command=close_application)
btn_exit.pack(pady=5)
#============================================================#

root.mainloop()
