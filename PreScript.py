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

def filename_creator(save_path ,patient_data_dict, prescription_dict):
    patient_ID = patient_data_dict['HC']
    patient_name = patient_data_dict['Nombres']
    patient_surname = patient_data_dict['Apellido']
    patient_presc = prescription_dict['Prescripción']

    patient_name_noaccent = unidecode(patient_name).upper()
    patient_surname_noaccent = unidecode(patient_surname).upper()
    patient_presc_noaccent = unidecode(patient_presc)

    pdfname = save_path+f'{patient_ID}_{patient_surname_noaccent}_{patient_name_noaccent}_({patient_presc_noaccent}).pdf'
    return pdfname

def main():
    # --------------------------------------------------------------------------------------------

    DEVELOP_MODE = True
    FRONTEND_QA_MODE = False
    BACKEND_QA_MODE = False

    # --------------------------------------------------------------------------------------------

    if DEVELOP_MODE:
        # Carga nuevamente las librerias para que la actualizacion del codigo se refleje al ejecutar el notebook 
        import importlib
        importlib.reload(frontend)
        importlib.reload(backend)

        # Cambia direccion de guardado para no tener limitaciones de permisos de dominio en carpeta medicos
        save_path = '//FS-201-Radioterapia.intecnus.org.ar/fisicos/8 - Físicos Médicos/Roy/INTECNUS-PreScript/'
    else:
        save_path = '//FS-201-Radioterapia.intecnus.org.ar/medicos/PRESCRIPCION/'

    # --------------------------------------------------------------------------------------------


    institution_contact = {'website': 'http://intecnus.org.ar/',
                            'email': 'contacto@intecnus.org.ar',
                            'address': 'Ruta Provincial 82 s/n-CP 8400-S.C. de Bariloche, Río Negro, Argentina',
                            'phone': 'TE: +54294 4461090'}

    path = os.path.abspath('').replace('\\', '/')
    images_path = path + '/images/'

    header_path = resource_path(images_path + 'CALIDAD.png')

    logo_path = resource_path(images_path + 'logo.png')

    watermark_path = resource_path(images_path + 'marca_agua.png')

    # Reemplazar con path a Excel de contraints actualizado
    contraints_excel_filepath = resource_path('//FS-201-Radioterapia.intecnus.org.ar/fisicos/8 - Físicos Médicos/Natalia Espector/2024 - Protocolos clínicos/Protocolo de Constraints.xlsx')

    # --------------------------------------------------------------------------------------------

    if BACKEND_QA_MODE:
        import xlstools, json

        with open("data.json", "r") as archivo:
            data_dict = json.load(archivo)

        presc_templates = xlstools.get_cell_content(file_path=contraints_excel_filepath, cell_coordinate='B2', sheet_name=None)[3:]

        for template in presc_templates:
            data_dict['Prescripción'] = template
            print(template)
            patient_data_dict, prescription_dict, targets_chart, constraints_chart = backend.prescription_importer(data_dict, contraints_excel_filepath)
            pdfname = filename_creator(save_path ,patient_data_dict, prescription_dict)
            backend.generate_print_pdf(pdfname, institution_contact, header_path, watermark_path, contraints_excel_filepath, patient_data_dict, prescription_dict, targets_chart, constraints_chart)

    else:
        app = frontend.App(contraints_excel_filepath, logo_path)
        app.mainloop()
        data_dict = app.data

        if FRONTEND_QA_MODE: 
            return
        else:
            patient_data_dict, prescription_dict, targets_chart, constraints_chart = backend.prescription_importer(data_dict, contraints_excel_filepath)
            pdfname = filename_creator(save_path ,patient_data_dict, prescription_dict)

            backend.generate_print_pdf(pdfname, institution_contact, header_path, watermark_path, contraints_excel_filepath, patient_data_dict, prescription_dict, targets_chart, constraints_chart)

        #Abro la prescripcion nueva para visualizar
        if DEVELOP_MODE:
            backend.open_pdf_with_vscode(pdfname)
        else:
            return
            # backend.open_pdf_with_chrome(pdfname)

###################################################################################################

if __name__ == '__main__':
    main()