import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from db import get_connection

seed_patients = [
    ("Ravi Kumar", "Suresh Kumar", 34, "Male", "9876543210", "9876543210", "123456789012",
     "12-5-33, Hyderabad", "Kukatpally", None,
     "Vegetarian", "Idli + sambar", "Rice + dal", "Chapati + curry",
     "No", "No", "Moderately active", "Father: Diabetes"),

    ("Anjali Sharma", "Rajesh Sharma", 28, "Female", "9123456789", "9123456789", "234567890123",
     "Banjara Hills, Hyderabad", "Shamirpet", None,
     "Non-vegetarian", "Poha", "Roti + dal", "Rice + chicken curry",
     "No", "Occasional", "Lightly active", "Mother: Hypertension"),

    ("Mohammed Imran", "Mohammed Yousuf", 45, "Male", "9988776655", "9988776655", "345678901234",
     "Charminar, Hyderabad", "Moinabad", None,
     "Vegetarian", "Dosa + chutney", "Rice + sambar", "Chapati + paneer",
     "Yes", "Yes", "Sedentary", "Grandfather: Heart disease"),

    ("Priya Verma", "Anil Verma", 31, "Female", "9011223344", "9011223344", "456789012345",
     "Kondapur, Hyderabad", "Narsingi", None,
     "Vegan", "Smoothie", "Quinoa + veggies", "Soup + salad",
     "No", "No", "Very active", "No major history"),
]

conn = get_connection()
cur = conn.cursor()

cur.executemany("""
INSERT INTO patients
(name, father_name, age, gender, phone, mobile, aadhar, address, village, photo_path,
 diet, breakfast, lunch, dinner, tobacco, alcohol, activity_level, family_history)
VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
""", seed_patients)

conn.commit()
conn.close()

print("Seed data inserted successfully ✅")
