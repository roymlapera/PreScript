from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_RIGHT, TA_JUSTIFY
from reportlab.lib import utils

from itertools import product
import json
import subprocess
import platform
import xlstools
from xlstools import open_workbook
from datetime import datetime
import math
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

def open_pdf_with_vscode(pdf_path):
    # Determine the platform (Windows, macOS, or Linux)
    current_platform = platform.system()

    # Define the command to open VSCode with the PDF file
    if current_platform == "Windows":
        command = ["code.cmd", pdf_path]
    elif current_platform == "Darwin":  # macOS
        command = ["code", pdf_path]
    elif current_platform == "Linux":
        command = ["code", pdf_path]
    else:
        raise NotImplementedError("Unsupported operating system")
    # Run the command
    subprocess.run(command)

def open_pdf_with_chrome(pdf_path):
    # Determine the platform (Windows, macOS, or Linux)
    current_platform = platform.system()

    # Define the command to open Google Chrome with the PDF file
    if current_platform == "Windows":
        command = ["chrome", pdf_path]
    elif current_platform == "Darwin":  # macOS
        command = ["open", "-a", "Google Chrome", pdf_path]
    elif current_platform == "Linux":
        command = ["google-chrome", pdf_path]
    else:
        raise NotImplementedError("Unsupported operating system")

    # Run the command
    subprocess.run(command)

def set_fonts():
    font_path = os.path.dirname(os.path.abspath(__file__))+'/fonts/'

    pdfmetrics.registerFont(TTFont('CourierNewRegular', resource_path(font_path+'courier_new_regular.ttf')))
    pdfmetrics.registerFont(TTFont('CourierNewRegularBold', resource_path(font_path+'courier_new_regular-bold.ttf')))
    pdfmetrics.registerFontFamily('CourierNewRegular', normal='CourierNewRegular', bold='CourierNewRegularBold')

    pdfmetrics.registerFont(TTFont('Calibri', resource_path(font_path+'calibri.ttf')))
    pdfmetrics.registerFont(TTFont('CalibriBold', resource_path(font_path+'calibri-bold.ttf')))
    pdfmetrics.registerFontFamily('Calibri', normal='Calibri', bold='CalibriBold')

def set_styles():
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(name='Patient_data',
                            fontFamily='Calibri',
                            fontSize=9,
                            spaceBefore=0.1*inch,
                            spaceAfter=0.1*inch))

    styles.add(ParagraphStyle(name='Conclusions',
                            fontFamily='Calibri',
                            fontSize=7,
                            spaceBefore=0.1*inch,
                            spaceAfter=0.1*inch))

    styles.add(ParagraphStyle(name='PDFTitle',
                            fontName='CalibriBold',
                            fontSize=11,
                            spaceBefore=0.1*inch,
                            spaceAfter=0.1*inch))

    styles.add(ParagraphStyle(name='Constraints',
                            fontFamily='Calibri',
                            fontSize=10,
                            spaceBefore=0.1*inch,
                            spaceAfter=0.1*inch))

    styles.add(ParagraphStyle(name='comment',
                            fontFamily='Calibri',
                            fontSize=7,
                            spaceBefore=0.1*inch,
                            spaceAfter=0.1*inch))
    
    return styles

    
# %%


# Set the page height and width
HEIGHT = 11.7 * inch
WIDTH = 8.3 * inch

# Import our font
set_fonts()

# Set our styles
styles = set_styles()

# -------------------------------------------------------------------------------------------------------------------------

def format_preprocessing(targets_chart, constraints_chart):

    targets_chart = targets_chart[:,:-2]
    constraints_chart = constraints_chart[1:,1:]

    targets_chart = targets_chart.tolist()
    constraints_chart = constraints_chart.tolist()

    for i,_ in enumerate(targets_chart):
        if i:
            targets_chart[i][3] = str(int(targets_chart[i][1])//int(targets_chart[i][2]))

    reformated_constraints_chart = []
    for j,constraint_line in enumerate(constraints_chart):
        if j==0:
            reformated_constraints_chart.append([constraint_line[0],constraint_line[2],constraint_line[4]])
        if j!=0:
            aux = []
            aux.append(constraint_line[0]) if constraint_line[0]!='None' else aux.append('')
            if constraint_line[1] == 'V(D)>V_%':
                aux.append('V('+constraint_line[2]+' cGy)'+' > '+constraint_line[3]+' %')
                if constraint_line[4] != 'None': 
                    aux.append('V('+constraint_line[4]+' cGy)'+' > '+constraint_line[5]+' %')
                else:
                    aux.append('')
            elif constraint_line[1] == 'V(D)<V_%':
                aux.append('V('+constraint_line[2]+' cGy)'+' < '+constraint_line[3]+' %')
                if constraint_line[4] != 'None': 
                    aux.append('V('+constraint_line[4]+' cGy)'+' < '+constraint_line[5]+' %')
                else:
                    aux.append('')
            elif constraint_line[1] == 'V(D)<V_cc':
                aux.append('V('+constraint_line[2]+' cGy)'+' < '+constraint_line[3]+' cc')
                if constraint_line[4] != 'None': 
                    aux.append('V('+constraint_line[4]+' cGy)'+' < '+constraint_line[5]+' cc')
                else:
                    aux.append('')
            elif constraint_line[1] == 'D(V_%)<D':
                aux.append('V('+constraint_line[2]+' %)'+' < '+constraint_line[3]+' cGy')
                if constraint_line[4] != 'None': 
                    aux.append('V('+constraint_line[4]+' %)'+' < '+constraint_line[5]+' cGy')
                else:
                    aux.append('')
            elif constraint_line[1] == 'D(V_cc)<D':
                aux.append('V('+constraint_line[2]+' cc)'+' < '+constraint_line[3]+' cGy')
                if constraint_line[4] != 'None': 
                    aux.append('V('+constraint_line[4]+' cc)'+' < '+constraint_line[5]+' cGy')
                else:
                    aux.append('')
            elif constraint_line[1] == 'Dmedia':
                aux.append('Dmed < '+constraint_line[2]+' cGy')
                if constraint_line[4] != 'None': 
                    aux.append('Dmed < '+constraint_line[4]+' cGy')
                else:
                    aux.append('')
            elif constraint_line[1] == 'Dmax':
                aux.append('Dmax < '+constraint_line[2]+' cGy')
                if constraint_line[4] != 'None': 
                    aux.append('Dmax < '+constraint_line[4]+' cGy')
                else:
                    aux.append('')
            elif constraint_line[1] == 'D(V_%)>D':
                aux.append('D('+constraint_line[2]+' %)'+' > '+constraint_line[3]+' cGy')
                if constraint_line[4] != 'None': 
                    aux.append('D('+constraint_line[4]+' %)'+' > '+constraint_line[5]+' cGy')
                else:
                    aux.append('')
            elif constraint_line[1] == 'D(V_cc)>D':
                aux.append('D('+constraint_line[2]+' cc)'+' > '+constraint_line[3]+' cGy')
                if constraint_line[4] != 'None': 
                    aux.append('D('+constraint_line[4]+' cc)'+' > '+constraint_line[5]+' cGy')
                else:
                    aux.append('')
            reformated_constraints_chart.append(aux)

    constraints_chart = reformated_constraints_chart

    return targets_chart, constraints_chart  

def patient_data_splitter(story, patient_data_dict):
    # Apply styles to tables
    tbl_style = TableStyle([
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('FONT', (0, 0), (-1, -1), 'Calibri'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('LEADING', (0, 0), (-1, -1), 6)
    ])

    # Split the dictionary into two parts
    nro_lines = len(patient_data_dict)

    # Split the dictionary into two parts
    if nro_lines%2 != 0:
        patient_data_dict.append(['', ''])

    half_length = len(patient_data_dict) // 2
    
    first_part = patient_data_dict[:half_length]
    second_part = patient_data_dict[half_length:]
    
    content = []
    for (key1, value1), (key2, value2) in zip(first_part,second_part):
        content.append([key1.upper(),value1,key2.upper(),value2])

    content_table = Table(
        content,
        colWidths=[1.5 * inch, 2 * inch, 1.5 * inch, 2 * inch]
    )

    # Apply styles to the table
    content_table.setStyle(tbl_style)
    story.append(content_table)

def constraints_chart_splitter(constraints_chart):
    # Apply styles to tables
    tbl_style = TableStyle([
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('FONT', (0, 0), (-1, -1), 'Calibri'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT')
    ])

    # constraints_chart.pop()
    nro_constraint_lines = len(constraints_chart) - 1

    if nro_constraint_lines < 10:
        return constraints_chart
    else:
        # Split the dictionary into two parts
        title = constraints_chart.pop(0)

        if nro_constraint_lines%2 != 0:
            constraints_chart.append(['', '', ''])

        half_length = nro_constraint_lines // 2
        
        first_part = constraints_chart[:half_length]
        second_part = constraints_chart[half_length:]

        first_part.insert(0,title)
        second_part.insert(0,title)
        
        content = []
        for (value1, value2, value3), (value4, value5, value6) in zip(first_part,second_part):
            content.append([value1, value2, value3, value4, value5, value6])

        return content

def myPageWrapper(institution_contact, watermark_path):
    # template for static, non-flowables, on the first page
    # draws all of the contact information at the bottom of the page
    def myPage(canvas, doc):
        canvas.saveState()  # save the current state

        watermark = utils.ImageReader(watermark_path)

        # Set the position and size of the watermark
        canvas.saveState()
        canvas.rotate(0)  # Adjust the rotation angle as needed
        canvas.drawImage(watermark, 200, 20, width=6*inch, height=6*inch)
        # canvas.restoreState()
        # canvas.save()

        canvas.setFont('Calibri', 8)  # sets the font for contact

        # canvas.drawRightString(
        #     WIDTH - (.4 * inch),
        #     .4 * inch,  # draw the website at the bottom right of the page
        #     institution_contact['website'])

        canvas.setLineWidth(2)
        canvas.setStrokeColorRGB(0, 0, 0)
        canvas.line(.4 * inch, .8 * inch, 
            WIDTH - (.4 * inch), .8 * inch)  # adjust the position of the line

        canvas.drawString(
            .4 * inch,
            .6 * inch,  # draw the phone at the second line from the bottom
            institution_contact['phone'])

        canvas.drawCentredString(
            WIDTH / 2.0,
            .6 * inch,  # draw the address at the second line from the bottom
            institution_contact['address'])

        canvas.drawRightString(
            WIDTH - (.4 * inch),
            .6 * inch,  # draw the email at the second line from the bottom
            institution_contact['email'])

        # restore the state to what it was when saved
        canvas.restoreState()

    return myPage

def generate_print_pdf(pdfname, institution_contact, image_path, watermark_path, contraints_excel_filepath, patient_data_dict, prescription_dict, targets_chart, constraints_chart):
    doc = SimpleDocTemplate(
        pdfname,
        pagesize=A4,
        bottomMargin=0.1 * inch,
        topMargin=0.1 * inch,
        rightMargin=.3 * inch,
        leftMargin=.3 * inch
        )  # set the doc template

    story = []  # create a blank story to tell

    # Add the image as a header
    header_image = Image(image_path, width=WIDTH-0.8*inch, height=1.6 * inch)
    
    story.append(header_image)


    #DATOS DE PACIENTE
    disease_title = Paragraph('DATOS DEL PACIENTE', styles['PDFTitle']) 
    story.append(disease_title)

    patient_data_splitter(story, patient_data_dict)

    #LINEA TITULO ENFERMEDAD ACTUAL
    disease_title = Paragraph('ANTECEDENTES CLÍNICOS', styles['PDFTitle']) 
    story.append(disease_title)

    #CONCLUSIONES
    styles_conclusions = styles['Conclusions']
    styles_conclusions.alignment = 4
    conclusions_text = Paragraph(prescription_dict['Conclusiones'], styles['Conclusions'])
    story.append(conclusions_text)

    #LINEA TITULO PRESCRIPCION DE RADIOTERAPIA
    presc_title = Paragraph('PRESCRIPCIÓN DE RADIOTERAPIA', styles['PDFTitle']) 
    story.append(presc_title)

    tto_text1 = Paragraph(prescription_dict['Plan de Tratamiento'], styles['Conclusions'])
    story.append(tto_text1)
    tto_text2 = Paragraph('Prescripción: '+prescription_dict['Prescripci\u00f3n']+
                         '  -  Técnica: '+prescription_dict['T\u00e9cnica']+
                         '  -  Intención: '+prescription_dict['Intenci\u00f3n'], 
                         styles['Conclusions'])
    story.append(tto_text2)

    targets_chart, constraints_chart = format_preprocessing(targets_chart, constraints_chart)

    #DOSIS
    presc_title = Paragraph('PRESCRIPCIÓN DE DOSIS', styles['PDFTitle']) 
    story.append(presc_title)

    target_col_widths = 5 * [1.2*inch]
    constraints_col_widths = 6 * [1.2*inch]

    # Create a table from the data
    targets_table = Table(targets_chart, colWidths=target_col_widths)
    # Add style to the table
    grey_color = (0.8, 0.8, 0.8)  # RGB values for grey color
    style = TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), 'Calibri'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('BACKGROUND', (0, 0), (-1, 0), grey_color),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)   
            ])
    targets_table.setStyle(style)
    for i in range(0, len(targets_chart)):
        targets_table._argH[i] = 11

    story.append(targets_table)

    #CONSTRAINTS
    presc_title = Paragraph('RESTRICCIONES', styles['PDFTitle']) 
    story.append(presc_title)

    constraints_chart = constraints_chart_splitter(constraints_chart)

    # Create a table from the data
    constraints_table = Table(constraints_chart, colWidths=constraints_col_widths)

    # Add style to the table
    for i in range(0, len(constraints_chart)):
        constraints_table._argH[i] = 13

    if len(constraints_chart[0])>3:
        grey_color = (0.8, 0.8, 0.8)  # RGB values for grey color
        style.add('BACKGROUND', (0, 0), (0, -1), grey_color)    #columna 0
        style.add('BACKGROUND', (3, 0), (3, -1), grey_color)    #columna 3

    constraints_table.setStyle(style)
    story.append(constraints_table)

    #IMAGENES
    presc_title = Paragraph('PROTOCOLO DE IMÁGENES: '+prescription_dict['Protocolo de Im\u00e1genes'], styles['PDFTitle']) 
    story.append(presc_title)

    #OBSERVACIONES
    alert_keys = ['Tratamiento Previo',
                'Dias Alternos',
                'Bolus',
                'Hipoacusia',
                'Enf. Infecciosa',
                'Discapacidad Motora',
                'Patología psiquiátrica/cognitiva']

    alert_string = ' - '.join([key for key in alert_keys if prescription_dict[key] != 0])

    if prescription_dict['Bolus'] == 0:
        alert_string.replace('Bolus','')
    if prescription_dict['Bolus'] == 1:
        alert_string.replace('Bolus','Tratamiento c/Bolus')
    elif prescription_dict['Bolus'] == 2:
        alert_string.replace('Bolus','50% Tratamiento c/Bolus')
    
    obs_title = Paragraph(f"OBSERVACIONES: {prescription_dict['Nota de Observaciones']} - {alert_string}", styles['PDFTitle']) 
    story.append(obs_title)

    doc.build(story, onFirstPage=myPageWrapper(institution_contact, watermark_path))

    return pdfname

def calculate_age(birthday):
    if birthday == '' or not isinstance(birthday, str):
        return ''
    
    accepted_formats = ["%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y"]

    for format_str in accepted_formats:
        try:
            birth_date = datetime.strptime(birthday, format_str)
            break
        except ValueError:
            continue
    else:
        raise ValueError("Invalid date format")

    today = datetime.now()
    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    return age

def raw_importer(contraints_excel_filepath, presc_template_name):
    excel_data = xlstools.cell_data_importer(open_workbook(contraints_excel_filepath, presc_template_name),
                                               (4,'A'), 
                                               (45,'G'))
    
    targets_chart, constraints_chart = xlstools.none_based_data_parser(excel_data)

    return targets_chart, constraints_chart

def prescription_importer(frontend_data, contraints_excel_filepath):
    # Datos de paciente
    #Agrego edad a la fecha de la precripcion
    frontend_data['Edad'] = str(calculate_age(frontend_data['Fecha de Nacimiento']))

    # Importacion de datos de template de prescripcion de excel de constraints
    prescription_keys = ['Conclusiones', 
                         'Plan de Tratamiento', 
                         'Intenci\u00f3n', 
                         'T\u00e9cnica',
                         'Prescripci\u00f3n',
                         'Protocolo de Im\u00e1genes',
                         'Nota de Observaciones', 
                         'Tratamiento Previo',
                         'Dias Alternos', 
                         'Bolus', 
                         'Hipoacusia', 
                         'Enf. Infecciosa', 
                         'Discapacidad Motora',
                         'Patología psiquiátrica/cognitiva' 
                         ]

    prescription_dict = {key: frontend_data.pop(key) for key in prescription_keys if key in frontend_data}

    #Separo prescription_dict de patient_data_dict
    patient_data_dict = [[key, value] for key,value in frontend_data.items()]

    targets_chart, constraints_chart = raw_importer(contraints_excel_filepath, prescription_dict['Prescripci\u00f3n'])

    return patient_data_dict, prescription_dict, targets_chart, constraints_chart
