# %%
import tkinter as tk
from tkinter import ttk
import customtkinter
from PIL import Image, ImageTk
import openpyxl
import xlstools
import pandas as pd

from backend import raw_importer

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
        self.geometry(f"{1500}x{900}")
        self.resizable(False, False)

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
        self.patient_labels = ['HC',
                               'Apellido',
                               'Nombres',
                               'Documento',
                               'Fecha de nacimiento',
                               'Ciudad/País',
                               'Fecha de admisión',
                               'Obra social', 
                               'Médico derivante', 
                               'Guía utilizada']

        self.data = {}
        self.entry_widgets = []

        for i, label in enumerate(self.patient_labels):
            patient_data_label_generator(self, label, i+3)

        # -------------------- Frame donde vivira el appearance mode -----------------------

        self.appearance_frame = customtkinter.CTkFrame(self, width=300, corner_radius=0)
        self.appearance_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        self.appearance_mode_label = customtkinter.CTkLabel(self.appearance_frame, text="Apariencia", font=customtkinter.CTkFont(size=15, weight="bold"), anchor="n")
        self.appearance_mode_label.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        self.appearance_mode_optionemenu = customtkinter.CTkOptionMenu(self.appearance_frame, values=["Dark", "Light"],
                                                                       command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        self.appearance_mode_optionemenu.set("Dark")
        
        #****************************************************************************************************************

        # Frame donde viviran todas los widget de ANTECEDENTES Y PRESCRIPCION

        self.presc_frame = customtkinter.CTkFrame(self, corner_radius=0)
        self.presc_frame.grid(row=1, column=2, columnspan=3, padx=10, pady=10, sticky="new")
        self.presc_frame.columnconfigure(0, weight=1)
        self.presc_frame.columnconfigure(1, weight=1)

        # Titulo antecedentes
        self.background_label = customtkinter.CTkLabel(self.presc_frame, text='Antecedentes Clínicos', font=customtkinter.CTkFont(size=20, weight="bold"))
        self.background_label.grid(row=0, column=0, columnspan=3, padx=10, pady=10, sticky="n")

        # Entrada para escribir breve oracion resumiendo los antecedentes
        self.background_entry = PlaceholderTextbox(master=self.presc_frame, 
                                                   placeholder="Describir aquí los antecedentes clínicos del paciente.", 
                                                   wrap="word", 
                                                   height=100, 
                                                   font=customtkinter.CTkFont(size=14),
                                                   fg_color="#1C1C1C",  # Example fg_color
                                                   text_color="darkgray")
        self.background_entry.grid(row=1, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")
        self.entry_widgets.append(self.background_entry)

        
        # ----------------------------------------- FRAME DE PRESCRIPCION ------------------------------------------------

        self.presc_label = customtkinter.CTkLabel(master=self.presc_frame, text='Prescripción de Dosis', font=customtkinter.CTkFont(size=20, weight="bold"))
        self.presc_label.grid(row=2, column=0, columnspan=3, padx=10, pady=10)
        self.presc_frame.grid_columnconfigure(0, weight=1)
        self.presc_frame.grid_columnconfigure(1, weight=1)
        self.presc_frame.grid_columnconfigure(2, weight=10)

        # Entrada para escribir breve oracion resumiendo el tratamiento
        self.plan_entry = customtkinter.CTkEntry(master=self.presc_frame, placeholder_text="Describir aquí brevemente el esquema de tratamiento")
        self.plan_entry.grid(row=3, column=0, columnspan=3, padx=10, pady=(10, 10), sticky="nsew")

        # Eleccion de la tecnica de tratamiento
        self.technique_options = ['3D','IMRT', 'VMAT', 'SBRT', 'SRS', 'A definir según planificación']
        
        self.technique_menu, self.chosen_technique = self._create_dropdown_menu(self.presc_frame,"Técnica de Tratamiento", self.technique_options, row=4, column=0)
        self.technique = self.chosen_technique.get()

        # Eleccion de la intención del tto
        self.intention_options = ['Adyuvante', 'Neoadyuvante', 'Radical', 'Paliativo']

        self.intention_menu, self.chosen_intention = self._create_dropdown_menu(self.presc_frame,"Intención del tratamiento", self.intention_options, row=5, column=0)
        self.intention = self.chosen_intention.get()

        # -------------------------------------------------

        # Eleccion del template de prescripcion
        self.presc_templates = xlstools.get_cell_content(file_path=self.contraints_excel_filepath, cell_coordinate='B2', sheet_name=None)[3:]

        self.presc_menu, self.chosen_presc_template = self._create_dropdown_menu(self.presc_frame, 
                                                                                 'Template de Prescripción', 
                                                                                 self.presc_templates, 
                                                                                 row=6, 
                                                                                 column=0, 
                                                                                 callback=self.update_presc_template)
        self.presc_template = self.chosen_presc_template.get()
        
        # Eleccion del template de protocolo de imagenes de CC
        self.images_templates = self.get_images_template()

        self.images_menu, self.chosen_images_template = self._create_dropdown_menu(self.presc_frame, 
                                                                                   'Protocolo de Imágenes', 
                                                                                   self.images_templates, 
                                                                                   row=7, 
                                                                                   column=0, 
                                                                                   callback=self.update_images_template
        )
        self.images_template = self.chosen_images_template.get()

        # ---------------------------------------- Boton Preview de template ---------------------------------------

        self.pv_button = customtkinter.CTkButton(master=self.presc_frame, text='Previsualizar Prescripcion', border_width=3,
                                                   text_color=("gray10", "#DCE4EE"), command=self.preview)
        self.pv_button.grid(row=6, column=2, columnspan=1, padx=20, pady=10, sticky='W')

        # ---------------------------------------- Frame de Observaciones ---------------------------------------

        padx_observaciones = 5
        pady_observaciones = 5

        # Frame de Observaciones
        self.options_frame = customtkinter.CTkFrame(master=self.presc_frame)
        self.options_frame.grid(row=8, column=0, columnspan=4, padx=10, pady=10, sticky="nsew")
        # Configurar el peso de las columnas del options_frame para que se expanda
        self.options_frame.columnconfigure(0, weight=1)
        self.options_frame.columnconfigure(1, weight=1)
        self.options_frame.columnconfigure(2, weight=1)
        self.options_frame.columnconfigure(3, weight=1)
        self.options_frame.columnconfigure(4, weight=1)

        #Entry de observaciones
        self.obs_label = customtkinter.CTkLabel(master=self.options_frame, text='Observaciones', font=customtkinter.CTkFont(size=12), anchor="w")
        self.obs_label.grid(row=0, column=0, padx=padx_observaciones, pady=2*pady_observaciones)
        self.obs_entry = customtkinter.CTkEntry(master=self.options_frame, placeholder_text="Escriba aquí")
        self.obs_entry.grid(row=0, column=1, columnspan=2, padx=2*padx_observaciones, pady=2*pady_observaciones, sticky="ew")

        #Checkboxes de tratamiento previo
        self.prevous_treat_checkbox = customtkinter.CTkCheckBox(master=self.options_frame, text="RT Previa")
        self.prevous_treat_checkbox.grid(row=0, column=3, columnspan=1, padx=padx_observaciones, pady=pady_observaciones, sticky="w")

        #Checkbox de dias Alternos
        self.alternate_days_checkbox = customtkinter.CTkCheckBox(master=self.options_frame, text="Dias Alternos")
        self.alternate_days_checkbox.grid(row=0, column=4, columnspan=1, padx=padx_observaciones, pady=pady_observaciones, sticky="w")

        #Bolus
        self.bolus_label = customtkinter.CTkLabel(master=self.options_frame, text='Bolus', font=customtkinter.CTkFont(size=12), anchor="w")
        self.bolus_label.grid(row=1, column=0, padx=padx_observaciones, pady=2*pady_observaciones)

        self.bolus_options = ['Sin Bolus', 'Con Bolus', 'Mitad Con/Mitad Sin']
        self.bolus_var = tk.IntVar(value=0)
        for i, option in enumerate(self.bolus_options):
            self.radio_button = customtkinter.CTkRadioButton(master=self.options_frame, text=option, value=i, variable=self.bolus_var)
            self.radio_button.grid(row=1, column=i+1, padx=padx_observaciones, pady=pady_observaciones, sticky="w")

        #Alertas
        self.alerts_label = customtkinter.CTkLabel(master=self.options_frame, text='Alertas', font=customtkinter.CTkFont(size=12), anchor="w")
        self.alerts_label.grid(row=2, column=0, padx=padx_observaciones, pady=2*pady_observaciones)

        self.alerts_options = ['Hipoacusia', 
                               'Enf. infecciosa', 
                               'Discap. Motora',
                               'Patol. psiq./cognitiva', 
                               'Marcapasos', 
                               'Reirradiación misma zona'
                               ]
        
        self.checkbox_list = []
        for i, option in enumerate(self.alerts_options):
            checkbox = customtkinter.CTkCheckBox(master=self.options_frame, text=option)
            checkbox.grid(row=2, column=i+1, padx=padx_observaciones, pady=pady_observaciones, sticky="w") 
            self.checkbox_list.append(checkbox)

        # ---------------------------------------- Boton Generar Prescripcion ---------------------------------------

        self.button_frame = customtkinter.CTkFrame(self, corner_radius=0)
        self.button_frame.grid(row=2, column=1, columnspan=4, padx=20, pady=10, sticky="ew")

        self.main_button = customtkinter.CTkButton(self.button_frame, 
                                                     text='Generar Prescripción',
                                                     border_width=3,
                                                     text_color=("gray10", "#DCE4EE"), 
                                                     command=self.get_entries)
        self.main_button.grid(row=0, column=1, columnspan=2, padx=20, pady=10, sticky='ew')

        # ****************************************************************************************************************


    def change_appearance_mode_event(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)

    def quit(self):
        for key,value in self.data.items(): print(f'{key}: {value}')
        
    def get_entries(self):
        self.entry_widgets.append(self.plan_entry)
        self.entry_widgets.append(self.chosen_technique)
        self.entry_widgets.append(self.chosen_intention)
        self.entry_widgets.append(self.chosen_presc_template)
        self.entry_widgets.append(self.chosen_images_template)
        
        self.entry_widgets.append(self.obs_entry)
        self.entry_widgets.append(self.prevous_treat_checkbox)
        self.entry_widgets.append(self.alternate_days_checkbox)
        self.entry_widgets.append(self.bolus_var)
        for check_box in enumerate(self.checkbox_list):
            self.entry_widgets.append(check_box[1])

        entries = [entry.get() if not isinstance(entry, customtkinter.CTkTextbox) else entry.get("1.0",'end-1c') for entry in self.entry_widgets]

        self.patient_labels = self.patient_labels + ['Conclusiones', 
                                                     'Plan de Tratamiento', 
                                                     'Técnica', 
                                                     'Intención', 
                                                     'Prescripción', 
                                                     'Protocolo de Imágenes', 
                                                     'Nota de Observaciones', 
                                                     'Tratamiento Previo',
                                                     'Dias Alternos', 
                                                     'Bolus'] + self.alerts_options
                                                     
        self.data = dict(zip(self.patient_labels, entries))
        
        for key,value in self.data.items():
            print(f'{key:30}{value}')

        # with open('data.json', 'w') as f:
        #     json.dump(self.data, f)

        self.destroy()

    def get_images_template(self):
        images_template = xlstools.cell_data_importer(
            openpyxl.load_workbook(self.contraints_excel_filepath, read_only=True)['General'],
            (3,'E'), 
            (21,'E')
        )
        images_template = [item for sublist in images_template for item in sublist if item != 'None']
        return images_template

    def update_presc_template(self, new_template):
        self.presc_template = new_template
        print(f"Updated presc_template to: {self.presc_template}")
        self.update_images_menu()
        self.update_presc_data()

    def update_images_menu(self):
        new_images_template = self.get_images_template_based_on_presc_template(self.presc_template)
        self.images_menu.set(new_images_template)
        self.chosen_images_template.set(new_images_template)
        self.images_template = new_images_template
        print(f"Updated images_template to: {self.images_template}")

    def update_images_template(self, new_template):
        self.images_template = new_template
        print(f"Updated images_template to: {self.images_template}")

    def update_presc_data(self):
        actual_presc_data, _ = raw_importer(self.contraints_excel_filepath, self.presc_template)
        actual_presc_data = actual_presc_data[:, :3]
        self.actual_presc_data_df = pd.DataFrame(actual_presc_data[1:], columns=actual_presc_data[0])

    def get_images_template_based_on_presc_template(self, presc_template):
        if not hasattr(self, 'default_images_dict'):
            keys = self.presc_templates
            values = xlstools.get_cell_content(file_path=self.contraints_excel_filepath, cell_coordinate='G5', sheet_name=None)[3:]
            try:
                if len(keys) != len(values):
                    raise ValueError("The length of keys and values lists must be equal.")
                self.default_images_dict = dict(zip(keys, values))
            except ValueError as e:
                print(f"Error: {e}")

        return self.default_images_dict[presc_template]

    def preview(self):
        self.presc_template = self.chosen_presc_template.get()
        self.update_presc_data()  # se actualiza self.actual_presc_data

        self.preview_window = customtkinter.CTkToplevel(self)
        self.preview_window.title("Dosis prescripta del Template seleccionado")
        self.preview_window.geometry("600x400")
        self.preview_window.transient(self)
        self.preview_window.grab_set()
        self.preview_window.lift()
        self.preview_window.focus_force()

        self.preview_label = customtkinter.CTkLabel(self.preview_window, font=customtkinter.CTkFont(size=25, weight="bold"), text="Dosis Prescriptas:")
        self.preview_label.grid(row=0, column=0, padx=20, pady=20, sticky=tk.W)

        # Crear un Frame para el Treeview
        self.pv_frame = customtkinter.CTkFrame(self.preview_window, width=560)
        self.pv_frame.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")

        # Configurar el frame para expandirse correctamente
        self.preview_window.grid_rowconfigure(1, weight=1)
        self.preview_window.grid_columnconfigure(0, weight=1)

        # Crear un Treeview dentro del Frame de customtkinter
        columns = list(self.actual_presc_data_df.columns)
        self.tree = ttk.Treeview(self.pv_frame, columns=columns, show='headings')
        self.tree.grid(row=0, column=0, sticky='nsew')

        # Configurar las columnas
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, anchor='center')  # Establece un ancho fijo para las columnas

        # Insertar los datos del DataFrame en el Treeview
        for index, row in self.actual_presc_data_df.iterrows():
            self.tree.insert("", "end", values=list(row))



    def _create_dropdown_menu(self, frame, text, options, row, column, width=250, padx=20, pady=10, sticky=tk.W, callback=None):
        dropdown_label = customtkinter.CTkLabel(master=frame, text=text, anchor="w")
        dropdown_label.grid(row=row, column=column, padx=padx, pady=pady, sticky=sticky)

        chosen_option = tk.StringVar(value=options[0])

        dropdown_menu = customtkinter.CTkOptionMenu(
            master=frame, values=options, variable=chosen_option, anchor="w",
            command=lambda value: self.update_option(value, callback)
        )
        dropdown_menu.grid(row=row, column=column+1, padx=padx, pady=pady, sticky=sticky)
        dropdown_menu.configure(width=width)

        return dropdown_menu, chosen_option

    def update_option(self, value, callback):
        print(f"Saved option: {value}")
        if callback:
            callback(value)

def find_associated_value(search_list, value_list, search_string):
    if len(search_list) != len(value_list):
        raise ValueError("The two lists must be of equal length")
    
    try:
        index = search_list.index(search_string)
        return value_list[index]
    except ValueError:
        return None  # or you could raise an exception if you prefer
