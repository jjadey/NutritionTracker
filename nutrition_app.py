# Imports and settings
import google.generativeai as genai
import matplotlib.pyplot as plt
import numpy as np
import io
import os
from datetime import date
from PIL import Image
import tkinter as tk
from tkinter.filedialog import askopenfilename


# Nutrition App Backend
class NutritionApp:

    # Constructor
    def __init__(self):    
        self.dates = {}
        self.target_cal = 0
        self.target_pro = 0
        self.target_carb = 0
        self.target_fat = 0
        self.img = None
        self.model = None
        self.verify_user = False
        self.verify_api = False

    # Class to store and track data for a day
    class Entry:

        # Constructor
        def __init__(self, app):
            # Copy targets into a field in case targets change in the future
            self.target_cal = app.target_cal
            self.target_pro = app.target_pro
            self.target_carb = app.target_carb
            self.target_fat = app.target_fat
            self.current_cal = 0
            self.current_pro = 0
            self.current_carb = 0
            self.current_fat = 0
            self.meals = []

        # Returns the progress of the current metrics to the target as a percentage, using all meals combined
        def get_total_progress(self):
            return [
                self.current_cal / self.target_cal * 100,
                self.current_pro / self.target_pro * 100,
                self.current_carb / self.target_carb * 100,
                self.current_fat / self.target_fat * 100,
            ]

        # Returns the progress of the current metrics to the target as a percentage, showing the contribution of each meal
        def get_split_progress(self):
            arr = []
            for meal in self.meals:
                arr.append(
                    [
                        meal.get_cal() / self.target_cal * 100,
                        meal.get_pro() / self.target_pro * 100,
                        meal.get_carb() / self.target_carb * 100,
                        meal.get_fat() / self.target_fat * 100,
                    ]
                )
            return arr

        # Returns the names of all stored meals
        def get_meal_names(self):
            arr = []
            for meal in self.meals:
                arr.append(meal.name)
            return arr

        # Add a meal to the array and update metrics
        def update(self, meal):
            self.meals.append(meal)
            self.current_cal += meal.get_cal()
            self.current_pro += meal.get_pro()
            self.current_carb += meal.get_carb()
            self.current_fat += meal.get_fat()

        # Print all meals
        def __str__(self):
            string = ""
            for meal in self.meals:
                string += str(meal)
            return string

    # Class to consolodate ingredients (items) into a meal
    class Meal:

        # Constructor
        def __init__(self, name, item, cal, pro, carb, fat):
            self.name = name
            self.item = item
            self.cal = cal
            self.pro = pro
            self.carb = carb
            self.fat = fat

        # Getter functions to sum all the ingredients' metrics
        def get_cal(self):
            return sum(self.cal)

        def get_pro(self):
            return sum(self.pro)

        def get_carb(self):
            return sum(self.carb)

        def get_fat(self):
            return sum(self.fat)

        # Print meal name with ingredients and their metrics
        def __str__(self):
            string = self.name + "\n"
            for i in range(len(self.item)):
                string += (
                    "\t"
                    + str(self.item[i])
                    + ", "
                    + str(self.cal[i])
                    + " cal, "
                    + str(self.pro[i])
                    + " g, "
                    + str(self.carb[i])
                    + " g, "
                    + str(self.fat[i])
                    + " g\n"
                )
            string += (
                "\tTotal: "
                + str(self.get_cal())
                + " cal, "
                + str(self.get_pro())
                + " g protein, "
                + str(self.get_carb())
                + " g carbohydrates, "
                + str(self.get_fat())
                + " g fat\n"
            )
            return string

    # Initialize Gemini AI using API key
    def init_gem(self, api_key):
        self.model
        # First, try API key entered by user
        try:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel("gemini-1.5-flash")
            self.model.generate_content("Hello")
            return
        except:
            # Second, check if API key is stored in Environment Variables
            try:
                genai.configure(api_key=os.environ["GEMINI_API_KEY"])
                self.model = genai.GenerativeModel("gemini-1.5-flash")
                self.model.generate_content("Hello")
                return
            except:
                raise Exception("Invalid API key")

    # Initialize target variables using user details
    def init_var(self, sex, weight, height, age):
        # Using Mifflin-St Jeor formula (using kg and cm), and moderately active activity level (1.55x)
        if sex == "male":
            self.target_cal = (10 * weight + 6.25 * height - 5 * age + 5) * 1.55
        else:
            self.target_cal = (10 * weight + 6.25 * height - 5 * age - 161) * 1.55
        # Using composition that calories should come from 25% protein, 50% carbohydrates, and 25% fat. Then convert to grams
        self.target_pro = (0.25 * self.target_cal) / 4
        self.target_carb = (0.5 * self.target_cal) / 4
        self.target_fat = (0.25 * self.target_cal) / 9
        # Require positive metrics
        if (
            self.target_cal <= 0
            or self.target_pro <= 0
            or self.target_carb <= 0
            or self.target_fat <= 0
        ):
            raise Exception("Must be all positive values")

    # Function to open user-specified image
    def choose_image(self):
        tk.Tk().withdraw()
        filename = askopenfilename()
        self.img = Image.open(filename)
        # Downsize image for efficiency
        self.img.thumbnail(
            (200, 200), Image.LANCZOS
        )  # LANCZOS is more intensive but results in better image quality
        return self.img

    # Get a response from Gemini
    def prompt_gemini(self, information):
        # Build question (string)
        instructions = "Using the information provided, estimate the quantity, calories, protein, carbohydrates, and fat of each food item."
        rules = [
            "Be descriptive.",
            "If there are multiple of the same food, combine them. For example, write 2 buns instead of writing 1 bun twice.",
            "Write in this format: # of [food], # cal, # g protein, # g carbohydrate, # g fat.",
            "Give a name for the dish on the first line.",
            "Write each ingredient on a new line.",
            "Use metric measurements.",
            "Round to the nearest whole number.",
            "Do not ask the user for more information.",
            "Do not write a disclaimer.",
            "Do not write a total.",
        ]
        string = (
            "Information: "
            + information
            + "\nInstructions: "
            + instructions
            + "\nRules:"
        )
        for i in rules:
            string += " " + i

        # Ask Gemini
        if self.img is None:
            return self.model.generate_content(string).text
        else:
            return self.model.generate_content([string, self.img]).text

    # Parse response
    def parse_response(self, text):
        split = text.split("\n")
        item = []
        cal = []
        pro = []
        carb = []
        fat = []
        # First line is the meal name
        name = split[0]
        # Loop through one ingredient (item) at a time
        for i in split[1:]:
            # Tokenize the line to seperate each metric
            line = i.split(",")
            # Filter empty lines
            if len(line) == 1:
                continue
            # Add so that an index corresponds to the same ingredient (item) across arrays
            item.append(line[0])
            cal.append(int(line[1].split()[0]))  # The number is always the first token
            pro.append(int(line[2].split()[0]))
            carb.append(int(line[3].split()[0]))
            fat.append(int(line[4].split()[0]))

        # Create meal object
        meal = NutritionApp.Meal(name, item, cal, pro, carb, fat)
        # Store the meal
        today = str(date.today())
        if today not in self.dates:
            self.dates[today] = NutritionApp.Entry(self)
        self.dates[today].update(meal)

        return meal

    # Function to graph the progress on the different metrics for a given day
    def graph_progress(self, date):
        # Plot initial bar chart
        if date not in self.dates:
            raise Exception("No meals for this date")
        x = ["Calories", "Protein", "Carbohydrates", "Fat"]
        y = self.dates[date].get_split_progress()
        plt.bar(x, y[0])
        # Plot stacked bars
        bot = y[0]
        for i in range(1, len(y)):
            plt.bar(x, y[i], bottom=bot)
            bot = np.add(bot, y[i])
        plt.legend(
            self.dates[date].get_meal_names(), bbox_to_anchor=(1.02, 1)
        )  # Position legend to the top-right of plot
        # Threshold line
        plt.axhline(y=100, color="r")
        # Labels
        plt.xlabel("Metric")
        plt.ylabel("Percentage")
        plt.title("Goals for " + str(date))

        # Convert graph to image
        buffer = io.BytesIO()
        fig = plt.gcf()
        fig.savefig(buffer, bbox_inches="tight")
        buffer.seek(0)
        img = Image.open(buffer)
        plt.close()  # Prevents colours changing if graph is redrawn
        return img
