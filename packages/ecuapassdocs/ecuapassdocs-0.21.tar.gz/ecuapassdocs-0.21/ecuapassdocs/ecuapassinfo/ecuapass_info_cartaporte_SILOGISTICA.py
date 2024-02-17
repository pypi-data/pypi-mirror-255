#!/usr/bin/env python3

import re, os, json, sys
from traceback import format_exc as traceback_format_exc
from datetime import datetime, timedelta

from .ecuapass_info_cartaporte import CartaporteInfo
from .ecuapass_extractor import Extractor
from .ecuapass_data import EcuData
from .ecuapass_utils import Utils

#----------------------------------------------------------
USAGE = "\
Extract information from document fields analized in AZURE\n\
USAGE: ecuapass_info_cartaportes.py <Json fields document>\n"
#----------------------------------------------------------
# Main
#----------------------------------------------------------
def main ():
	args = sys.argv
	fieldsJsonFile = args [1]
	runningDir = os.getcwd ()
	mainFields = CartaporteInfo.getMainFields (fieldsJsonFile, runningDir)
	Utils.saveFields (mainFields, fieldsJsonFile, "Results")

#----------------------------------------------------------
# Class that gets main info from Ecuapass document 
#----------------------------------------------------------
class EcuCPT_SILOGISTICA (CartaporteInfo):
	def __init__ (self, fieldsJsonFile, runningDir):
		super().__init__ (fieldsJsonFile, runningDir)
		self.empresa   = EcuData.getEmpresaInfo ("SILOGISTICA")

	#-------------------------------------------------------------------
	#-- Get subject info: nombre, dir, pais, ciudad, id, idNro ---------
	#-- SILOGISTICA format: 4 lines: <Nombre> <Direccion> <ID> <PaisCiudad> -----
	#-------------------------------------------------------------------
	#-- Get subject info: nombre, dir, pais, ciudad, id, idNro
	def getSubjectInfo (self, key):
		subject = {"nombre":None, "direccion":None, "pais": None, 
		           "ciudad":None, "tipoId":None, "numeroId": None}
		text	= Utils.getValue (self.fields, key)
		try:
			lines = text.split ("\n")
			if len (lines) < 4:
				text    = re.sub ("\s*//\s*", "\n", text)   # For SILOG "//" separator cartaportes
			lines = text.split ("\n")
			subject ["nombre"]    = lines [0]
			subject ["direccion"] = lines [1]
			text, subject = Extractor.removeSubjectId (lines[2], subject, key)
			text, subject = Extractor.removeSubjectCiudadPais (lines [3],  subject, self.resourcesPath, key)
		except:
			Utils.printException (f"Obteniendo datos del sujeto: '{key}' en el texto", text)

		return (subject)

#--------------------------------------------------------------------
# Call main 
#--------------------------------------------------------------------
if __name__ == '__main__':
	main ()

