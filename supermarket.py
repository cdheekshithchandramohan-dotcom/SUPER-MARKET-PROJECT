# COMPUTER SCIENCE PROJECT

import mysql.connector
from datetime import date, datetime
import sys

#============================================================#
#                                     DATA BASE CONNECTION
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
        print("Database connected successfully")
        break
    except mysql.connector.Error:
        print("Unable to connect to the database.")
        x = ""
        while x not in ["YES", "NO"]:
            x = input("Do you want to try again (YES/NO) : ").upper().strip()
            if x not in ["YES", "NO"]:
                print("Please enter YES or NO.")
        if x == "NO":
            sys.exit()
            
#============================================================#
#                              INPUT VALIDATION FUNCTION
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
#								PRODUCT LOOKUP FUNCTION
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
#                                        EXPIRY FUNCTION
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
#                         	           BILLING FUNCTIONS
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
		quantity = get_integer("Enter the quantity : ")
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
#                 	                 ADD PRODUCT FUNCTION
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
                quantity = get_integer("Enter quantity : ")
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
#									SEARCH PRODUCT FUNCTION
#============================================================#

def search_product():
    search_value = input("\nEnter product name or ID : ")
    product = find_product(search_value)
    if product:
        display_product(product)
    else:
        print("\nProduct not available\n")

#============================================================#    #           	  			       DELETE PRODUCT FUNCTION
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
#								PRODUCT UPDATE FUNCTION
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
        new_name = input("Enter new name : ").title()
        c.execute(
            """
            UPDATE products
            SET Product_Name=%s
            WHERE Product_ID=%s
            """, (new_name, product[0]))
    elif choice == 2:
        new_price = float(input("Enter new price : "))
        c.execute(
            """
            UPDATE products
            SET Price=%s
            WHERE Product_ID=%s
            """, (new_price, product[0]))
    elif choice == 3:
        new_quantity = get_integer("Enter new quantity : ")
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
# 											VIEW PRODUCTS
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

while True:
    print("1 = Billing")
    print("2 = Add Product")
    print("3 = Remove Product")
    print("4 = Search Product")
    print("5 = Expired Products")
    print("6 = View Products")
    print("7 = Update Product")
    print("8 = Exit")
    choice = get_integer(" Enter your choice : ")
    if choice == 1:
    	billing_system()
    elif choice == 2:
        add_product()
    elif choice == 3:
        remove_product()
    elif choice == 4:
        search_product()
    elif choice == 5:
        expiry_checker()
    elif choice == 6:
        view_products()
    elif choice == 7:
        product_data_update()
    elif choice == 8:
    	close_application()
    	break
    else:
        print("\nInvalid choice\n")
