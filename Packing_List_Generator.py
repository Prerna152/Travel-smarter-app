#Packing List Generator


# Basic packing items
basic_items = {
    "Clothing": ["T-shirts", "Pants", "Underwear", "Socks", "Jacket"],
    "Toiletries": ["Toothbrush", "Toothpaste", "Shampoo", "Soap", "Deodorant"],
    "Electronics": ["Phone", "Charger", "Headphones"],
    "Travel Essentials": ["Passport", "Wallet", "Sunglasses", "Snacks"],
    "Activity" : [],
}

# Additional items based on activities
activity_items = {
    "Beach vacation": ["Swimsuit", "Towel", "Sunscreen", "Flip flops", "Beach hat", "Beach bag"],
    "Hiking trip": ["Hiking boots", "Water bottle", "Map", "Compass", "Sunscreen", "Backpack", "Snacks"],
    "Business travel": ["Laptop", "Notebook", "Pen", "Business cards", "Formal attire", "Travel adapter", "Work documents"],
    "Winter Wonderland": ["Gloves", "Hat", "Scarf", "Snow boots", "Thermal wear", "Heavy jacket", "Snow goggles"],
    "Camping": ["Tent", "Sleeping bag", "Flashlight", "Camping stove", "Camping chair", "First aid kit", "Insect repellent"]
}

# Function to generate packing list
def generate_packing_list(destination, duration, activities):
    packing_list = basic_items.copy()
    
    # Add items based on duration
    if duration > 7:
        packing_list["Clothing"].append("Extra T-shirts")
        packing_list["Clothing"].append("Extra Pants")
    if duration > 14:
        packing_list["Clothing"].append("Laundry bag")
    
    packing_list['Activity'] = activity_items.get(activities)

   
    return packing_list



