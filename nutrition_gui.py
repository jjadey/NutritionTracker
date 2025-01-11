# Imports and settings
from datetime import date
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import font
from tkcalendar import Calendar


# Nutrition App Frontend
class NutritionGUI:

    # Constructor
    def __init__(self, app):
        self.app = app
        self.root = tk.Tk()
        self.pages = self.init_elem()

    # Initialize elements
    def init_elem(self):

        # Initialize UI
        tk.Tk().withdraw()
        self.root.title("Nutrition Tracker App")
        self.root.geometry("1000x750")

        # Initialize menu
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        filemenu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=filemenu)
        filemenu.add_command(label="Exit", command=self.exit)
        navmenu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Navigate", menu=navmenu)
        navmenu.add_command(label="Settings", command=lambda: self.show_page(0))
        navmenu.add_command(label="Log Meal", command=lambda: self.show_page(1))
        navmenu.add_command(label="View Diary", command=lambda: self.show_page(2))

        # Initialize pages
        settings_page = tk.Frame(self.root)
        add_page = tk.Frame(self.root)
        view_page = tk.Frame(self.root)

        # Define fonts
        default_font = font.nametofont("TkDefaultFont")
        default_font.configure(family="Arial", size=10)
        bold_font = font.Font(self.root, family="Arial", size=10, weight="bold")
        # underline_font = font.Font(self.root, family="Arial", size=10, underline=True)

        # User information page
        api_label = tk.Label(settings_page, text="API Key:", font=bold_font)
        api_label.pack()
        api_text = tk.Text(settings_page, width=40, height=1)
        api_text.pack()
        api_button = tk.Button(
            settings_page,
            text="Verify Key",
            font=bold_font,
            command=lambda: self.set_key(
                api_text.get("1.0", "end-1c").strip(), confirmation_label
            ),
        )  # 1.0 is line 0 character 1, end-1c is the end minus the \n
        api_button.pack(pady=20)
        settings_label = tk.Label(settings_page, text="User details:", font=bold_font)
        settings_label.pack()
        sex_label = tk.Label(settings_page, text="Sex")
        sex_label.pack()
        sex_options = ["Male", "Female"]
        sex_var = tk.StringVar(settings_page, value=sex_options[0])
        sex_selector = tk.OptionMenu(settings_page, sex_var, *sex_options)
        sex_selector.pack()
        weight_scale = tk.Scale(
            settings_page,
            from_=0,
            to=250,
            orient=tk.HORIZONTAL,
            length=200,
            label="Weight (kg)",
        )
        weight_scale.pack()
        height_scale = tk.Scale(
            settings_page,
            from_=0,
            to=250,
            orient=tk.HORIZONTAL,
            length=200,
            label="Height (cm)",
        )
        height_scale.pack()
        age_scale = tk.Scale(
            settings_page,
            from_=0,
            to=100,
            orient=tk.HORIZONTAL,
            length=200,
            label="Age (years)",
        )
        age_scale.pack()
        save_button = tk.Button(
            settings_page,
            text="Save Details",
            font=bold_font,
            command=lambda: self.save(
                sex_var.get(),
                weight_scale.get(),
                height_scale.get(),
                age_scale.get(),
                confirmation_label,
            ),
        )
        save_button.pack(pady=20)
        confirmation_label = tk.Label(settings_page, fg="red")
        confirmation_label.pack()

        # Add meal page
        add_label = tk.Label(add_page, text="Add a meal:", font=bold_font)
        add_label.pack()
        instructions_label = tk.Label(
            add_page,
            text="Describe the meal using text and/or an image\n\nText Description",
        )
        instructions_label.pack()
        info_text = tk.Text(add_page, width=40, height=3)
        info_text.pack()
        upload_button = tk.Button(
            add_page,
            text="Upload Image",
            command=lambda: self.choose_image_wrapper(image_label),
        )
        upload_button.pack(pady=20)
        image_label = tk.Label(add_page, text="(No image chosen)")
        image_label.pack()
        add_button = tk.Button(
            add_page,
            text="Add Meal",
            font=bold_font,
            command=lambda: self.add(
                info_text.get("1.0", "end-1c").strip(), error_label
            ),
        )
        add_button.pack(pady=20)
        error_label = tk.Label(add_page, fg="red", justify=tk.LEFT)
        error_label.pack()

        # View diary page
        view_label = tk.Label(view_page, text="View food diary:", font=bold_font)
        view_label.pack()
        calendar_button = tk.Button(
            view_page,
            text="Choose a date",
            command=lambda: self.show_calendar(graph_label),
        )
        calendar_button.pack(pady=20)
        graph_label = tk.Label(view_page)
        graph_label.pack()

        return [settings_page, add_page, view_page]

    # Run
    def run(self):
        self.show_page(0)
        self.root.mainloop()

    # UI Methods (Commands)
    # Exit GUI
    def exit(self):
        self.root.quit()  # Found that it is more consistent using both quit and destroy methods
        self.root.destroy()

    # Show a given page
    def show_page(self, index):
        # Hide all pages
        for page in self.pages:
            page.pack_forget()
        # Show the specified page
        self.pages[index].pack()
        # Special case - reset image when loading add meal page
        if index == 1:
            self.app.img = None

    # Use user-given API key to initialize Gemini AI
    def set_key(self, api_key, confirmation_label):
        try:
            self.app.init_gem(api_key)
            self.app.verify_api = True
            confirmation_label.config(fg="green", text="Success! API key has been set")
        except:
            confirmation_label.config(text="Failure. Please check your API key")

    # Use user information to initialize target variables
    def save(self, sex, weight, height, age, confirmation_label):
        try:
            self.app.init_var(sex, weight, height, age)
            self.app.verify_user = True
            confirmation_label.config(
                fg="green",
                text="Success!\n\nYour targets:\nCalories: "
                + str(round(self.app.target_cal, 2))
                + " cal\nProtein: "
                + str(round(self.app.target_pro, 2))
                + " g\nCarbohydrates: "
                + str(round(self.app.target_carb, 2))
                + " g\nFat: "
                + str(round(self.app.target_fat, 2))
                + " g",
            )
        except:
            confirmation_label.config(
                text="Failure. Please check your inputs/measurements"
            )

    # Set image and convert it for displaying
    def choose_image_wrapper(self, image_label):
        self.app.img = self.app.choose_image()
        display_img = self.app.img.copy()
        display_img.thumbnail((100, 100), Image.LANCZOS)
        photo_img = ImageTk.PhotoImage(display_img, master=self.root)
        image_label.config(image=photo_img)
        image_label.image = photo_img  # Needed to prevent blank image

    # Add a meal to the food diary
    def add(self, information, error_label):    
        # Check that API key has been set
        if self.app.verify_api is False:
            error_label.config(text="Please set your API key first")
            return
        # Check that targets have been set
        if self.app.verify_user is False:
            error_label.config(text="Please set your user details first")
            return
        # Check that input is not blank
        information = information.strip()
        if information == "" and self.app.img is None:
            error_label.config(text="No text or image detected")
        # Ask gemini
        else:
            text = self.app.prompt_gemini(information)
            try:
                meal = self.app.parse_response(text)
                error_label.config(
                    fg="green", text="Success!\n\nYour meal:\n" + str(meal)
                )
            except:
                error_label.config(text="AI generation error. Please try again")

    # Open a pop-up window with a calendar
    def show_calendar(self, graph_label):

        # Use the calendar input to display the correct graph
        def show_graph():
            date = calendar.selection_get()
            try:
                img = self.app.graph_progress(str(date))
                photo_img = ImageTk.PhotoImage(img, master=self.root)
                graph_label.config(image=photo_img)
                graph_label.image = photo_img
                top.destroy()
            except:
                feedback_label.config(text="No stored meals for " + str(date))

        top = tk.Toplevel(self.root)
        today = date.today()
        calendar = Calendar(
            top,
            selectmode="day",
            year=int(today.strftime("%Y")),
            month=int(today.strftime("%m").lstrip("0")),
            day=int(today.strftime("%d").lstrip("0")),
        )
        calendar.pack()
        select_button = tk.Button(top, text="Select", command=show_graph)
        select_button.pack()
        feedback_label = tk.Label(top, fg="red")
        feedback_label.pack()
