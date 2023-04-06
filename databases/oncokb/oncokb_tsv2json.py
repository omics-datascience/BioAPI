#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Descripcion: 
#	Anota el archivo oncokb_biomarker_drug_associations.tsv con los niveles de evidencia de OncoKB
#   y lo reformatea de TSV a un Json importable en MongoDB 
# -_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_

import csv
import argparse

class C:
	pass

# La siguiente evidencia fue obtenida desde el sitio oficiald e OncoKB: https://www.oncokb.org/levels
EVIDENCE = {
      # OncoKB Therapeutic Levels of Evidence
      "1": {
		        "clasification": "Therapeutic",
		        "description": "FDA-recognized biomarker predictive of response to an FDA-approved drug in this indication",
      },
      "2": {
		        "clasification": "Therapeutic",
		        "description": "Standard care biomarker recommended by the NCCN or other professional guidelines predictive of response to an FDA-approved drug in this indication",
      },
      "3A": {
		        "clasification": "Therapeutic",
		        "description": "Compelling clinical evidence supports the biomarker as being predictive of response to a drug in this indication",
      },
      "3B": {
		        "clasification": "Therapeutic",
		        "description": "Standard care or investigational biomarker predictive of response to an FDA-approved or investigational drug in another indication",
      },
      "4": {
		        "clasification": "Therapeutic",
		        "description": "Compelling biological evidence supports the biomarker as being predictive of response to a drug",
      },
      "R1": {
		        "clasification": "Therapeutic",
		        "description": "Standard care biomarker predictive of resistance to an FDA-approved drug in this indication",
      },
      "R2": {
		        "clasification": "Therapeutic",
		        "description": "Compelling clinical evidence supports the biomarker as being predictive of resistance to a drug",
      },
      # OncoKB Diagnostic Levels of Evidence
      "Dx1": {
		        "clasification": "Diagnostic",
		        "description": "FDA and/or professional guideline-recognized biomarker required for diagnosis in this indication",
      },
      "Dx2": {
		        "clasification": "Diagnostic",
		        "description": "FDA and/or professional guideline-recognized biomarker that supports diagnosis in this indication",
      },
      "Dx3": {
		        "clasification": "Diagnostic",
		        "description": "Biomarker that may assist disease diagnosis in this indication based on clinical evidence",
      },
      # OncoKB Prognostic Levels of Evidence
      "Px1": {
		        "clasification": "Prognostic",
		        "description": "FDA and/or professional guideline-recognized biomarker prognostic in this indication based on a well-powered study (or studies)",
      },
      "Px2": {
		        "clasification": "Prognostic",
		        "description": "FDA and/or professional guideline-recognized biomarker prognostic in this indication based on a single or multiple small studies",
      },
      "Px3": {
		        "clasification": "Prognostic",
		        "description": "Biomarker is prognostic in this indication based on clinical evidence in well-powered studies",
      }      
}

c = C()
parser = argparse.ArgumentParser(description='Procesa la base de datos de genes accionables de OncoKB. Genera un nuevo archivo en Formato Json importable en MongoDB.')
parser.add_argument('--input', help='archivo tsv correspondiente a la base de datos de genes accionables de OncoKB', required=True)
parser.add_argument('--output', help='Nombre del archivo Json de salida', required=False, default="oncokb_output.json")

args = parser.parse_args(namespace=c)

#Defino funciones
def get_level_of_evidence(evidence: str): # Obtiene el nivel de evidencia nivel 2 desde OncoKB
    result = None
    if evidence in EVIDENCE:
        result = EVIDENCE[evidence]
        result["level"] = evidence
    
    return result

if __name__ == '__main__':
    archivo = c.input
    archivo_salida = c.output
    tsvfile = open(archivo)
    contenido = csv.reader(tsvfile, dialect='excel', delimiter='\t')
    cont_json = []
    print("Procesando archivo...")
    headers = next(contenido) 
    # Level	Gene	Alterations	Cancer Types	Drugs (for therapeutic implications only)
    # Cambio nombres en el header:
    headers[headers.index('Drugs (for therapeutic implications only)')] = 'Drugs'
    headers[headers.index('Cancer Types')] = 'Cancer_Types'
    headers[headers.index('Level')] = 'OncoKB_Level_of_Evidence'

    for registro in contenido:
        json_file = {}
        for i in range(0, len(headers)):
            if headers[i] == 'OncoKB_Level_of_Evidence':
                le = get_level_of_evidence(registro[i])
                if le != None:
                    json_file[headers[i]] = le
            else: 
                if registro[i] != "":
                    json_file[headers[i]] = registro[i]
        cont_json.append(json_file)
        
    jsonfile = open(archivo_salida, "w")
    jsonfile.write(str(cont_json).replace("'", "\""))
    jsonfile.close()
    print("Finalizado!")