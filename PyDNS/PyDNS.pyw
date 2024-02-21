import tkinter as tk
import requests
import threading
import time

def get_public_ip():
    try:
        response = requests.get("https://api.ipify.org?format=json")
        data = response.json()
        return data["ip"]
    except requests.RequestException:
        return "Error fetching IP address"

def auto_update_ip():
    while True:
        public_ip = get_public_ip()
        ip_label.config(text=f"Public IP: {public_ip}")
        time.sleep(3 * 60 * 60)  # Sleep for 3 hours

def update_ddns():
    domain = domain_entry.get()
    hosts = host_entry.get().split(",")  # Split hosts by comma
    ddnskey = ddnskey_entry.get()

    try:
        # Get public IP address
        ip = requests.get("https://api.ipify.org").text

        # Update Namecheap DDNS for each host
        for host in hosts:
            response = requests.get(f"https://dynamicdns.park-your-domain.com/update?host={host}&domain={domain}&password={ddnskey}&ip={ip}")
            if "<ErrCount>0</ErrCount>" in response.text:
                result_label.config(text=f"DDNS update successful for {host}")
            else:
                result_label.config(text=f"DDNS update failed for {host}")
    except requests.RequestException:
        result_label.config(text="Error updating DDNS")

    # Save the entered values to a file
    with open("ddns_config.txt", "w") as config_file:
        config_file.write(f"Domain: {domain}\nHosts: {', '.join(hosts)}\nDDNS Key: {ddnskey}")

def load_saved_values():
    try:
        with open("ddns_config.txt", "r") as config_file:
            lines = config_file.readlines()
            domain_entry.insert(0, lines[0].split(":")[1].strip())
            host_entry.insert(0, lines[1].split(":")[1].strip())
            ddnskey_entry.insert(0, lines[2].split(":")[1].strip())
    except FileNotFoundError:
        pass  # File doesn't exist yet

def auto_update():
    while True:
        update_ddns()
        time.sleep(3 * 60 * 60)  # Sleep for 3 hours

# Create GUI
root = tk.Tk()
root.title("PyDNS DDNS Updater")

# Public IP
ip_label = tk.Label(root, text="Fetching IP address...")
ip_label.pack(pady=10)

# Domain input
domain_label = tk.Label(root, text="Domain:")
domain_label.pack()
domain_entry = tk.Entry(root)
domain_entry.pack()

# Host input
host_label = tk.Label(root, text="Hosts (comma-separated):")
host_label.pack()
host_entry = tk.Entry(root)
host_entry.pack()

# DDNS key input
ddnskey_label = tk.Label(root, text="DDNS Key:")
ddnskey_label.pack()
ddnskey_entry = tk.Entry(root)
ddnskey_entry.pack()

# Load saved values
load_saved_values()

update_button = tk.Button(root, text="Update DDNS", command=update_ddns)
update_button.pack(pady=10)

result_label = tk.Label(root, text="")
result_label.pack()


# Start auto-updating thread
auto_update_thread = threading.Thread(target=auto_update_ip)
auto_update_thread.daemon = True
auto_update_thread.start()

# Start auto-updating thread
auto_update_thread = threading.Thread(target=auto_update)
auto_update_thread.daemon = True
auto_update_thread.start()

root.mainloop()
