# Imports and settings
from nutrition_app import NutritionApp
from nutrition_gui import NutritionGUI

# Run
app = NutritionApp()
gui = NutritionGUI(app)
gui.run()
