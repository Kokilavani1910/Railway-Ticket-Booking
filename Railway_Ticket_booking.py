#--------------------------------------- Imports ---------------------------------------#
import bcrypt
import tkinter as tk
from tkinter import messagebox, ttk
import mysql.connector
import logging
import re
#--------------------------------------- Logging Setup ---------------------------------#
logging.basicConfig(filename='railway_booking.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s', encoding='utf-8')
#--------------------------------------- Database Connection ---------------------------#
try:
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password=" ",#Enter Your password
        
    )
    
    cursor = conn.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS railway_booking")
    cursor.execute("USE railway_booking")
    
except mysql.connector.Error as err:
    logging.error(f"Error connecting to MySQL: {err}")
    messagebox.showerror("Database Error", "Unable to connect to the database. Please check your connection.")
    raise SystemExit
#--------------------------------------- Create Tables ---------------------------------#
def create_tables():
    cursor.execute('''CREATE TABLE IF NOT EXISTS ChennaiExp (
        seat_num INT PRIMARY KEY,
        status INT
    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS DelhiRajdhani (
        seat_num INT PRIMARY KEY,
        status INT
    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS MumbaiDuronto (
        seat_num INT PRIMARY KEY,
        status INT
    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(50) NOT NULL UNIQUE,
        email VARCHAR(100) NOT NULL UNIQUE,
        password VARCHAR(255) NOT NULL,
        name VARCHAR(255) NOT NULL,
        age INT(3) NOT NULL
    )''')

create_tables()
#--------------------------------------- Initialize Seats ------------------------------#
def initialize_seats(train_name):
    for seat_num in range(1, 81):
        cursor.execute(f"INSERT IGNORE INTO {train_name} (seat_num, status) VALUES (%s, %s)", (seat_num, 1))
    conn.commit()

initialize_seats("ChennaiExp")
initialize_seats("DelhiRajdhani")
initialize_seats("MumbaiDuronto")
#--------------------------------------- User Authentication ---------------------------#
def authenticate_user(username, password):
    cursor.execute("SELECT password FROM users WHERE username = %s", (username,))
    result = cursor.fetchone()
    if result and bcrypt.checkpw(password.encode('utf-8'), result[0].encode('utf-8')):
        return True
    return False

def register_user(username, email, password, name, age):
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    try:
        cursor.execute("INSERT INTO users (username, email, password, name, age) VALUES (%s, %s, %s, %s, %s)",
                       (username, email, hashed_password.decode('utf-8'), name, age))
        conn.commit()
        messagebox.showinfo("Registration Successful", "User registered successfully! You can now log in.")
        
    except mysql.connector.IntegrityError as e:
        if "Duplicate entry" in str(e):
            if "for key 'username'" in str(e):
                messagebox.showerror("Registration Failed", "Username already exists. Please choose another one.")
            elif "for key 'email'" in str(e):
                messagebox.showerror("Registration Failed", "Email ID already exists. Please use another one.")
        else:
            messagebox.showerror("Registration Failed", "An error occurred during registration.")

def login():
    username = username_entry.get()
    password = password_entry.get()

    # Authenticate user and proceed if successful
    if authenticate_user(username, password):
        messagebox.showinfo("Login Successful", f"Welcome, {username}!")
        username_entry.delete(0, tk.END)
        password_entry.delete(0, tk.END)

        # Ensure login window is destroyed before opening train selection
        if login_window:
            login_window.destroy()

        # Now open the train selection window
        open_train_selection()
    else:
        messagebox.showerror("Login Failed", "Invalid username or password.")

def open_signup_window():
    signup_window = tk.Toplevel(login_window)
    signup_window.title("Sign Up")
    signup_window.geometry("400x400")
    signup_window.configure(bg="#f0f0f0")

    tk.Label(signup_window, text="Username").pack(pady=5)
    username_signup_entry = tk.Entry(signup_window)
    username_signup_entry.pack(pady=5)

    tk.Label(signup_window, text="Email").pack(pady=5)
    email_signup_entry = tk.Entry(signup_window)
    email_signup_entry.pack(pady=5)

    tk.Label(signup_window, text="Name").pack(pady=5)
    name_signup_entry = tk.Entry(signup_window)
    name_signup_entry.pack(pady=5)

    tk.Label(signup_window, text="Age").pack(pady=5)
    age_signup_entry = tk.Entry(signup_window)
    age_signup_entry.pack(pady=5)

    tk.Label(signup_window, text="Password").pack(pady=5)
    password_signup_entry = tk.Entry(signup_window, show="*")
    password_signup_entry.pack(pady=5)

    tk.Label(signup_window, text="Re-enter Password").pack(pady=5)
    reenter_password_signup_entry = tk.Entry(signup_window, show="*")
    reenter_password_signup_entry.pack(pady=5)

    tk.Button(signup_window, text="Sign Up", bg="green", command=lambda: validate_signup(
        username_signup_entry.get(), 
        email_signup_entry.get(), 
        password_signup_entry.get(), 
        reenter_password_signup_entry.get(), 
        name_signup_entry.get(), 
        age_signup_entry.get()
    )).pack(pady=5)

def validate_signup(username, email, password, reenter_password, name, age):
    if not (username and name and age and email and password and reenter_password):
        messagebox.showerror("Input Error", "Please fill all the fields.")
        return
    if password != reenter_password:
        messagebox.showerror("Password Error", "Passwords do not match. Please re-enter.")
        return
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    if not re.match(email_regex, email):
        messagebox.showerror("Email Error", "Please enter a valid email address.")
        return
    if len(password) < 8:
        messagebox.showerror("Password Error", "Password must be at least 8 characters long.")
        return
    if not re.search("[a-z]", password):
        messagebox.showerror("Password Error", "Password must contain at least one lowercase letter.")
        return
    if not re.search("[A-Z]", password):
        messagebox.showerror("Password Error", "Password must contain at least one uppercase letter.")
        return
    if not re.search("[0-9]", password):
        messagebox.showerror("Password Error", "Password must contain at least one digit.")
        return
    if not re.search("[!@#$%^&*(),.?\":{}|<>]", password):
        messagebox.showerror("Password Error", "Password must contain at least one special character.")
        return
    if not age.isdigit() or int(age) <= 0:
        messagebox.showerror("Input Error", "Please enter a valid age.")
        return

    register_user(username, email, password, name, age)

#--------------------------------------- Train Selection ---------------------------#

def open_train_selection():
    train_window = tk.Tk()
    train_window.title("Select Train")
    train_window.geometry("400x300")
    
    tk.Label(train_window, text="Please select a train:", font=("Arial", 14)).pack(pady=20)

    trains = ["Chennai Exp", "Delhi Rajdhani", "Mumbai Duronto"]
    selected_train = ttk.Combobox(train_window, values=trains, state="readonly")
    selected_train.pack(pady=10)

    tk.Button(train_window, text="Proceed", command=lambda: open_train_specific_window(selected_train.get())).pack(pady=20)

def open_train_specific_window(train):
    train_classes = {
        "Chennai Exp": ChennaiExp,
        "Delhi Rajdhani": DelhiRajdhani,
        "Mumbai Duronto": MumbaiDuronto
    }

    if train in train_classes:
        train_instance = train_classes[train]()
        train_instance.open_booking_page()
    else:
        messagebox.showerror("Selection Error", "Please select a valid train.")

#---------------------------------------------------- Base class for train booking system---------------------------------------------------------#
class TrainBooking:
    def __init__(self, train_name, departure_options, distance_data):
        self.train_name = train_name
        self.departure_options = departure_options
        self.distance_data = distance_data
        self.train_window = None
        self.departure_entry = None
        self.destination_entry = None
        self.seat_buttons = {}  # Store seat buttons
        
    def open_booking_page(self):
        self.train_window = tk.Tk()
        self.train_window.title(f"{self.train_name} Booking")
        self.train_window.geometry("1000x1000")

        tk.Label(self.train_window, text=self.train_name, font=("Arial", 16)).pack(pady=10)

        tk.Label(self.train_window, text="Departure From:").pack(pady=5)
        self.departure_entry = ttk.Combobox(self.train_window, values=self.departure_options)
        self.departure_entry.pack(pady=5)

        tk.Label(self.train_window, text="Destination To:").pack(pady=5)
        self.destination_entry = ttk.Combobox(self.train_window, values=self.departure_options)
        self.destination_entry.pack(pady=5)

        self.check_button = tk.Button(self.train_window, text="Check Seat Availability", command=self.check_availability)
        self.check_button.pack(pady=20)

    def check_availability(self):
        
        self.display_seat_availability()

        self.check_button.config(state="disabled")


    def get_distance(self, departure, destination):
        return self.distance_data.get((departure, destination), 0)
    
    def calculate_fare(self, distance):
        base_fare=10
        return base_fare + distance * 2

    def book_seat(self, seat_num):
        try:
            if self.train_window is None or not self.train_window.winfo_exists():
                raise Exception("The booking window has been closed.")

            departure = self.departure_entry.get()
            destination = self.destination_entry.get()

            if not departure or not destination:
                messagebox.showerror("Input Error", "Please select both departure and destination.")
                return

            cursor.execute(f"SELECT status FROM {self.train_name} WHERE seat_num = %s", (seat_num,))
            status = cursor.fetchone()

            if status and status[0] == 1:
                distance = self.get_distance(departure, destination)
                if distance == 0:
                    messagebox.showerror("Error", "Distance not defined for the selected route.")
                    return
                fare = self.calculate_fare(distance)
                berth_type = self.berth_confirmation(seat_num)
                
                cursor.execute(f"UPDATE {self.train_name} SET status = 0 WHERE seat_num = %s", (seat_num,))
                conn.commit()
                messagebox.showinfo("Booking Successful",
                                    f"Seat {seat_num} booked successfully!\n"
                                    f"Berth Type: {berth_type}\n"
                                    f"From: {departure}\nTo: {destination}\n"
                                    f"Distance: {distance} km\nFare: ₹{fare}.")
                logging.info(f"Seat {seat_num} booked on {self.train_name}. From: {departure} To: {destination} Fare: ₹{fare}")

                self.seat_buttons[seat_num].config(bg="red", state="disabled")

            else:
                messagebox.showerror("Booking Failed", "This seat is already booked.")

        except Exception as e:
            logging.error(f"Error booking seat {seat_num}: {e}")
            messagebox.showerror("Booking Error", f"An error occurred: {e}")
    def display_seat_availability(self):
        seat_frame = tk.Frame(self.train_window)
        seat_frame.pack(pady=20)
        
        for button in self.seat_buttons.values():
            button.destroy()
        self.seat_buttons.clear()

        for seat_num in range(1, 81):
            cursor.execute(f"SELECT status FROM {self.train_name} WHERE seat_num = %s", (seat_num,))
            status = cursor.fetchone()
            if status:
                if status[0] == 1:
                    seat_status = "Available"
                    seat_color = "green" 
                else:
                    seat_status="Booked"
                    seat_color ="red"
               
                button = tk.Button(seat_frame, text=f"Seat {seat_num} - {seat_status}", bg=seat_color,
                                   command=lambda num=seat_num: self.book_seat(num) if seat_status == "Available" else None)
                button.grid(row=(seat_num - 1) // 8, column=(seat_num - 1) % 8, padx=5, pady=5)
                self.seat_buttons[seat_num] = button

    def berth_confirmation(self, seat_num):
        if seat_num % 8 == 1 or seat_num % 8 == 4:
            return "Lower Berth"
        elif seat_num % 8 == 2 or seat_num % 8 == 5:
            return "Middle Berth"
        elif seat_num % 8 == 3 or seat_num % 8 == 6:
            return "Upper Berth"
        elif seat_num % 8 == 7:
            return "Side Lower"
        elif seat_num % 8 == 0:
            return "Side Upper"

           
#------------------------------------ Chennai Exp train class---------------------------#
class ChennaiExp(TrainBooking):
    def __init__(self):
        super().__init__(
            train_name="ChennaiExp",
            departure_options=sorted([
                "HYDERABAD DECAN", "SECUNDERABAD JN", "NALGONDA", "MIRYALAGUDA",
                "NADIKODE", "PIDUGURALLA", "SATTENAPALLE", "GUNTUR JN",
                "TENALI JN", "NIDUBROLU", "BAPATLA", "CHIRALA", "ONGOLE",
                "SINGARAYAKONDA", "KAVALI", "NELLORE", "GUDUR JN", "SULLURUPETA",
                "CHENNAI CENTRAL"
            ]),
            distance_data={
                ("CHENNAI CENTRAL", "GUDUR JN"): 137,
                ("CHENNAI CENTRAL", "NELLORE"): 176,
                ("CHENNAI CENTRAL", "KAVALI"): 218,
                ("CHENNAI CENTRAL", "SINGARAYAKONDA"): 254,
                ("CHENNAI CENTRAL", "ONGOLE"): 292,
                ("CHENNAI CENTRAL", "CHIRALA"): 321,
                ("CHENNAI CENTRAL", "BAPATLA"): 340,
                ("CHENNAI CENTRAL", "NIDUBROLU"): 357,
                ("CHENNAI CENTRAL", "TENALI JN"): 375,
                ("CHENNAI CENTRAL", "GUNTUR JN"): 402,
                ("CHENNAI CENTRAL", "SATTENAPALLE"): 437,
                ("CHENNAI CENTRAL", "PIDUGURALLA"): 471,
                ("CHENNAI CENTRAL", "NADIKODE"): 500,
                ("CHENNAI CENTRAL", "MIRYALAGUDA"): 537,
                ("CHENNAI CENTRAL", "NALGONDA"): 573,
                ("CHENNAI CENTRAL", "SECUNDERABAD JN"): 705,
                ("CHENNAI CENTRAL", "HYDERABAD DECAN"): 715,
                
                ("GUDUR JN", "NELLORE"): 37,
                ("GUDUR JN", "KAVALI"): 79,
                ("GUDUR JN", "SINGARAYAKONDA"): 115,
                ("GUDUR JN", "ONGOLE"): 151,
                ("GUDUR JN", "CHIRALA"): 189,
                ("GUDUR JN", "BAPATLA"): 208,
                ("GUDUR JN", "NIDUBROLU"): 226,
                ("GUDUR JN", "TENALI JN"): 238,
                ("GUDUR JN", "GUNTUR JN"): 247,
                ("GUDUR JN", "SATTENAPALLE"): 282,
                ("GUDUR JN", "PIDUGURALLA"): 316,
                ("GUDUR JN", "NADIKODE"): 345,
                ("GUDUR JN", "MIRYALAGUDA"): 382,
                ("GUDUR JN", "NALGONDA"): 418,
                ("GUDUR JN", "SECUNDERABAD JN"): 550,
                ("GUDUR JN", "HYDERABAD DECAN"): 560,
                
                ("NELLORE", "KAVALI"): 42,
                ("NELLORE", "SINGARAYAKONDA"): 78,
                ("NELLORE", "ONGOLE"): 114,
                ("NELLORE", "CHIRALA"): 152,
                ("NELLORE", "BAPATLA"): 171,
                ("NELLORE", "NIDUBROLU"): 189,
                ("NELLORE", "TENALI JN"): 201,
                ("NELLORE", "GUNTUR JN"): 210,
                ("NELLORE", "SATTENAPALLE"): 245,
                ("NELLORE", "PIDUGURALLA"): 279,
                ("NELLORE", "NADIKODE"): 308,
                ("NELLORE", "MIRYALAGUDA"): 345,
                ("NELLORE", "NALGONDA"): 381,
                ("NELLORE", "SECUNDERABAD JN"): 513,
                ("NELLORE", "HYDERABAD DECAN"): 523,
                
                ("KAVALI", "SINGARAYAKONDA"): 36,
                ("KAVALI", "ONGOLE"): 72,
                ("KAVALI", "CHIRALA"): 110,
                ("KAVALI", "BAPATLA"): 129,
                ("KAVALI", "NIDUBROLU"): 147,
                ("KAVALI", "TENALI JN"): 159,
                ("KAVALI", "GUNTUR JN"): 168,
                ("KAVALI", "SATTENAPALLE"): 203,
                ("KAVALI", "PIDUGURALLA"): 237,
                ("KAVALI", "NADIKODE"): 266,
                ("KAVALI", "MIRYALAGUDA"): 303,
                ("KAVALI", "NALGONDA"): 339,
                ("KAVALI", "SECUNDERABAD JN"): 471,
                ("KAVALI", "HYDERABAD DECAN"): 481,
                
                ("SINGARAYAKONDA", "ONGOLE"): 36,
                ("SINGARAYAKONDA", "CHIRALA"): 74,
                ("SINGARAYAKONDA", "BAPATLA"): 93,
                ("SINGARAYAKONDA", "NIDUBROLU"): 111,
                ("SINGARAYAKONDA", "TENALI JN"): 123,
                ("SINGARAYAKONDA", "GUNTUR JN"): 132,
                ("SINGARAYAKONDA", "SATTENAPALLE"): 167,
                ("SINGARAYAKONDA", "PIDUGURALLA"): 201,
                ("SINGARAYAKONDA", "NADIKODE"): 230,
                ("SINGARAYAKONDA", "MIRYALAGUDA"): 267,
                ("SINGARAYAKONDA", "NALGONDA"): 303,
                ("SINGARAYAKONDA", "SECUNDERABAD JN"): 435,
                ("SINGARAYAKONDA", "HYDERABAD DECAN"): 445,
                
                ("ONGOLE", "CHIRALA"): 38,
                ("ONGOLE", "BAPATLA"): 57,
                ("ONGOLE", "NIDUBROLU"): 75,
                ("ONGOLE", "TENALI JN"): 87,
                ("ONGOLE", "GUNTUR JN"): 96,
                ("ONGOLE", "SATTENAPALLE"): 131,
                ("ONGOLE", "PIDUGURALLA"): 165,
                ("ONGOLE", "NADIKODE"): 194,
                ("ONGOLE", "MIRYALAGUDA"): 231,
                ("ONGOLE", "NALGONDA"): 267,
                ("ONGOLE", "SECUNDERABAD JN"): 399,
                ("ONGOLE", "HYDERABAD DECAN"): 409,
                
                ("CHIRALA", "BAPATLA"): 19,
                ("CHIRALA", "NIDUBROLU"): 37,
                ("CHIRALA", "TENALI JN"): 49,
                ("CHIRALA", "GUNTUR JN"): 58,
                ("CHIRALA", "SATTENAPALLE"): 93,
                ("CHIRALA", "PIDUGURALLA"): 127,
                ("CHIRALA", "NADIKODE"): 156,
                ("CHIRALA", "MIRYALAGUDA"): 193,
                ("CHIRALA", "NALGONDA"): 229,
                ("CHIRALA", "SECUNDERABAD JN"): 361,
                ("CHIRALA", "HYDERABAD DECAN"): 371,
                
                ("BAPATLA", "NIDUBROLU"): 18,
                ("BAPATLA", "TENALI JN"): 30,
                ("BAPATLA", "GUNTUR JN"): 40,
                ("BAPATLA", "SATTENAPALLE"): 75,
                ("BAPATLA", "PIDUGURALLA"): 109,
                ("BAPATLA", "NADIKODE"): 138,
                ("BAPATLA", "MIRYALAGUDA"): 175,
                ("BAPATLA", "NALGONDA"): 211,
                ("BAPATLA", "SECUNDERABAD JN"): 343,
                ("BAPATLA", "HYDERABAD DECAN"): 353,
                
                ("NIDUBROLU", "TENALI JN"): 12,
                ("NIDUBROLU", "GUNTUR JN"): 22,
                ("NIDUBROLU", "SATTENAPALLE"): 57,
                ("NIDUBROLU", "PIDUGURALLA"): 91,
                ("NIDUBROLU", "NADIKODE"): 120,
                ("NIDUBROLU", "MIRYALAGUDA"): 157,
                ("NIDUBROLU", "NALGONDA"): 193,
                ("NIDUBROLU", "SECUNDERABAD JN"): 325,
                ("NIDUBROLU", "HYDERABAD DECAN"): 335,
                
                ("TENALI JN", "GUNTUR JN"): 10,
                ("TENALI JN", "SATTENAPALLE"): 45,
                ("TENALI JN", "PIDUGURALLA"): 79,
                ("TENALI JN", "NADIKODE"): 108,
                ("TENALI JN", "MIRYALAGUDA"): 145,
                ("TENALI JN", "NALGONDA"): 181,
                ("TENALI JN", "SECUNDERABAD JN"): 313,
                ("TENALI JN", "HYDERABAD DECAN"): 323,
                
                ("GUNTUR JN", "SATTENAPALLE"): 35,
                ("GUNTUR JN", "PIDUGURALLA"): 69,
                ("GUNTUR JN", "NADIKODE"): 98,
                ("GUNTUR JN", "MIRYALAGUDA"): 135,
                ("GUNTUR JN", "NALGONDA"): 171,
                ("GUNTUR JN", "SECUNDERABAD JN"): 303,
                ("GUNTUR JN", "HYDERABAD DECAN"): 313,
                
                ("SATTENAPALLE", "PIDUGURALLA"): 34,
                ("SATTENAPALLE", "NADIKODE"): 63,
                ("SATTENAPALLE", "MIRYALAGUDA"): 100,
                ("SATTENAPALLE", "NALGONDA"): 136,
                ("SATTENAPALLE", "SECUNDERABAD JN"): 268,
                ("SATTENAPALLE", "HYDERABAD DECAN"): 278,
                
                ("PIDUGURALLA", "NADIKODE"): 29,
                ("PIDUGURALLA", "MIRYALAGUDA"): 66,
                ("PIDUGURALLA", "NALGONDA"): 102,
                ("PIDUGURALLA", "SECUNDERABAD JN"): 234,
                ("PIDUGURALLA", "HYDERABAD DECAN"): 244,
                
                ("NADIKODE", "MIRYALAGUDA"): 37,
                ("NADIKODE", "NALGONDA"): 73,
                ("NADIKODE", "SECUNDERABAD JN"): 205,
                ("NADIKODE", "HYDERABAD DECAN"): 215,
                
                ("MIRYALAGUDA", "NALGONDA"): 36,
                ("MIRYALAGUDA", "SECUNDERABAD JN"): 168,
                ("MIRYALAGUDA", "HYDERABAD DECAN"): 178,
                
                ("NALGONDA", "SECUNDERABAD JN"): 132,
                ("NALGONDA", "HYDERABAD DECAN"): 142,
                
                ("SECUNDERABAD JN", "HYDERABAD DECAN"): 10
            }
        )
#----------------------------- Delhi Rajdhani train class-----------------------------#
class DelhiRajdhani(TrainBooking):
    def __init__(self):
        super().__init__(
            train_name="DelhiRajdhani",
            departure_options=sorted([
                "NEW DELHI", "KANPUR CENTRAL", "PT DEEN DAYAL UPADHYAYA JN", 
                "GAYA JN", "DHANBAD JN", "ASANSOL JN", "DURGAPUR", "KOLKATA SEALDAH"
            ]),
            distance_data={
                ("NEW DELHI", "KANPUR CENTRAL"): 440,
                ("NEW DELHI", "PT DEEN DAYAL UPADHYAYA JN"): 765,
                ("NEW DELHI", "GAYA JN"): 1034,
                ("NEW DELHI", "DHANBAD JN"): 890,
                ("NEW DELHI", "ASANSOL JN"): 926,
                ("NEW DELHI", "DURGAPUR"): 1066,
                ("NEW DELHI", "KOLKATA SEALDAH"): 1465,
                
                ("KANPUR CENTRAL", "PT DEEN DAYAL UPADHYAYA JN"): 326,
                ("KANPUR CENTRAL", "GAYA JN"): 681,
                ("KANPUR CENTRAL", "DHANBAD JN"): 368,
                ("KANPUR CENTRAL", "ASANSOL JN"): 399,
                ("KANPUR CENTRAL", "DURGAPUR"): 539,
                ("KANPUR CENTRAL", "KOLKATA SEALDAH"): 880,
                
                ("PT DEEN DAYAL UPADHYAYA JN", "GAYA JN"): 211,
                ("PT DEEN DAYAL UPADHYAYA JN", "DHANBAD JN"): 429,
                ("PT DEEN DAYAL UPADHYAYA JN", "ASANSOL JN"): 458,
                ("PT DEEN DAYAL UPADHYAYA JN", "DURGAPUR"): 598,
                ("PT DEEN DAYAL UPADHYAYA JN", "KOLKATA SEALDAH"): 905,
                
                ("GAYA JN", "DHANBAD JN"): 198,
                ("GAYA JN", "ASANSOL JN"): 248,
                ("GAYA JN", "DURGAPUR"): 348,
                ("GAYA JN", "KOLKATA SEALDAH"): 450,
                
                ("DHANBAD JN", "ASANSOL JN"): 58,
                ("DHANBAD JN", "DURGAPUR"): 112,
                ("DHANBAD JN", "KOLKATA SEALDAH"): 362,
                
                ("ASANSOL JN", "DURGAPUR"): 43,
                ("ASANSOL JN", "KOLKATA SEALDAH"): 139,
                
                ("DURGAPUR", "KOLKATA SEALDAH"): 159,
            }
        )


#----------------------------- Mumbai Duronto train class------------------------------#
class MumbaiDuronto(TrainBooking):
    def __init__(self):
        super().__init__(
            train_name="MumbaiDuronto",
            departure_options=sorted([
                "HOWRAH JN", "TATANAGAR JN", "BILASPUR JN", "RAIPUR JN", 
                "NAGPUR", "BHUSAVAL JN", "KALYAN JN", "MUMBAI CSMT"
            ]),
            distance_data={
                ("HOWRAH JN", "TATANAGAR JN"): 250,
                ("HOWRAH JN", "BILASPUR JN"): 594,
                ("HOWRAH JN", "RAIPUR JN"): 691,
                ("HOWRAH JN", "NAGPUR"): 940,
                ("HOWRAH JN", "BHUSAVAL JN"): 1020,
                ("HOWRAH JN", "KALYAN JN"): 1140,
                ("HOWRAH JN", "MUMBAI CSMT"): 1460,

                ("TATANAGAR JN", "BILASPUR JN"): 360,
                ("TATANAGAR JN", "RAIPUR JN"): 287,
                ("TATANAGAR JN", "NAGPUR"): 457,
                ("TATANAGAR JN", "BHUSAVAL JN"): 623,
                ("TATANAGAR JN", "KALYAN JN"): 795,
                ("TATANAGAR JN", "MUMBAI CSMT"): 1125,

                ("BILASPUR JN", "RAIPUR JN"): 111,
                ("BILASPUR JN", "NAGPUR"): 215,
                ("BILASPUR JN", "BHUSAVAL JN"): 290,
                ("BILASPUR JN", "KALYAN JN"): 463,
                ("BILASPUR JN", "MUMBAI CSMT"): 715,

                ("RAIPUR JN", "NAGPUR"): 292,
                ("RAIPUR JN", "BHUSAVAL JN"): 365,
                ("RAIPUR JN", "KALYAN JN"): 543,
                ("RAIPUR JN", "MUMBAI CSMT"): 785,

                ("NAGPUR", "BHUSAVAL JN"): 422,
                ("NAGPUR", "KALYAN JN"): 610,
                ("NAGPUR", "MUMBAI CSMT"): 850,

                ("BHUSAVAL JN", "KALYAN JN"): 405,
                ("BHUSAVAL JN", "MUMBAI CSMT"): 648,

                ("KALYAN JN", "MUMBAI CSMT"): 54,
            }
        )
#--------------------------------Login Window--------------------------------------#
# Main Login window
login_window = tk.Tk()
login_window.title("Railway Booking System - Login")
login_window.geometry("400x300")

tk.Label(login_window, text="Username").pack(pady=10)
username_entry = tk.Entry(login_window)
username_entry.pack(pady=5)

tk.Label(login_window, text="Password").pack(pady=10)
password_entry = tk.Entry(login_window, show="*")
password_entry.pack(pady=5)

tk.Button(login_window, text="Login", command=login, bg="green").pack(pady=20)

tk.Button(login_window, text="Sign Up", command=open_signup_window, bg="blue").pack()

login_window.mainloop()

#--------------------------------------- Close Connection -------------------------------#
cursor.close()
conn.close()
