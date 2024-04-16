# %%
import tkinter as tk
from tkinter import ttk
import customtkinter
from PIL import Image, ImageTk
import openpyxl
import numpy as np
import xlstools

import json

customtkinter.set_appearance_mode("dark")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

# %%
class App(customtkinter.CTk):
    def __init__(self, contraints_excel_filepath, icon_path):
        super().__init__()

        self.icon_path = icon_path
        self.contraints_excel_filepath = contraints_excel_filepath
        self.data = {}  #Diccionario para guardar los datos ingresados por el medico

        def tool_bar(self):
            def open_setup_window():
                setup_window = customtkinter.CTkToplevel(self)
                setup_window.title("Configuración")
                setup_window.geometry("600x400")
                setup_label = customtkinter.CTkLabel(setup_window, text="Datos de Configuración")
                setup_label.grid(row=0, column=0, padx=20, pady=20)

                self.label = customtkinter.CTkLabel(self.sidebar_frame, text='', font=customtkinter.CTkFont(size=15, weight="bold"))
                self.label.grid(row=row_number, column=0, padx=0, pady=(10, 10))
                self.entry = customtkinter.CTkEntry(self.sidebar_frame, placeholder_text="Escriba aquí")
                self.entry.grid(row=row_number, column=1, columnspan=3, padx=(10, 10), pady=(10, 10), sticky="nsew")
                self.entry_widgets.append(self.entry)

            def open_miscellaneous_window():
                misc_window = customtkinter.CTkToplevel(self)
                misc_window.title("Acerca de..")
                misc_window.geometry("300x200")
                misc_label = customtkinter.CTkLabel(misc_window, text="PreScript v1.0")
                misc_label.grid(row=0, column=0, padx=20, pady=20)

            def menu_selected(event):
                selected_menu = menu_combobox.get()
                if selected_menu == "Configuración":
                    open_setup_window()
                elif selected_menu == "PreScript Version":
                    open_miscellaneous_window()

            # Create a menu
            menu = tk.Menu(self)

            # Create a submenu for "Setup" and "Miscellaneous"
            submenu = tk.Menu(menu, tearoff=0)
            submenu.add_command(label="Setup", command=open_setup_window)
            submenu.add_command(label="Miscellaneous", command=open_miscellaneous_window)

            # Add the submenu to the main menu
            menu.add_cascade(label="Menu", menu=submenu)

            # Configure the menu
            self.config(menu=menu)


        def patient_data_label_generator(self, title: str, row_number: int) -> None:
            self.label = customtkinter.CTkLabel(self.sidebar_frame, text=title, font=customtkinter.CTkFont(size=15, weight="bold"))
            self.label.grid(row=row_number, column=0, padx=0, pady=(10, 10))
            self.entry = customtkinter.CTkEntry(self.sidebar_frame, placeholder_text="Escriba aquí")
            self.entry.grid(row=row_number, column=1, columnspan=3, padx=(10, 10), pady=(10, 10), sticky="nsew")
            self.entry_widgets.append(self.entry)


        #****************************************************************************************************************

        #VENTANA PRINCIPAL
            
        # configure window
        self.title("PreScript")
        self.geometry(f"{1400}x{950}")
        self.resizable(False, False)

        tool_bar(self)

        # configure grid layout (4x4)
        self.grid_columnconfigure((2,3,4), weight=1, uniform="column")
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=8)
        self.grid_rowconfigure(4, weight=6)

        #****************************************************************************************************************

        # Sidebar donde viviran los datos del paciente
        self.sidebar_frame = customtkinter.CTkFrame(self, width=150, corner_radius=0)
        self.sidebar_frame.grid(row=1, column=0, rowspan=4, padx=10, pady=(20, 30), sticky="nsew")


        # Logo intecnus
        # Open the image with PIL
        pil_image = Image.open(self.icon_path)

        # Convert PIL Image to Tkinter PhotoImage
        tk_image = ImageTk.PhotoImage(pil_image, master=self)

        # Add the image to the Canvas widget
        self.canvas = tk.Canvas(self.sidebar_frame, width=270, height=100, bg='black')
        self.canvas.create_image(0, 0, anchor=tk.NW, image=tk_image, tags='image_tag')

        # Keep a reference to the image to avoid garbage collection
        self.canvas.image = tk_image

        # Configure the Canvas grid to control position
        self.canvas.grid(row=0, column=0, rowspan=1, columnspan=4)


        # Titulo  
        self.titulo_label = customtkinter.CTkLabel(self.sidebar_frame, text="Prescripción de Radioterapia", font=customtkinter.CTkFont(size=30, weight="bold"))
        self.titulo_label.grid(row=1, column=0, columnspan=4, padx=10, pady=(20, 10))

        self.datos_label = customtkinter.CTkLabel(self.sidebar_frame, text="Datos del paciente", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.datos_label.grid(row=2, column=0, columnspan=4, padx=20, pady=(20, 10))

        # Entradas para los datos del paciente
        self.patient_labels = ['HC','Apellido','Nombres','Documento','Fecha de Admisión','Fecha de Nacimiento','Ciudad/País','Obra Social', 'Médico Derivante','Estadificación', 'Performance', 'Guía utilizada']

        self.data = {}
        self.entry_widgets = []

        for i, label in enumerate(self.patient_labels):
            patient_data_label_generator(self, label, i+3)

        self.appearance_mode_label = customtkinter.CTkLabel(self.sidebar_frame, text="Apariencia", font=customtkinter.CTkFont(size=15, weight="bold"), anchor="s")
        self.appearance_mode_label.grid(row=len(self.patient_labels)+5, column=0, padx=20, pady=10, sticky="s")
        self.appearance_mode_optionemenu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["Dark", "Light"],
                                                                       command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(row=len(self.patient_labels)+5, column=1, columnspan=4, padx=20, pady=10, sticky="s")
        
        #****************************************************************************************************************

        # Entrada de texto para incluir el resumen del paciente
        self.text_label = customtkinter.CTkLabel(self, text='Conclusiones', font=customtkinter.CTkFont(size=20, weight="bold"))
        self.text_label.grid(row=1, column=1, columnspan=4, padx=(20, 20), pady=(20, 20), sticky="n")

        self.textbox = customtkinter.CTkTextbox(self, height=300, width=1110)
        self.textbox.grid(row=2, column=1, columnspan=4, padx=(10, 10), pady=(10, 10), sticky="n")

        self.entry_widgets.append(self.textbox)
        
        #****************************************************************************************************************

        # Frame donde viviran todas los widget de precripcion
        self.tabview = customtkinter.CTkFrame(self)
        self.tabview.grid(row=3, column=1, columnspan=4, padx=(10, 10), pady=(0, 0), sticky="nsew")
        self.tabview.grid_rowconfigure((0,1,2,3,4), weight=1)
        self.tabview.grid_columnconfigure(0, weight=3, uniform="column")
        self.tabview.grid_columnconfigure(1, weight=2, uniform="column")

        self.presc_label = customtkinter.CTkLabel(master=self.tabview, text='Prescripción de Dosis', font=customtkinter.CTkFont(size=20, weight="bold"))
        self.presc_label.grid(row=0, column=0, columnspan=4, padx=(0, 0), pady=(10, 0))

        # Entrada para escribir breve oracion resumiendo el tratamiento
        self.plan_entry = customtkinter.CTkEntry(master=self.tabview, placeholder_text="Describir aquí brevemente el esquema de tratamiento")
        self.plan_entry.grid(row=1, column=0, columnspan=2, padx=(20, 0), pady=(10, 10), sticky="nsew")
        self.entry_widgets.append(self.plan_entry)

        # Eleccion de la tecnica de tratamiento
        self.technique_label = customtkinter.CTkLabel(master=self.tabview, text="Técnica", anchor="w")
        self.technique_label.grid(row=1, column=2, padx=20, pady=(10, 10), sticky=tk.W)

        techniques = ['2D','3D','IMRT', 'VMAT', 'SBRT', 'SRS']
        
        self.technique_optionemenu = customtkinter.CTkOptionMenu(self.tabview, values=techniques)
        self.technique_optionemenu.grid(row=1, column=3, padx=20, pady=(10, 10), sticky=tk.W)
        self.entry_widgets.append(self.technique_optionemenu)

        # Eleccion de la intención del tto
        self.intention_label = customtkinter.CTkLabel(master=self.tabview, text="Intención del tratamiento", anchor="n")
        self.intention_label.grid(row=3, column=0, padx=20, pady=(10, 10), sticky=tk.N)

        intention_options = ['Curativa', 'Paliativa']

        self.intention_optionemenu = customtkinter.CTkOptionMenu(master=self.tabview, values=intention_options, anchor="w")
        self.intention_optionemenu.grid(row=3, column=1, padx=20, pady=(10, 10), sticky=tk.W)
        self.entry_widgets.append(self.intention_optionemenu)

        # Eleccion del template de prescripcion
        self.presc_template_label = customtkinter.CTkLabel(master=self.tabview, text="Template de Prescripción", anchor="n")
        self.presc_template_label.grid(row=4, column=0, padx=20, pady=(10, 10), sticky=tk.N)

        presc_template = xlstools.get_cell_content(file_path=self.contraints_excel_filepath, 
                                      cell_coordinate='B2', 
                                      sheet_name=None)[2:]

        self.presc_template_optionemenu = customtkinter.CTkOptionMenu(master=self.tabview, values=presc_template, anchor="w")
        self.presc_template_optionemenu.grid(row=4, column=1, padx=20, pady=(10, 10), sticky=tk.W)
        self.entry_widgets.append(self.presc_template_optionemenu)

        # Eleccion del template de protocolo de imagenes de CC
        self.imagenes_template_label = customtkinter.CTkLabel(master=self.tabview, text="Protocolo de Imágenes de CC", anchor="n")
        self.imagenes_template_label.grid(row=5, column=0, padx=20, pady=(10, 10), sticky=tk.N)

        imagenes_template = xlstools.cell_data_importer(openpyxl.load_workbook(self.contraints_excel_filepath, read_only=True)['General'],
                                               (2,'D'), 
                                               (20,'D'))
        imagenes_template = [item for sublist in imagenes_template for item in sublist ]
        imagenes_template = [item for item in imagenes_template if item !='None']
        


        self.imagenes_template_optionemenu = customtkinter.CTkOptionMenu(master=self.tabview, 
                                                                         values=imagenes_template, 
                                                                         anchor='w')
        self.imagenes_template_optionemenu.grid(row=5, column=1, padx=20, pady=(10, 10), sticky=tk.W)
        self.entry_widgets.append(self.imagenes_template_optionemenu)



        #****************************************************************************************************************

        # Boton Generar Prescripcion
        self.main_button_1 = customtkinter.CTkButton(master=self, 
                                                     text='Generar Prescripción',
                                                     border_width=3,
                                                     text_color=("gray10", "#DCE4EE"), 
                                                     command=self.get_entries)
        self.main_button_1.grid(row=4, column=1, columnspan=4, padx=(20, 20), pady=(20, 20), sticky="ew")

        #****************************************************************************************************************

        self.appearance_mode_optionemenu.set("Dark")

    def change_appearance_mode_event(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)

    def quit(self):
        for key,value in self.data.items(): print(f'{key}: {value}')

    def get_entries(self):
        # Function to retrieve values from entry widgets
        entries = [entry.get() if not isinstance(entry, type(self.textbox)) else entry.get("1.0",'end-1c') for entry in self.entry_widgets ]

        self.patient_labels = self.patient_labels + ['Conclusiones', 'Plan de Tratamiento', 'Técnica', 'Intención', 'Prescripción', 'Protocolo de Imágenes']
        self.data = dict(zip(self.patient_labels, entries))
        
        # for key,value in self.data.items():
        #     print(f'{key:30}{value}')

        # with open('my_dict.json', 'w') as f:
        #     json.dump(self.data, f)

        self.destroy()







