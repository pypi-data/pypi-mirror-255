from tkinter import *
from tkinter import ttk
from tkinter.filedialog import askopenfile 
from tkinter import Canvas
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg



def open_new_window(gui):
     
    newWindow = Toplevel(gui)
 
    # sets the title of the
    # Toplevel widget
    newWindow.title("New Window")
    newWindow.geometry("500x500")
 
    # canvas = Canvas(newWindow)
    # canvas.create_rectangle(30, 10, 120, 80,
        # outline="#fb0", fill="#fb0")
    # canvas.create_rectangle(150, 10, 240, 80,
        # outline="#f50", fill="#f50")
    # canvas.create_rectangle(270, 10, 370, 80,
        # outline="#05f", fill="#05f")
    # canvas.pack(fill=BOTH, expand=1)

    figure2 = plt.Figure(figsize=(5, 4), dpi=100)
    ax2 = figure2.add_subplot(111)
    line2 = FigureCanvasTkAgg(figure2, newWindow)
    line2.get_tk_widget().pack(side=LEFT, fill=BOTH)

    # plt.scatter( 0 , 0 , s = 7000 )
    # plt.title( 'Circle' )
    
    # plt.xlim( -0.85 , 0.85 )
    # plt.ylim( -0.95 , 0.95 )
    
    # plt.title( "Scatter plot of points Circle" )
    # plt.show(newWindow)


def open_file(gui=None):
    file_path = askopenfile(mode='r', filetypes=[('Graph Json File', '*json')])
    if file_path is not None:
        pass

def create_gui():
    gui = Tk()
    gui.title("Plan Generated Test.")
    gui.geometry("400x300")

    return gui

def create_text_field(gui, row, label):
    label_text = Label(gui, text=label, anchor='w')
    label_text.grid(row=row, column=0)

    current_var = StringVar()

    entry = Entry(gui, textvariable=current_var)
    entry.grid(row=row, column=1, sticky='W')

    return current_var

def create_combo_box(gui, row, label, list):

    label_text = Label(gui, text=label, anchor='w')
    label_text.grid(row=row, column=0)

    current_var = StringVar()

    combobox = ttk.Combobox(gui, textvariable=current_var)
    combobox["values"] = list

    combobox.grid(row=row, column=1, sticky='W')

    return current_var

def create_button(gui, row, column, text, func=None):
    button = Button(gui, text=text, command=lambda:func(gui) if func else None)
    button.grid(row=row, column=column, pady=3)

    return button

if __name__ == '__main__':
    gui = create_gui()
    
    mir_pose_var = create_text_field(gui, 0, "MIR Pose:")
    ident_right_var = create_text_field(gui, 1, "Identified Markers Camera Right:")
    ident_left_var = create_text_field(gui, 2, "Identified Markers Camera Left:")
    activ_front_var = create_combo_box(gui, 3, "Activation Range Front:", [0, 1])
    activ_rear_var = create_combo_box(gui, 4, "Activation Range Rear:", [0, 1])
    is_battery_var = create_combo_box(gui, 5, "Is Battery Low:", [0, 1])
    robot_state_var = create_combo_box(gui, 6, "Robot State:", ['moving', 'stopped'])
    ur5_state_var = create_combo_box(gui, 7, "UR5 State:", ['moving', 'stopped'])

    transport_request_var = create_text_field(gui, 8, "Transport Requests:")    
    
    goal_intention_var = create_combo_box(gui, 9, "Goal Intention:", ['EXPLORATION', 'CHARGE', 'TRANSPORT'])
    goal_pose_var = create_text_field(gui, 10, "Goal Pose:")

    create_button(gui, 11, 0, "Check Plan", open_new_window)
    create_button(gui, 11, 1, "Load Graph File", open_file)
    create_button(gui, 12, 0, "Clear Path")

    gui.mainloop()

    