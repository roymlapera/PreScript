import frontend
import backend
from unidecode import unidecode
import sys
import os
import json


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def get_app_dir():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def get_paths_json_path():
    return os.path.join(get_app_dir(), "file_paths.json")


def load_file_paths():
    json_path = get_paths_json_path()

    if not os.path.exists(json_path):
        raise FileNotFoundError(
            f"No se encontró file_paths.json en:\n{json_path}"
        )

    with open(json_path, "r", encoding="utf-8") as f:
        paths = json.load(f)

    required_keys = ["save_path", "template_excel_path"]

    for key in required_keys:
        if key not in paths:
            raise KeyError(f"Falta la clave '{key}' en file_paths.json")

    return paths


def filename_creator(save_path, patient_data_dict, prescription_dict):
    patient_ID = patient_data_dict["HC"]
    patient_name = patient_data_dict["Nombres"]
    patient_surname = patient_data_dict["Apellido"]
    patient_presc = prescription_dict["Prescripción"]

    patient_name_noaccent = unidecode(patient_name).upper()
    patient_surname_noaccent = unidecode(patient_surname).upper()
    patient_presc_noaccent = unidecode(patient_presc)

    pdfname = os.path.join(
        save_path,
        f"{patient_ID}_{patient_surname_noaccent}_{patient_name_noaccent}_({patient_presc_noaccent}).pdf"
    )

    return pdfname


def main():
    DEVELOP_MODE = False
    FRONTEND_QA_MODE = False
    BACKEND_QA_MODE = False

    if DEVELOP_MODE:
        import importlib
        importlib.reload(frontend)
        importlib.reload(backend)

    paths = load_file_paths()

    save_path = paths["save_path"]
    contraints_excel_filepath = paths["template_excel_path"]

    if not os.path.exists(save_path):
        raise FileNotFoundError(
            f"No se encontró el directorio de guardado:\n{save_path}"
        )

    if not os.path.exists(contraints_excel_filepath):
        raise FileNotFoundError(
            f"No se encontró el archivo Excel de templates:\n{contraints_excel_filepath}"
        )

    institution_contact = {
        "website": "http://intecnus.org.ar/",
        "email": "contacto@intecnus.org.ar",
        "address": "Ruta Provincial 82 s/n-CP 8400-S.C. de Bariloche, Río Negro, Argentina",
        "phone": "TE: +54294 4461090"
    }

    header_path = resource_path(os.path.join("images", "CALIDAD.png"))
    logo_path = resource_path(os.path.join("images", "logo.png"))
    watermark_path = resource_path(os.path.join("images", "marca_agua.png"))

    if BACKEND_QA_MODE:
        import xlstools

        with open("data.json", "r", encoding="utf-8") as archivo:
            data_dict = json.load(archivo)

        presc_templates = xlstools.get_cell_content(
            file_path=contraints_excel_filepath,
            cell_coordinate="B2",
            sheet_name=None
        )[3:]

        for template in presc_templates:
            data_dict["Prescripción"] = template
            print(template)

            patient_data_dict, prescription_dict, targets_chart, constraints_chart = backend.prescription_importer(
                data_dict,
                contraints_excel_filepath
            )

            pdfname = filename_creator(save_path, patient_data_dict, prescription_dict)

            backend.generate_print_pdf(
                pdfname,
                institution_contact,
                header_path,
                watermark_path,
                contraints_excel_filepath,
                patient_data_dict,
                prescription_dict,
                targets_chart,
                constraints_chart
            )

    else:
        app = frontend.App(contraints_excel_filepath, logo_path)
        app.mainloop()
        data_dict = app.data

        if FRONTEND_QA_MODE:
            return

        patient_data_dict, prescription_dict, targets_chart, constraints_chart = backend.prescription_importer(
            data_dict,
            contraints_excel_filepath
        )

        pdfname = filename_creator(save_path, patient_data_dict, prescription_dict)

        backend.generate_print_pdf(
            pdfname,
            institution_contact,
            header_path,
            watermark_path,
            contraints_excel_filepath,
            patient_data_dict,
            prescription_dict,
            targets_chart,
            constraints_chart
        )

        if DEVELOP_MODE:
            backend.open_pdf_with_vscode(pdfname)
        else:
            return


if __name__ == "__main__":
    main()