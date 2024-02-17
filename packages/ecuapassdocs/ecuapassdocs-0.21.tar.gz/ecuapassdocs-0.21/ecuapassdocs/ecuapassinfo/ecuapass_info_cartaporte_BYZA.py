#!/usr/bin/env python3

#import re, os, json, sys
#from traceback import format_exc as traceback_format_exc
#from datetime import datetime, timedelta

import re, sys, os
from .ecuapass_info_cartaporte_NTA import EcuCPT_NTA
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
	CartaporteInfo = CartaporteByza (fieldsJsonFile, runningDir)
	mainFields = CartaporteInfo.getMainFields ()
	Utils.saveFields (mainFields, fieldsJsonFile, "Results")

#----------------------------------------------------------
# Class that gets main info from Ecuapass document 
#----------------------------------------------------------
class CartaporteByza (EcuCPT_NTA):
	def __init__ (self, fieldsJsonFile, runningDir):
		super().__init__ (fieldsJsonFile, runningDir)
		self.empresa   = EcuData.getEmpresaInfo ("BYZA")

	def getSubjectInfo (self, key):
		return self.getSubjectInfoByza (key)
#	#-------------------------------------------------------------------
#	#-- Get subject info: nombre, dir, pais, ciudad, id, idNro ---------
#	#-- BYZA format: <Nombre>\n<Direccion>\n<PaisCiudad><TipoID:ID> -----
#	#-------------------------------------------------------------------
#	#-- Get subject info: nombre, dir, pais, ciudad, id, idNro
#	def getSubjectInfo (self, key):
#		subject = {"nombre":None, "direccion":None, "pais": None, 
#		           "ciudad":None, "tipoId":None, "numeroId": None}
#		try:
#			text	= Utils.getValue (self.fields, key)
#			lines   = text.split ("\n")
#
#			if len (lines) == 3:
#				idPaisLine   = lines [2]
#				nameDirLines = lines [0:2]
#			elif len (lines) == 4:
#				idPaisLine   = lines [3]
#				nameDirLines = lines [0:3]
#
#			text, subject = Extractor.removeSubjectId (idPaisLine, subject, key)
#			text, subject = Extractor.removeSubjectCiudadPais (text, subject, self.resourcesPath, key)
#			nameDirText   = "\n".join (nameDirLines)
#			text, subject = Extractor.removeSubjectNombreDireccion (nameDirText, subject, key)
#			subject ["numeroId"] = Utils.convertToEcuapassId (subject ["numeroId"])
#		except:
#			Utils.printException (f"Obteniendo datos del sujeto: '{key}' en el texto", text)
#
#		return (subject)

	#-----------------------------------------------------------
	# Clean watermark: depending for each "company" class
	#-----------------------------------------------------------
	def cleanWaterMark (self, text):
		text = re.sub ("Byza\n|Byza", "", text)

		value1 = "soluciones que facilitan tuvida"
		value2 = value1+"\n"
		text   = re.sub (rf"{value2}|{value1}", "", text)
		return text.strip()

#--------------------------------------------------------------------
# Call main 
#--------------------------------------------------------------------
if __name__ == '__main__':
	main ()

