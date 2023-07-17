from tkinter import filedialog, messagebox, ttk
import plotly.graph_objects as go
from collections import Counter
from exercise import Exercise
from datetime import datetime
import tkinter as tk
import csv

class StrongAppDataVisualizer():
    def __init__(self):
        # Initialise Tkinter window
        self.root = tk.Tk()
        self.root.geometry("720x480")
        self.root.resizable(width=False, height=False)
        self.root.title("Strong App - Data Visualizer")
        self.root.iconbitmap("Daniooo.ico")
        self.root.config(background="#181d1f")

        # Variables
        self.display_mode = tk.StringVar(value="Simple")
        self.y_axis = tk.StringVar(value="Weight")
        self.exercise_sort = tk.StringVar(value="Alphabetical")
        self.vcmd = (self.root.register(self.validate_input), '%P')
        self.exercise_table = []
        self.exercises = []
        self.x_axis_backend = []
        self.y_axis_backend = []
        self.x_axis_frontend = []
        self.hover_info = []
        self.ignore_values = [] 

        # Ttk styles
        radioButtonStyle = ttk.Style()
        radioButtonStyle.configure("RadioToggleStyle.TRadiobutton", background="#181d1f", foreground="white", selectcolor="black")
        mainRadioButtonStyle = ttk.Style()
        mainRadioButtonStyle.configure("MainRadioToggleStyle.TRadiobutton", background="#2e9ffe", foreground="white", selectcolor="black")

        # Initialise Tkinter widgets
        self.csv_button = tk.Button(self.root, text="Select CSV File", command=self.choose_csv, fg="white", bg='#8534dd')
        self.csv_button.place(x=15, y=15, width=337, height=45)

        self.alphabetical_toggle = ttk.Radiobutton(self.root, text="Alphabetical", variable=self.exercise_sort, value="Alphabetical", style="RadioToggleStyle.TRadiobutton", command=self.sort_exercises)
        self.alphabetical_toggle.place(x=372, y=60)

        self.frequency_toggle = ttk.Radiobutton(self.root, text="Frequency", variable=self.exercise_sort, value="Frequency", style="RadioToggleStyle.TRadiobutton", command=self.sort_exercises)
        self.frequency_toggle.place(x=470, y=60)

        self.exercise_dropdown = ttk.Combobox(self.root, state="readonly", values=["Waiting for CSV file"], background='#2e9ffe')
        self.exercise_dropdown.current(0)
        self.exercise_dropdown.place(x=372, y=15, width=332, height=45)

        self.display_mode_text = tk.Label(self.root, text="Display Mode\n---------------\nToggle between Simple View (displays best set for each day) or Detailed View (shows every single recorded set)", wraplength=300, fg="white", bg='#181d1f')
        self.display_mode_text.place(x=15, y=95, width=332, height=100)

        self.simple_toggle = ttk.Radiobutton(self.root, text="Simple", variable=self.display_mode, value="Simple", style="MainRadioToggleStyle.TRadiobutton")
        self.simple_toggle.place(x=372, y=95, width=332, height=45)

        self.detailed_toggle = ttk.Radiobutton(self.root, text="Detailed", variable=self.display_mode, value="Detailed", style="MainRadioToggleStyle.TRadiobutton")
        self.detailed_toggle.place(x=372, y=150, width=332, height=45)

        self.y_axis_text = tk.Label(self.root, text="Data to Plot\n-------------\nToggle between plotting the weight for each set or reps performed", wraplength=300, fg="white", bg='#181d1f')
        self.y_axis_text.place(x=15, y=220, width=332, height=100)

        self.weight_toggle = ttk.Radiobutton(self.root, text="Weight", variable=self.y_axis, value="Weight", style="MainRadioToggleStyle.TRadiobutton")
        self.weight_toggle.place(x=372, y=220, width=332, height=45)

        self.reps_toggle = ttk.Radiobutton(self.root, text="Reps", variable=self.y_axis, value="Reps", style="MainRadioToggleStyle.TRadiobutton")
        self.reps_toggle.place(x=372, y=275, width=332, height=45)

        self.ignore_values_text = tk.Label(self.root, text="Weights to Ignore\n-------------------\nInput weights to be ignored when plotting the chart (seperated by spaces)", wraplength=300, fg="white", bg='#181d1f')
        self.ignore_values_text.place(x=15, y=345, width=332, height=60)

        self.ignore_input = tk.Entry(self.root, validate='key', validatecommand=self.vcmd, fg="white", bg='#2e9ffe')
        self.ignore_input.place(x=372, y=350, width=332, height=45)
        self.ignore_input.insert(0, '20')

        self.plot_button = tk.Button(self.root, text="Plot", command=self.plot_data, fg="white", bg='#29d062')
        self.plot_button.place(x=15, y=420, width=690, height=45)

    # Choose CSV file, perform data retrieval and sort exercises
    def choose_csv(self):
        file_path = filedialog.askopenfilename(
            title="Select CSV File",
            filetypes=(("CSV files", "*.csv"), ("All files", "*.*"))
        )

        if file_path != "":
            # Open CSV file
            with open(file_path, 'r') as file:
                csv_reader = csv.reader(file, delimiter=';')
                error_count = 0
                descriptorsSkipped = False
                self.exercise_table.clear()

                # Iterate CSV dataset
                for row in csv_reader:
                    # Skips descriptors and moves onto dataset
                    if descriptorsSkipped is False: 
                        descriptorsSkipped = True
                        continue

                    if len(row) >= 14:
                        # Record first exercise entry
                        if len(self.exercise_table) == 0:
                            self.exercise_table.insert(len(self.exercise_table), Exercise(row[2], row[0]))
                            self.exercise_table[-1].add_set(row[3], row[4], row[6])

                        # Append exercise data to existing entry
                        elif self.exercise_table[-1].name == row[2] and self.exercise_table[-1].date_time == row[0]:
                            self.exercise_table[-1].add_set(row[3], row[4], row[6])

                        # Record new exercise entry
                        else:
                            self.exercise_table.insert(len(self.exercise_table), Exercise(row[2], row[0]))
                            self.exercise_table[-1].add_set(row[3], row[4], row[6])

                    else:
                        error_count += 1
                        messagebox.showerror("Error", 'Error encountered during parsing. Possible cause: "" characters inside notes')
            
            self.sort_exercises()

    # Sorts collected excercises based on set preference
    def sort_exercises(self):
        self.exercises.clear()

        # Sort by alphabetical order
        if self.exercise_sort.get() == "Alphabetical" and len(self.exercise_table) != 0:
            for exercise in self.exercise_table:
                if exercise.name not in self.exercises:
                    self.exercises.append(exercise.name)
            self.exercises = sorted(self.exercises)

            # Update exercise dropdown with exercise names
            self.exercise_dropdown.config(values=self.exercises)
            self.exercise_dropdown.current(0)
        
        # Sort exercises based on frequency
        elif self.exercise_sort.get() == "Frequency" and len(self.exercise_table) != 0:
            exercise_count = Counter(exercise.name for exercise in self.exercise_table)
            sorted_exercises = sorted(exercise_count, key=exercise_count.get, reverse=True)

            # Update exercise dropdown with exercise names
            self.exercise_dropdown.config(values=sorted_exercises)
            self.exercise_dropdown.current(0)

    # Validate input for ignore list
    def validate_input(self, text):
        # Remove whitespace and split the text by commas
        numbers = text.replace(" ", "").split(",")

        for num in numbers:
            # Allow empty strings
            if not num:
                continue
            
            # Check if each part is a valid number
            if not num.replace(".", "").isdigit():
                return False
        return True
    
    # Collect all specified data and plot chart
    def plot_data(self):
        if self.exercise_dropdown.get() == "Waiting for CSV file":
            messagebox.showerror("Error", "Please select a CSV file first")
            return

        identifier = 0
        self.x_axis_backend.clear()
        self.y_axis_backend.clear()
        self.x_axis_frontend.clear()
        self.hover_info.clear()
        self.ignore_values.clear()

        ignore = self.ignore_input.get()
        self.ignore_values = ignore.split()

        for exercise in self.exercise_table:
            if exercise.name == self.exercise_dropdown.get():
                # Display best set for each exercise session
                if self.display_mode.get() == "Simple":
                    ignore = False
                    # Plot weight progression
                    if self.y_axis.get() == "Weight":
                        # Skip values to be ignored
                        for ignore_value in self.ignore_values:
                            if float(exercise.best[1]) == float(ignore_value):
                                ignore = True
                                break
                        if ignore is True:
                            continue
                        self.x_axis_backend.append(exercise.date_time) 
                        self.y_axis_backend.append(exercise.best[1])
                        self.hover_info.append(f"{exercise.best[2]} reps")
                    
                    # Plot rep progression
                    elif self.y_axis.get() == "Reps":
                        self.x_axis_backend.append(exercise.date_time) 
                        self.y_axis_backend.append(exercise.best[2])
                        self.hover_info.append(f"{exercise.best[1]} kg")

                # Display each set for each exercise session
                elif self.display_mode.get() == "Detailed":
                    for set in exercise.sets:
                        ignore = False
                        # Plot weight progression
                        if self.y_axis.get() == "Weight":
                            # Skip values to be ignored
                            for ignore_value in self.ignore_values:
                                if float(set[1]) == float(ignore_value):
                                    ignore = True
                                    break
                            if ignore is True:
                                continue
                            self.x_axis_backend.append(f"{exercise.date_time} {identifier}")
                            self.y_axis_backend.append(set[1])
                            self.hover_info.append(f"{set[2]} reps")
                            timestamp = datetime.strptime(exercise.date_time, '%Y-%m-%d %H:%M:%S')
                            clean_timestamp = timestamp.strftime('%d %B %Y')
                            self.x_axis_frontend.append(clean_timestamp)
                            identifier += 1
                        
                        # Plot rep progression
                        elif self.y_axis.get() == "Reps":
                            self.x_axis_backend.append(f"{exercise.date_time} {identifier}") 
                            self.y_axis_backend.append(set[2])
                            self.hover_info.append(f"{set[1]} kg")
                            timestamp = datetime.strptime(exercise.date_time, '%Y-%m-%d %H:%M:%S')
                            clean_timestamp = timestamp.strftime('%d %B %Y')
                            self.x_axis_frontend.append(clean_timestamp)
                            identifier += 1
        # Clean up data
        self.y_axis_backend = [float(item) for item in self.y_axis_backend]

        if self.y_axis.get() == "Weight":
            yAxisTitle = "Weight (kg)"
        else:
            yAxisTitle = "Reps"

        ignored = ""
        if len(self.ignore_values) != 0:
            ignored = f"Ignored values: "
            for i in self.ignore_values:
                ignored += f"{i} "

        # Plot settings
        scatter_trace = go.Scatter(
            x=self.x_axis_backend,
            y=self.y_axis_backend,
            mode='markers+lines',
            line=dict(width=5, color='#8534dd'),
            marker=dict(size=15, color='#8534dd'),
            text=self.hover_info,
        )

        simpleViewLayout = go.Layout(
            title=f'Strong App - Data Visualizer<br>{self.exercise_dropdown.get()} - Simple View<br>{ignored}',
            xaxis=dict(
                title="Timestamp", 
                title_font=dict(color='white'),
            ),
            yaxis=dict(
                title=yAxisTitle,
                title_font=dict(color='white'),
            ),
            plot_bgcolor='#181d1f', 
            paper_bgcolor='#181d1f',
            title_font=dict(color='white'),
            xaxis_tickfont=dict(color='white'),
            yaxis_tickfont=dict(color='white'),
        )

        detailedViewLayout = go.Layout(
            title=f'Strong App - Data Visualizer<br>{self.exercise_dropdown.get()} - Detailed View<br>{ignored}',
            xaxis=dict(
                title="Timestamp", 
                title_font=dict(color='white'),
                tickmode='array', 
                ticktext=self.x_axis_frontend, 
                tickvals=self.x_axis_backend
            ),
            yaxis=dict(
                title=yAxisTitle,
                title_font=dict(color='white'),
            ),
            plot_bgcolor='#181d1f', 
            paper_bgcolor='#181d1f',
            title_font=dict(color='white'),
            xaxis_tickfont=dict(color='white'),
            yaxis_tickfont=dict(color='white'),
        )

        # Plot and show the chart
        if self.display_mode.get() == "Simple":
            fig = go.Figure(data=[scatter_trace], layout=simpleViewLayout)
        elif self.display_mode.get() == "Detailed":
            fig = go.Figure(data=[scatter_trace], layout=detailedViewLayout)
        fig.show()

if __name__ == '__main__':
    app = StrongAppDataVisualizer()
    app.root.mainloop()