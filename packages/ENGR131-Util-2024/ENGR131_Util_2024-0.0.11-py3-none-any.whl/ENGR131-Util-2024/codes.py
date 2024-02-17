import ipywidgets as widgets
from IPython.display import display
from IPython.display import clear_output
from ipywidgets import Output
import drexel_jupyter_logger
import json

# Predefined key
key = "7mPZKa3gJZn4ng0WJ5TsUmuQC2RK9XBAwTzrTEjbyB0="

def assign_dict_to_vars(input_dict):
   for key, value in input_dict.items():
      globals()[key] = value

def get_string_from_encrypted_string(binary):
   string = binary.decode()
   return drexel_jupyter_logger.decrypt_outputs(string)
   
   
def upsert_to_json_file(file_path, new_data):
   try:
      # Read the existing data
      with open(file_path, 'r') as file:
         data = json.load(file)
   except (FileNotFoundError, json.JSONDecodeError):
      # If file does not exist or is empty, start with an empty dictionary
      data = {}

   # Update the dictionary with new data
   data.update(new_data)

   # Write the updated dictionary back to the file
   with open(file_path, 'w') as file:
      json.dump(data, file, indent=4)


def load_json_to_dict(file_path):
   try:
      with open(file_path, 'r') as file:
         data = json.load(file)
      return data
   except (FileNotFoundError, json.JSONDecodeError):
      # Return an empty dictionary if the file doesn't exist or is not valid JSON
      return {}


# Global variable in the module
responses = load_json_to_dict('.responses.json')

class StudentInfoForm:

   def __init__(self, **kwargs):
      
      self.printed_output = Output()
      
      # Using kwargs.get() to retrieve the values, providing default values if not found in kwargs
      first_name_default = kwargs.get('first_name', "Person")
      last_name_default = kwargs.get('last_name', "Doe")
      drexel_id_default = kwargs.get('drexel_id', "pad123")
      drexel_email_default = kwargs.get('drexel_email', "pad123@drexel.edu")

      self.first_name_widget = widgets.Text(description="First Name:", value=first_name_default)
      self.last_name_widget = widgets.Text(description="Last Name:", value=last_name_default)
      self.drexel_id_widget = widgets.Text(description="Drexel ID:", value=drexel_id_default)
      self.drexel_email_widget = widgets.Text(description="Drexel Email:", value=drexel_email_default)
      self.submit_button = widgets.Button(description="Submit")

      self.submit_button.on_click(self.on_submit_clicked)
      display(self.first_name_widget, self.last_name_widget, self.drexel_id_widget, self.drexel_email_widget, self.submit_button, self.printed_output)

   def on_submit_clicked(self, b):
      self.printed_output.clear_output()
      
      # Gets the values from the widgets
      responses["first_name"] = self.first_name_widget.value
      responses["last_name"] = self.last_name_widget.value
      responses["drexel_id"] = self.drexel_id_widget.value
      responses["drexel_email"] = self.drexel_email_widget.value
      
      # Function to extract local part of the email
      def get_local_part(email):
         return email.split('@')[0]

      # Extracting local part of the Drexel email
      local_part_email = get_local_part(responses["drexel_email"])
      
      
      
      with self.printed_output:
         
         # Asserting that the local part of the email is the same as the Drexel ID
         assert local_part_email == responses["drexel_id"] , f'The DrexelID extracted from the email {local_part_email} does not match the Drexel ID {responses["drexel_id"] }.'
         
         print(f'''Data Saved.
               First Name: {responses["first_name"]}
               Last Name: {responses["last_name"]}
               Drexel ID: {responses["drexel_id"]}
               Drexel Email: {responses["drexel_email"]}''')
      
      # saves the values to variables for logging
      first_name = responses["first_name"]
      last_name = responses["last_name"]
      drexel_id = responses["drexel_id"]
      drexel_email = responses["drexel_email"]
      assignment = "Midterm_2024"
      drexel_jupyter_logger.variable_logger_csv(assignment, "info")
      drexel_jupyter_logger.variable_logger_csv(first_name, "info")
      drexel_jupyter_logger.variable_logger_csv(last_name, "info")
      drexel_jupyter_logger.variable_logger_csv(drexel_id, "info")
      drexel_jupyter_logger.variable_logger_csv(drexel_email, "info")
      
      upsert_to_json_file(".responses.json", responses)
      


class DataTypes:

   def __init__(self, **kwargs):
      self.printed_output = Output()
      
      # Using kwargs.get() to retrieve the values, providing default values if not found in kwargs
      self.types1 = kwargs.get('types1', "None")
      self.types2 = kwargs.get('types2', "None")
      self.types3 = kwargs.get('types3', "None")
      self.types4 = kwargs.get('types4', "None")
   
      types_ = [self.types1, self.types2, self.types3, self.types4]
         
      # Dropdown options
      options = ['None','list', 'function', 'dictionary', 'array', 'variable', 'integer']

      # Descriptions for each index
      descriptions = [
         "a whole number on the real number line",  # index 0
         "a collection containing key:value pairs",  # index 1
         "a mutable collection of multiple ordered items that can be heterogeneous",  # index 2
         "a defined set of operations that is callable"  # index 3
      ]

      # Set a standard width for description widgets
      description_width = '350px'

      # Create HTML widgets for descriptions with a standard width and left-justified text
      description_widgets = [widgets.HTML(value=f"<div style='text-align: left; width: {description_width};'><b>{i+1}. {desc}</b></div>") 
                        for i, desc in enumerate(descriptions)]
      
      # Create dropdown widgets
      self.dropdowns = [widgets.Dropdown(options=options, value=type_, layout=widgets.Layout(width='300px')) 
                  for desc, type_ in zip(descriptions, types_)]


      # Create a button for submission
      self.submit_button = widgets.Button(description="Submit")
      
      # Link the button to the function
      self.submit_button.on_click(self.on_submit_button_clicked)
      
      # Display the widgets using HBox for alignment
      for desc_widget, dropdown in zip(description_widgets, self.dropdowns):
         display(widgets.HBox([desc_widget, dropdown]))

      display(self.submit_button, self.printed_output)
      
   

   def on_submit_button_clicked(self, b):
      self.printed_output.clear_output()
      
      selected_values = [dropdown.value for dropdown in self.dropdowns]
      
      solutions = [b'gAAAAABlso8WfMq3eXPGdTXbbMz67HfJTEpASclIlQgDZcfsRGiLofiJP4uxYchUjZOw3DWlFYGk-i8AakTc6rwEvV0TxWWU0Q==',
                  b'gAAAAABlso8WAMKd9AdF2661BOuVmwbPE-nHeIocVbifnXwmiYBtEVIg8mNu7ePBP_n2L4bSBcDrClouZDc79vlNVQ5HodRULg==',
                  b'gAAAAABlso8WW0IRmPGo0RNLvCQufY5PfiA8Hi01wwz821djyHC0fv8NKZQMCPrjq4Vhp6dP1PocHPDTB4uewT6mZPlR7r25GQ==',
                  b'gAAAAABlso8W4JlSbvszyHDUiElwCTKOvI2q213a-HSNyBK15Hlqg3z_fk907nNzjehqyJng_gTTcXyUf5CEKVxK2KInnS-Gyw==']
      
      with self.printed_output:
         print("Data Saved")
         
         for i, value in enumerate(selected_values):
            exec(f'responses["types{i+1}"] = value')
            
            if value == 'None':
               print(f"Please select an option for question {i+1}.")
            else:
               print(f"Question {i+1}: {value}")
            
            exec(f"types{i+1} = value")
            
            if value == get_string_from_encrypted_string(solutions[i]):
               exec(f'drexel_jupyter_logger.variable_logger_csv("2, 2", "Types_{i+1}")')
            else:
               exec(f'drexel_jupyter_logger.variable_logger_csv("0, 2", "Types_{i+1}")')
      
      upsert_to_json_file(".responses.json", responses)

class LogicalOperators:

   def __init__(self, **kwargs):
      self.printed_output = Output()
      
      # Using kwargs.get() to retrieve the values, providing default values if not found in kwargs
      self.logical1 = kwargs.get('logical1', "None")
      self.logical2 = kwargs.get('logical2', "")
      self.logical3 = kwargs.get('logical3', "None")
   
      logical_ = [self.logical1, self.logical2, self.logical3]
         
      # Dropdown options
      options = ["None","+", "-", "*", "/", "%", "**", "//", "and", "or", "not", "is",  
            "==","!=","<","<=", ">", "a", "b","c"]
      
      
      ####### Question 1 #######
      
      # Title widget
      title1 = widgets.HTML(
         value="""<div style='text-align: left;'>
                  <b>1.</b>Complete the logical statement with the provided options such that the result is <code>True</code>:
                  </div>
         <code>
         a = 9 <br>
         b = '9'
         </code>
                  """,
         layout=widgets.Layout(justify_content='center')
      )


      # Text widgets for left and right descriptions
      left_text1 = widgets.HTML(value="<code>a</code>")
      right_text1 = widgets.HTML(value="<code>b</code>")

      # Central widget (e.g., a button)
      self.logical_widget1 = widgets.Dropdown(options=options, layout=widgets.Layout(width='60px'))

      # Horizontal before the central widget and side texts
      hbox_layout1 = widgets.HBox([left_text1, self.logical_widget1, right_text1])

      # Vertical stack the title above the horizontal layout
      vbox_layout1 = widgets.VBox([title1, hbox_layout1])
      
      
      ####### Question 2 #######
      
      title2 = widgets.HTML(
   value="""
   <div style='text-align: left; font-family: Arial;'>
      <div style='font-size: 16px; margin-bottom: 10px;'>
         <b>2.</b> Complete the logical statement such that the result is <code>True</code>:
      </div>
      <div style='font-size: 14px; color: #555; margin-bottom: 15px;'>
         <strong>Note:</strong> Entry should only be a string if it is required for the statement.<br>
         <strong>Note:</strong> The line of code should appear exactly how it would be seen in Python.
      </div>
         c = 56<br>
         d = '567'
   </div>
   """,
   layout=widgets.Layout(justify_content='center')
)
      
      left_text2 = widgets.HTML(value='<code>f"{c}" == d</code>')

      # Central widget (e.g., a button)
      self.logical_widget2 = widgets.widgets.Text(value = self.logical2, layout=widgets.Layout(width='60px'))

      # Horizontal before the central widget and side texts
      hbox_layout2 = widgets.HBox([left_text2, self.logical_widget2])

      # Vertical stack the title above the horizontal layout
      vbox_layout2 = widgets.VBox([title2, hbox_layout2])
      
      ####### Question 3 #######
      
      # Dropdown options
      options3 = ["None","+", "-", "*", "/", "%", "**", "//", "and", "or", "not", "is", "is not",  
            "==","<="]
      
      # Title widget
      title3 = widgets.HTML(
         value="""<div style='text-align: left;'>
                  <b>3.</b>Complete the logical statement with the provided options such that the result is <code>False</code>:
                  </div>
         <code>
         e = [9] <br>
         </code>
                  """,
         layout=widgets.Layout(justify_content='center')
      )


      # Text widgets for left and right descriptions
      left_text3 = widgets.HTML(value="<code>e</code>")
      right_text3 = widgets.HTML(value="<code>e.copy()</code>")

      # Central widget (e.g., a button)
      self.logical_widget3 = widgets.Dropdown(options=options3, layout=widgets.Layout(width='60px'))

      # Horizontal before the central widget and side texts
      hbox_layout3 = widgets.HBox([left_text3, self.logical_widget3, right_text3])

      # Vertical stack the title above the horizontal layout
      vbox_layout3 = widgets.VBox([title3, hbox_layout3])
      

      display(vbox_layout1, vbox_layout2, vbox_layout3)
      
      
      # Create a button for submission
      self.submit_button = widgets.Button(description="Submit")
      
      # Link the button to the function
      self.submit_button.on_click(self.on_submit_button_clicked)
      
      display(self.submit_button,self.printed_output)
      
   

   def on_submit_button_clicked(self, b):
      self.printed_output.clear_output()
      
      selected_values = [self.logical_widget1.value, self.logical_widget2.value, self.logical_widget3.value]
      
      solutions =[b'gAAAAABlsuslW0ZnuGH0n7eLlOOyPVt-jnXzA2Zuq9v7bl9sV-FGeWVcY1EIcF-bNry9ecMCL_g6aE66PSrQ4SwYyWpw5B_IdQ==',
               b'gAAAAABlsuslaIV1dS6lSQCPpicYUAZDjZ0DgzP_vHhWUpspr5tc0XBONFRVaj_uQZsuvtgsE26mbwzaKDD4A8XZ-EqLVmNgOw==',
               b'gAAAAABlsuslytydWOJmUQ5rgocnkHV8QgL9PGHGBZ9u8uCqH1hhTv3pDkCEL1x3YcdoML9EIYX6F7I85c8Fd_zOiB6H2rBisQ==']
                     
      with self.printed_output:
         print("Data Saved")
         
         for i, value in enumerate(selected_values):
            exec(f'responses["logical{i+1}"] = value')
            
            if value == 'None' or value == '':
               print(f"Please select an option for question {i+1}.")
            else:
               print(f"Question {i+1}: {value}")
            
            exec(f"logical{i+1} = value")
            
            if value == get_string_from_encrypted_string(solutions[i]):
               exec(f'drexel_jupyter_logger.variable_logger_csv("3, 3", "logical_{i+1}")')
            else:
               exec(f'drexel_jupyter_logger.variable_logger_csv("0, 3", "logical_{i+1}")')
      
      upsert_to_json_file(".responses.json", responses)   

   