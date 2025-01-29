import hashlib
from datetime import datetime
import tkinter as tk
from tkinter import messagebox

class Block:
    def __init__(self, data, previous_hash, authority):
        self.data = data
        self.timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.previous_hash = previous_hash
        self.authority = authority
        self.block_hash = self.calculate_hash()

    def calculate_hash(self):
        block_string = f"{self.data}{self.timestamp}{self.previous_hash}{self.authority}"
        return hashlib.sha256(block_string.encode()).hexdigest()

class Blockchain:
    def __init__(self):
        self.chain = [Block("Genesis Block", "0", "Firm")]
        self.authorities_with_passwords = {
            "Manufacturer": "m",
            "Warehouse": "w",
            "Customer": "c",
            "Firm": "f"
        }
        self.block_permissions = {
            "ProductManufactured": "Manufacturer",
            "ProductInWarehouse": "Warehouse",
            "ProductShipped": "Warehouse",
            "ShipmentDelayed": "Warehouse",
            "ProductReceived": "Customer",
            "PaymentMade": "Customer",
            "PaymentReceived": "Firm"
        }
        self.product_status = {}
        self.product_steps = [
            "Start",
            "ProductManufactured",
            "ProductInWarehouse",
            "ShipmentDelayed",  # Optional step
            "ProductShipped",
            "ProductReceived",
            "PaymentMade",
            "PaymentReceived",
            "TransactionComplete"
        ]

    def proof_of_authority(self, entered_password):
        entered_password = entered_password.strip()
        
        for authority, password in self.authorities_with_passwords.items():
            if password == entered_password:
                return authority
        print("Invalid password. Access denied.")
        return None

    def initialize_product(self, product_id):
        if product_id not in self.product_status:
            self.product_status[product_id] = "Start"
            print(f"Product {product_id} initialized.")
        else:
            print(f"Product {product_id} already exists.")
    
    def add_block(self, product_id, block_type, entered_password):
        authority = self.proof_of_authority(entered_password)
        if not authority:
            return False
        
        allowed_authority = self.block_permissions.get(block_type)
        if not allowed_authority or allowed_authority != authority:
            print(f"No permission for this block type: {block_type}")
            messagebox.showerror("Error", "Failed to add block. Invalid authority.")
            return False
        
        if product_id not in self.product_status:
            print(f"Product {product_id} does not exist. Please initialize it first.")
            messagebox.showerror("Error", "Product does not exist. Please initialize it first.")
            return False
        
        current_status = self.product_status[product_id]
        
        try:
            current_step_index = self.product_steps.index(current_status)
            next_step_index = self.product_steps.index(block_type)
        except ValueError:
            print(f"Invalid step: {block_type}")
            return False
        
        if (next_step_index == current_step_index + 1) or \
        (current_status == "ProductInWarehouse" and block_type in ["ShipmentDelayed", "ProductShipped"]) or \
        (current_status == "ShipmentDelayed" and block_type == "ProductShipped") or \
        (current_status == "ProductShipped" and block_type == "ProductReceived") or \
        (current_status == "ProductReceived" and block_type == "PaymentMade") or \
        (current_status == "PaymentMade" and block_type == "PaymentReceived"):
            self.product_status[product_id] = block_type
            previous_block = self.chain[-1]
            new_block = Block(f"Product {product_id} {block_type}", previous_block.block_hash, authority)
            self.chain.append(new_block)
            print(f"Block added by authority: {authority} - Block type: {block_type}")

            if block_type == "PaymentReceived":
                print(f"Automatically transitioning to 'TransactionComplete' for product {product_id}")
                self.product_status[product_id] = "TransactionComplete"
                new_block = Block(f"Product {product_id} TransactionComplete", previous_block.block_hash, authority)
                self.chain.append(new_block)
                print(f"Transaction Complete for Product {product_id}.")
            return True
        
        else:
            print(f"Invalid step sequence: {product_id} cannot go from {current_status} to {block_type}.")
            messagebox.showerror("Error", "Failed to add block. Invalid sequence.")
            return False
        

    def get_chain(self):
        return self.chain
    
    def get_product_history(self, product_id):
        history = []
        for block in self.chain:
            if product_id in block.data:
                history.append(block)
        return history


class BlockchainApp:
    def __init__(self, root, blockchain):
        self.root = root
        self.blockchain = blockchain
        self.root.title("Blockchain UI")
        
        self.blockchain_data_label = tk.Label(self.root, text="Blockchain History:")
        self.blockchain_data_label.grid(row=0, column=0, columnspan=2, pady=10)

        self.blockchain_display = tk.Listbox(self.root, width=80, height=10)
        self.blockchain_display.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

        self.data_label = tk.Label(self.root, text="Enter Product ID:")
        self.data_label.grid(row=2, column=0, sticky="w", padx=10)
        
        self.data_entry = tk.Entry(self.root, width=50)
        self.data_entry.grid(row=2, column=1, padx=10)

        self.password_label = tk.Label(self.root, text="Enter Password:")
        self.password_label.grid(row=3, column=0, sticky="w", padx=10)

        self.password_entry = tk.Entry(self.root, width=50, show="*")
        self.password_entry.grid(row=3, column=1, padx=10)

        self.product_manufactured_btn = tk.Button(self.root, text="Product Manufactured", command=self.add_product_manufactured)
        self.product_manufactured_btn.grid(row=5, column=0, padx=10, pady=5)

        self.product_in_warehouse_btn = tk.Button(self.root, text="Product In Warehouse", command=self.add_product_in_warehouse)
        self.product_in_warehouse_btn.grid(row=5, column=1, padx=10, pady=5)

        self.product_shipped_btn = tk.Button(self.root, text="Product Shipped", command=self.add_product_shipped)
        self.product_shipped_btn.grid(row=6, column=0, padx=10, pady=5)

        self.shipment_delayed_btn = tk.Button(self.root, text="Shipment Delayed", command=self.add_shipment_delayed)
        self.shipment_delayed_btn.grid(row=6, column=1, padx=10, pady=5)

        self.product_received_btn = tk.Button(self.root, text="Product Received", command=self.add_product_received)
        self.product_received_btn.grid(row=7, column=0, padx=10, pady=5)

        self.payment_made_btn = tk.Button(self.root, text="Payment Made", command=self.add_payment_made)
        self.payment_made_btn.grid(row=7, column=1, padx=10, pady=5)

        self.payment_received_btn = tk.Button(self.root, text="Payment Received", command=self.add_payment_received)
        self.payment_received_btn.grid(row=8, column=0, padx=10, pady=5)

        self.get_history_btn = tk.Button(self.root, text="Get Product History", command=self.view_product_history)
        self.get_history_btn.grid(row=9, column=0, columnspan=2, pady=5)

        self.update_blockchain_display()

    def add_block(self, block_type):  
        product_id = self.data_entry.get()
        password = self.password_entry.get()

        if not product_id or not block_type or not password:
            messagebox.showerror("Input Error", "Please fill in all fields.")
            return
        
        if block_type == "ProductManufactured":
            self.blockchain.initialize_product(product_id)
        
        if self.blockchain.add_block(product_id, block_type, password):
            messagebox.showinfo("Success", f"Block of type '{block_type}' added successfully.")
            self.update_blockchain_display()

            self.data_entry.delete(0, tk.END)
            self.password_entry.delete(0, tk.END)

    def update_blockchain_display(self):
        self.blockchain_display.delete(0, tk.END)
        for i, block in enumerate(self.blockchain.get_chain()):
            self.blockchain_display.insert(tk.END, f"Block {i}: Data -> {block.data}, Timestamp -> {block.timestamp}, Hash -> {block.block_hash}")

    def add_product_manufactured(self):
        self.add_block("ProductManufactured")

    def add_product_in_warehouse(self):
        self.add_block("ProductInWarehouse")

    def add_product_shipped(self):
        self.add_block("ProductShipped")

    def add_shipment_delayed(self):
        self.add_block("ShipmentDelayed")

    def add_product_received(self):
        self.add_block("ProductReceived")

    def add_payment_made(self):
        self.add_block("PaymentMade")

    def add_payment_received(self):
        self.add_block("PaymentReceived")
    
    def view_product_history(self):
        product_id = self.data_entry.get()
        if not product_id:
            messagebox.showerror("Input Error", "Please enter a Product ID.")
            return
        
        history = self.blockchain.get_product_history(product_id)
        if not history:
            messagebox.showinfo("No History", f"No history found for Product ID: {product_id}.")
            return
        
        self.blockchain_display.delete(0, tk.END)
        for block in history:
            self.blockchain_display.insert(tk.END, f"Block Data: {block.data}, Timestamp: {block.timestamp}, Hash: {block.block_hash}")


def main():
    blockchain = Blockchain()

    root = tk.Tk()
    app = BlockchainApp(root, blockchain)
    root.mainloop()

if __name__ == "__main__":
    main()
