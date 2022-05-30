#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import requests

url = "http://localhost:8088/genSymbol?"
casos_test = [["HGNC:1100","BRCA1"],["HGNC:26927","FOXRED1"],["HGNC:20105","FLVCR2"],["NCRNA00181","A1BG-AS1"],["ABC3","ABCA3"],["STGD","ABCA4"],["BM-009","CYRIB"],["P450RAI-2","CYP26B1"],["HRES-1/p28","HRES1"],["29974","A1CF"],["2","A2M"],["106480683","AARS1P1"],["ENSG00000253889","IGLVI-38"],["ENSG00000221510","MIR548O"],["ENSG00000280634","THRIL"],["OTTHUMG00000169548","LINC02356"],["OTTHUMG00000004276","OSTCP2"],["OTTHUMG00000133126","TUBA4A"],["BC140924","AARD"],["U60519","CASP10"],["AK023964","PRKRIP1"],["uc004eus.4","APLN"],["uc001zwm.2","CTXN2"],["uc001jfa.2","GDF2"],["XR_940049","PRKCE-AS1"],["NG_053071","RNA5SP479"],["NM_001348364","SIGLEC16"],["RBM5-AS1","RBM5-AS1"],["TUB-AS1","TUB-AS1"],["ZNF649-AS1","ZNF649-AS1"],["CCDS73439","A2ML1"],["CCDS9766","HSPA2"],["CCDS58030","ZBTB7B"],["Q9NVM9","INTS13"],["Q96QZ0","PANX3"],["P62424","RPL7A"],["HSP90AA1","HSP90AA1"],["IDH2","IDH2"],["IKZF3","IKZF3"],["604230","ADAT1"],["618860","C1orf87"],["609619","GOLGA8B"],["MI0016796","MIR548AH"],["MI0000437","MIR1-2"],["MI0000063","MIRLET7B"],["8363","DPRXP7"],["8623","ZHX2"],["8492","PITX2"],["SR0000311","TERC"],["SR0000013","SNORD55"],["SR0000370","SNORA35"],["SLC49A2","FLVCR2"],["SLC23A4P","SLC23A4P"],["SLC25A7","UCP1"],["119066","BRAF"],["470368","GAL"],["356638","IGHV4-34"],["PGOHUM00000291221","A2MP1"],["PGOHUM00000244076","RNFT1P2"],["PGOHUM00000249345","TRMT112P7"],["OR1A2","OR1A2"],["OR52E7P","OR52E7P"],["OR56B3P","OR56B3P"],["S09.991","AADAC"],["S01.033","HABP2"],["C01.975","TINAGL1"],["IGHD1-14","IGHD1-14"],["TRAV8-1","TRAV8-1"],["TRBVA/OR9-2","TRBVAOR9-2"],["objectId:1923","ABL1"],["objectId:40","BRS3"],["ligandId:4961","IFNA21"],["15","MT-TH"],["25","MT-TW"],["18","MT-TL1"],["CD156B","ADAM17"],["CDw218b","IL18RAP"],["CD43","SPN"],["adamts9-as2","ADAMTS9-AS2"],["gata3-as1","GATA3-AS1"],["Emx2os","EMX2OS"],["2.4.1.40","ABO"],["1.14.11.-","FTO"],["3.5.1.-","OARD1"],["HGNC:6459","KRT82"],["HGNC:9461","PRPH"],["HGNC:6638","LMNB2"],["HGNC:28425","BFSP2-AS1"],["HGNC:16729","C21orf91-OT1"],["HGNC:4932","HLA-B"]]
# cada elemento de la lista es una lista de 2 elementos: el id que paso como parametro y el
# symbolo que espero recibir como respuesta
casos_ok = 0
print("CASO TEST\tVALOR ESPERADO\tVALOR OBTENIDO\tRESULTADO")
for caso in casos_test:
	response = requests.request("GET", url+"gene_id="+caso[0])
	if response.status_code == 200:
		r = response.json()
		if type(r["gene"]) == list:
			if caso[1] in r["gene"]:
				casos_ok = casos_ok + 1
				print(caso[0] + "\t" + caso[1] + "\t" + ",".join(r["gene"]) + "\tOK")
			else:
				print(caso[0] + "\t" + caso[1] + "\t" + ",".join(r["gene"]) + "\tFAIL")
		else:
			print(caso[0] + "\t" + caso[1] + "\t" + str(r["gene"]) + "\tFAIL")
	else:
		print(caso[0] + "\t" + caso[1] + "\t" + str(r["error"]) + "\tFAIL")

print("RESUMEN")
print("Total de pruebas: " + str(len(casos_test)))
print("\tpasaron el test: " + str(casos_ok) + " (" + str((casos_ok/len(casos_test)*100.0)) + "%)")