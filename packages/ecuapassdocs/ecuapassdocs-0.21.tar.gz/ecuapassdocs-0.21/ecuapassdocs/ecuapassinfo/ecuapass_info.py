
import os, json, re

from .ecuapass_data import EcuData
from .ecuapass_extractor import Extractor
from .ecuapass_utils import Utils

# Base class for all info document clases: CartaporteInfo (CPI), EcuMNF (MCI), EcuDCL (DTAI)
class EcuInfo:
	def __init__ (self, fieldsJsonFile, runningDir):
		self.fieldsJsonFile      = fieldsJsonFile
		self.runningDir          = runningDir
		self.resourcesPath       = os.path.join (runningDir, "resources", "data-cartaportes") 
		self.fields              = json.load (open (fieldsJsonFile))
		self.fields ["jsonFile"] = fieldsJsonFile
		self.ecudoc              = {}

	def getNombreEmpresa (self):
		return self.empresa ["nombre"]

	def getDireccionEmpresa (self):
		return self.empresa ["direccion"]

	#-----------------------------------------------------------
	# Get info from mercancia: INCONTERM, Ciudad, Precio, Tipo Moneda
	#-----------------------------------------------------------
	def getIncotermInfo (self, text):
		info = {"incoterm":None, "precio":None, "moneda":None, "pais":None, "ciudad":None}

		try:
			text = text.replace ("\n", " ")

			# Precio
			text, precio    = Extractor.getRemoveNumber (text)
			info ["precio"] = Utils.checkLow (Utils.convertToAmericanFormat (precio))
			text = text.replace (precio, "") if precio else text

			# Incoterm
			termsString = Extractor.getDataString ("tipos_incoterm.txt", 
			                                        self.resourcesPath, From="keys")
			reTerms = rf"\b({termsString})\b" # RE for incoterm
			incoterm = Utils.getValueRE (reTerms, text)
			info ["incoterm"] = Utils.checkLow (incoterm)
			text = text.replace (incoterm, "") if incoterm else text

			# Moneda
			info ["moneda"] = "USD"
			text = text.replace ("USD", "")
			text = text.replace ("$", "")

			# Get ciudad from text and Search 'pais' in previos boxes
			ciudadPais   = Extractor.extractCiudadPais (text, self.resourcesPath) 
			ciudad, pais = ciudadPais ["ciudad"], ciudadPais ["pais"]

			info ["ciudad"], info ["pais"] = self.searchPaisPreviousBoxes (ciudad, pais)
			if not info ["pais"]:
				info ["pais"]   = Utils.checkLow (info["pais"])
				info ["ciudad"] = Utils.addLow (info ["ciudad"])
			elif info ["pais"] and not info ["ciudad"]:
				info ["ciudad"] = Utils.addLow (info ["ciudad"])

		except:
			Utils.printException ("Obteniendo informacion de 'mercancía'")

		return info

	#-----------------------------------------------------------
	# Clean watermark: depending for each "company" class
	#-----------------------------------------------------------
	def cleanWaterMark (self, text):
		return text
