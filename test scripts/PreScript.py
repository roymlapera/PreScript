import frontend
import backend
from unidecode import unidecode
import sys
import os

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller 
    https://stackoverflow.com/questions/31836104/pyinstaller-and-onefile-how-to-include-an-image-in-the-exe-file"""

    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
        #base_path = sys._MEIPASS2
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# --------------------------------------------------------------------------------------------

institution_contact = {'website': 'http://intecnus.org.ar/',
                           'email': 'contacto@intecnus.org.ar',
                           'address': 'Ruta Provincial 82 s/n-CP 8400-S.C. de Bariloche, Río Negro, Argentina',
                           'phone': 'TE: +54294 4461090'}

path = os.path.abspath('').replace('\\', '/')

header_path = resource_path(path+'/images/'+'CALIDAD.png')

logo_path = resource_path(path+'/images/'+'logo.png')

watermark_path = resource_path(path+'/images/'+'marca_agua.png')

contraints_excel_filepath = resource_path(path+'/protocols/'+'Protocolo de constraints.xlsx')

save_path = '//FS-201-Radioterapia.intecnus.org.ar/medicos/PRESCRIPCION/'

# save_path = '//FS-201-Radioterapia.intecnus.org.ar/fisicos/8 - Físicos Médicos/Roy/PreScript/'

# --------------------------------------------------------------------------------------------

app = frontend.App(contraints_excel_filepath, logo_path)

app.mainloop()

patient_data_dict, prescription_dict, targets_chart, constraints_chart = backend.prescription_importer(app.data, contraints_excel_filepath)

patient_ID = [value for key,value in patient_data_dict if key=='HC'][0]
patient_name = [value for key,value in patient_data_dict if key=='Nombres'][0]
patient_surname = [value for key,value in patient_data_dict if key=='Apellido'][0]
patient_presc = prescription_dict['Prescripción']

patient_name_noaccent = unidecode(patient_name).upper()
patient_surname_noaccent = unidecode(patient_surname).upper()
patient_presc_noaccent = unidecode(patient_presc)

pdfname = save_path+f'{patient_ID}_{patient_surname_noaccent}_{patient_name_noaccent}_({patient_presc_noaccent}).pdf'

backend.generate_print_pdf(pdfname, institution_contact, header_path, watermark_path, contraints_excel_filepath, patient_data_dict, prescription_dict, targets_chart, constraints_chart)

# --------------------------------------------------------------------------------------------

#Abro la prescripcion nueva para visualizar

# backend.open_pdf_with_chrome(pdfname)

