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
class PlaceholderTextbox(customtkinter.CTkTextbox):
    def __init__(self, master=None, placeholder="PLACEHOLDER", **kwargs):
        super().__init__(master, **kwargs)
        
        self.placeholder = placeholder
        self.default_text_color = self.cget("text_color")
        
        self.insert("1.0", self.placeholder)
        self.configure(text_color=self.default_text_color)
        self.bind("<FocusIn>", self.foc_in)
        self.bind("<FocusOut>", self.foc_out)
        self.bind("<Key>", self.key_press)
        
        self.has_placeholder = True

    def foc_in(self, *args):
        if self.has_placeholder:
            self.delete("1.0", "end")
            self.configure(text_color=self.default_text_color)

    def foc_out(self, *args):
        if not self.get("1.0", "end").strip():
            self.insert("1.0", self.placeholder)
            self.configure(text_color=self.default_text_color)
            self.has_placeholder = True

    def key_press(self, *args):
        if self.has_placeholder and self.get("1.0", "end").strip() == self.placeholder:
            self.delete("1.0", "end")
            self.configure(text_color=self.default_text_color)
            self.has_placeholder = False

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
            self.label.grid(row=row_number, column=0, padx=(20,10), pady=10)
            self.entry = customtkinter.CTkEntry(self.sidebar_frame, placeholder_text="Escriba aquí")
            self.entry.grid(row=row_number, column=1, padx=20, pady=10, sticky="nsew")
            self.entry_widgets.append(self.entry)


        #****************************************************************************************************************

        #VENTANA PRINCIPAL
            
        # configure window
        self.title("PreScript")
        self.geometry(f"{1400}x{950}")
        self.resizable(False, False)

        # tool_bar(self)

        # configure grid layout (4x4)
        
        self.grid_columnconfigure((2,3,4), weight=1, uniform="column")
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=8)
        self.grid_rowconfigure(4, weight=6)

        #****************************************************************************************************************

        # -------------------- Frame donde vivira el logo y el titulo -----------------------

        self.title_frame = customtkinter.CTkFrame(self, width=1400, corner_radius=0)
        self.title_frame.grid(row=0, column=0, columnspan=5, padx=20, pady=20, sticky="ew")

        # Logo intecnus
        pil_image = Image.open(self.icon_path)
        tk_image = ImageTk.PhotoImage(pil_image, master=self)  # PIL Image to Tkinter PhotoImage
        self.canvas = tk.Canvas(self.title_frame, width=270, height=100, bg='black') # Add the image to the Canvas widget
        self.canvas.create_image(0, 0, anchor=tk.NW, image=tk_image, tags='image_tag') # Keep a reference to the image to avoid garbage collection
        self.canvas.image = tk_image
        self.canvas.grid(row=0, column=0, rowspan=1, columnspan=1, padx=(10, 10), pady=(10, 10)) # Configure the Canvas grid to control position

        # Titulo
        self.titulo_label = customtkinter.CTkLabel(self.title_frame, text="Prescripción de Radioterapia", font=customtkinter.CTkFont(size=40, weight="bold"))
        self.titulo_label.grid(row=0, column=1, columnspan=4, padx=(30, 10), pady=(10, 10), sticky="ew")

        # ---------------- Sidebar donde viviran los datos del paciente -------------------- 

        self.sidebar_frame = customtkinter.CTkFrame(self, width=300, corner_radius=0)
        self.sidebar_frame.grid(row=1, column=0, padx=20, pady=(0,20), sticky="ew")

        self.datos_label = customtkinter.CTkLabel(self.sidebar_frame, text="Datos del paciente", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.datos_label.grid(row=0, column=0, columnspan=2, padx=20, pady=20, sticky="ew")

        # Entradas para los datos del paciente
        self.patient_labels = ['HC','Apellido','Nombres','Documento','Fecha de Admisión','Fecha de Nacimiento','Ciudad/País','Obra Social', 'Médico Derivante', 'Guía utilizada']

        self.data = {}
        self.entry_widgets = []

        for i, label in enumerate(self.patient_labels):
            patient_data_label_generator(self, label, i+3)

        # -------------------- Frame donde vivira el appearance mode -----------------------

        self.appearance_frame = customtkinter.CTkFrame(self, width=300, corner_radius=0)
        self.appearance_frame.grid(row=2, column=0, columnspan=2, padx=20, pady=(0, 20), sticky="ew")

        self.appearance_mode_label = customtkinter.CTkLabel(self.appearance_frame, text="Apariencia", font=customtkinter.CTkFont(size=15, weight="bold"), anchor="n")
        self.appearance_mode_label.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        self.appearance_mode_optionemenu = customtkinter.CTkOptionMenu(self.appearance_frame, values=["Dark", "Light"],
                                                                       command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(row=0, column=1, padx=20, pady=20, sticky="ew")

        self.appearance_mode_optionemenu.set("Dark")
        
        #****************************************************************************************************************

        # Frame donde viviran todas los widget de ANTECEDENTES Y PRESCRIPCION

        self.presc_frame = customtkinter.CTkFrame(self, corner_radius=0)
        self.presc_frame.grid(row=1, column=2, columnspan=3, padx=(10,20), pady=(0, 20), sticky="new")
        self.presc_frame.grid_columnconfigure(0, weight=1)
        self.presc_frame.grid_rowconfigure(0, weight=1)
        self.presc_frame.grid_rowconfigure(1, weight=2)

        # Titulo antecedentes
        self.background_label = customtkinter.CTkLabel(self.presc_frame, text='Antecedentes Clínicos', font=customtkinter.CTkFont(size=20, weight="bold"))
        self.background_label.grid(row=0, column=0, columnspan=3, padx=20, pady=20, sticky="n")

        # Entrada para escribir breve oracion resumiendo los antecedentes
        self.background_entry = PlaceholderTextbox(master=self.presc_frame, 
                                                   placeholder="Describir aquí los antecedentes clínicos del paciente.", 
                                                   wrap="word", 
                                                   height=100, 
                                                   font=customtkinter.CTkFont(size=14),
                                                   fg_color="#1C1C1C",  # Example fg_color
                                                   text_color="darkgray")
        self.background_entry.grid(row=1, column=0, columnspan=3, padx=20, pady=(10, 20), sticky="nsew")

        
        # ----------------------------------------- PRESCRIPCION ------------------------------------------------

        self.presc_label = customtkinter.CTkLabel(master=self.presc_frame, text='Prescripción de Dosis', font=customtkinter.CTkFont(size=20, weight="bold"))
        self.presc_label.grid(row=2, column=0, columnspan=3, padx=20, pady=20)
        self.presc_frame.grid_columnconfigure(0, weight=1)
        self.presc_frame.grid_columnconfigure(1, weight=1)
        self.presc_frame.grid_columnconfigure(2, weight=10)

        # Entrada para escribir breve oracion resumiendo el tratamiento
        self.plan_entry = customtkinter.CTkEntry(master=self.presc_frame, placeholder_text="Describir aquí brevemente el esquema de tratamiento")
        self.plan_entry.grid(row=3, column=0, columnspan=3, padx=20, pady=(10, 20), sticky="nsew")
        self.entry_widgets.append(self.plan_entry)

        option_menu_width = 250

        # Eleccion de la tecnica de tratamiento
        self.technique_label = customtkinter.CTkLabel(master=self.presc_frame, text="Técnica", anchor="w")
        self.technique_label.grid(row=4, column=0, padx=20, pady=10, sticky=tk.W)

        techniques = ['3D','IMRT', 'VMAT', 'SBRT', 'SRS']
        
        self.technique_optionemenu = customtkinter.CTkOptionMenu(self.presc_frame, values=techniques, anchor="w")
        self.technique_optionemenu.grid(row=4, column=1, padx=20, pady=10, sticky=tk.W)
        self.technique_optionemenu.configure(width=option_menu_width)
        self.entry_widgets.append(self.technique_optionemenu)

        # Eleccion de la intención del tto
        self.intention_label = customtkinter.CTkLabel(master=self.presc_frame, text="Intención del tratamiento", anchor="w")
        self.intention_label.grid(row=5, column=0, padx=20, pady=10, sticky=tk.W)

        intention_options = ['Adyuvante', 'Neoadyuvante', 'Radical', 'Paliativo']

        self.intention_optionemenu = customtkinter.CTkOptionMenu(master=self.presc_frame, values=intention_options, anchor="w")
        self.intention_optionemenu.grid(row=5, column=1, padx=20, pady=10, sticky=tk.W)
        self.intention_optionemenu.configure(width=option_menu_width)
        self.entry_widgets.append(self.intention_optionemenu)

        # Eleccion del template de prescripcion
        self.presc_template_label = customtkinter.CTkLabel(master=self.presc_frame, text="Template de Prescripción", anchor="w")
        self.presc_template_label.grid(row=6, column=0, padx=20, pady=10, sticky=tk.W)

        presc_template = xlstools.get_cell_content(file_path=self.contraints_excel_filepath, 
                                      cell_coordinate='B2', 
                                      sheet_name=None)[2:]

        self.presc_template_optionemenu = customtkinter.CTkOptionMenu(master=self.presc_frame, values=presc_template, anchor="w")
        self.presc_template_optionemenu.grid(row=6, column=1, padx=20, pady=10, sticky=tk.W)
        self.presc_template_optionemenu.configure(width=option_menu_width)
        self.entry_widgets.append(self.presc_template_optionemenu)

        # Eleccion del template de protocolo de imagenes de CC
        self.imagenes_template_label = customtkinter.CTkLabel(master=self.presc_frame, text="Protocolo de Imágenes de CC", anchor="w")
        self.imagenes_template_label.grid(row=7, column=0, padx=20, pady=10, sticky=tk.W)

        imagenes_template = xlstools.cell_data_importer(openpyxl.load_workbook(self.contraints_excel_filepath, read_only=True)['General'],
                                               (3,'E'), 
                                               (21,'E'))
        imagenes_template = [item for sublist in imagenes_template for item in sublist]
        imagenes_template = [item for item in imagenes_template if item !='None']


        chosen_presc_template = self.presc_template_optionemenu.get()
        default = xlstools.cell_data_importer(openpyxl.load_workbook(self.contraints_excel_filepath, read_only=True)[chosen_presc_template],
                                               (5,'G'), 
                                               (5,'G'))[0][0]
        
        self.default_template = tk.StringVar(value = default)

        self.imagenes_template_optionemenu = customtkinter.CTkOptionMenu(master=self.presc_frame, 
                                                                         variable=self.default_template,
                                                                         values=imagenes_template, 
                                                                         anchor='w')
        self.imagenes_template_optionemenu.grid(row=7, column=1, padx=20, pady=10, sticky=tk.W)
        self.imagenes_template_optionemenu.configure(width=option_menu_width)
        self.entry_widgets.append(self.imagenes_template_optionemenu)

        #                        poner opcion de bolus de bolus, tto previo, alarmas
        #                        NO SE ACTUALIZA EL PROTOCOLO POR DEFAULT SI CAMBIO EL TEMPLATE, DEBERIA CAMBIAR. ARREGLAR

        # Boton Preview de template

        self.main_button = customtkinter.CTkButton(master=self.presc_frame, 
                                                     text='Previsualizar Prescripcion',
                                                     border_width=3,
                                                     text_color=("gray10", "#DCE4EE"), 
                                                     #command=self.get_entries
                                                     )
        self.main_button.grid(row=8, column=0, columnspan=3, padx=20, pady=20)

        


        # Entrada para escribir breve oracion resumiendo el tratamiento
        self.plan_entry = customtkinter.CTkEntry(master=self.presc_frame, placeholder_text="Describir aquí brevemente el esquema de tratamiento")
        self.plan_entry.grid(row=3, column=0, columnspan=3, padx=20, pady=(10, 20), sticky="nsew")
        self.entry_widgets.append(self.plan_entry)



        #****************************************************************************************************************

        # Boton Generar Prescripcion]]

        self.button_frame = customtkinter.CTkFrame(self, width=300, corner_radius=0)
        self.button_frame.grid(row=2, column=1, columnspan=3, padx=20, pady=20, sticky="ew")

        self.main_button = customtkinter.CTkButton(self.button_frame, 
                                                     text='Generar Prescripción',
                                                     border_width=3,
                                                     text_color=("gray10", "#DCE4EE"), 
                                                     command=self.get_entries)
        self.main_button.grid(row=2, column=1, padx=20, pady=20, sticky="n")



        # self.appearance_frame = customtkinter.CTkFrame(self, width=300, corner_radius=0)
        # self.appearance_frame.grid(row=2, column=0, columnspan=2, padx=20, pady=(0, 20), sticky="ew")

        # self.appearance_mode_label = customtkinter.CTkLabel(self.appearance_frame, text="Apariencia", font=customtkinter.CTkFont(size=15, weight="bold"), anchor="n")
        # self.appearance_mode_label.grid(row=0, column=0, padx=20, pady=20, sticky="ew")




        # #****************************************************************************************************************

        

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

    def preview_window(self):
        preview_window = customtkinter.CTkToplevel(self)
        preview_window.title("Dosis prescriptas del Template seleccionado")
        preview_window.geometry("600x400")
        preview_label = customtkinter.CTkLabel(preview_window, text="Dosis Prescriptas")
        preview_label.grid(row=0, column=0, padx=20, pady=20)

        self.label = customtkinter.CTkLabel(self.sidebar_frame, text='', font=customtkinter.CTkFont(size=15, weight="bold"))
        self.label.grid(row=row_number, column=0, padx=0, pady=(10, 10))
        self.entry = customtkinter.CTkEntry(self.sidebar_frame, placeholder_text="Escriba aquí")
        self.entry.grid(row=row_number, column=1, columnspan=3, padx=(10, 10), pady=(10, 10), sticky="nsew")
        self.entry_widgets.append(self.entry)







