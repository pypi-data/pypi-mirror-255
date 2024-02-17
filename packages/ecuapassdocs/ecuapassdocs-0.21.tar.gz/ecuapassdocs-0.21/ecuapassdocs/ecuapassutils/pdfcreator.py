#!/usr/bin/env python

import io, sys, tempfile, json, re
from os.path import join

# External packages for creating PDF documents
from PyPDF2 import PdfReader, PdfWriter
import reportlab
from reportlab.pdfgen import canvas

# External package for getting image size
from PIL import Image 

# For loading resources
#from .resourceloader import ResourceLoader 
from ecuapassdocs.ecuapassutils.resourceloader import ResourceLoader 

#----------------------------------------------------------------
# Crea un documento PDF con background y textos
#----------------------------------------------------------------
class CreadorPDF:
	def __init__ (self, docType):
		self.docType = docType
		if docType == "manifiesto":
			self.backgroundPdf = ResourceLoader.loadPdf ("docs", 'manifiesto-vacio-NTA-BYZA.pdf')
			self.backgroundImg = ResourceLoader.loadImage ("docs", 'manifiesto-vacio-NTA-BYZA.png')
			self.inputBounds   = ResourceLoader.loadJson ("docs", 'manifiesto_input_parameters.json')
			self.prefix = "MCI"
		elif docType == "cartaporte":
			self.backgroundPdf = ResourceLoader.loadPdf ("docs", 'cartaporte-vacia-SILOG-BYZA.pdf')
			self.backgroundImg = ResourceLoader.loadImage ("docs", 'cartaporte-vacia-SILOG-BYZA.png')
			self.inputBounds   = ResourceLoader.loadJson ("docs", 'cartaporte_input_parameters.json')
			self.prefix = "CPI"
		else:
			print (f"Error: Tipo de documento '{docType}' no soportado")
			sys.exit (0)

	#----------------------------------------------------------------
	#-- Crea PDF con otro PDF como background y añade texto sobre este
	#-- pdfType: "preliminar", "original", "copia", "clon"
	#----------------------------------------------------------------
	def createPdfDocument (self, inputValues, pdfType):
		pdfType     = pdfType.lower()
		tmpPath     = tempfile.gettempdir ()
		copyString  = ""
		if "preliminar" in pdfType:
			inputValues ['txt00'] = "PRELIMINAR"
			copyString = "PRELIMINAR"
		elif "original" in pdfType:
			copyString = "ORIGINAL"
		elif "copia" in pdfType:
			copyString = "COPIA"

		print (">>> creando PDF: txt00:", inputValues ["txt00"])

		numberCPI   = inputValues ['txt00']
		copyKey     = max (inputValues.keys ())
		inputValues [copyKey] = copyString;
		outPdfPath  = join (tmpPath, f"{self.prefix}-{numberCPI}.pdf") 
		outJsonPath = join (tmpPath, f"{self.prefix}-{numberCPI}.json") 

		text_pdf, jsonFieldsDic = self.writeInputsToPdf (self.inputBounds, inputValues)
		json.dump (jsonFieldsDic, open (outJsonPath, "w"), indent=4)
		self.merge_pdfs (self.backgroundPdf, text_pdf, outPdfPath)

		return outPdfPath, outJsonPath

	#----------------------------------------------------------------
	# Write text values to output PDF
	#----------------------------------------------------------------
	def writeInputsToPdf (self, inputBounds, inputValues):
		FONTSIZE = 9                  # Font "normal"
		packet = io.BytesIO()
		can = canvas.Canvas(packet)

		for key, params in inputBounds.items():
			imgBounds = [params["x"]-7, params["y"]-7, params ["width"], params ["height"]]
			pdfBounds = self.convertToImageToPdfBounds (imgBounds)

			print (">>>", params ["font"])
			if params ["font"] == "hidden":
				FONTSIZE = 0
			elif params ["font"] == "normal":
				FONTSIZE = 9
			elif params ["font"] == "large":
				FONTSIZE = 16
			can.setFont ("Helvetica-Bold", FONTSIZE)

			text         = inputValues [key]
			textLines    = text.split ("\n")
			for i, line in enumerate (textLines):
				top = pdfBounds[1] - (i+1)*FONTSIZE
				if params ["align"] == "right":
					can.drawRightString (pdfBounds[0] + pdfBounds [2], top, line.strip())
				elif params ["align"] == "center":
					can.drawCentredString (pdfBounds[0] + pdfBounds [2]/2, top, line.strip())
				else:    # "left" align
					can.drawString (pdfBounds[0], top, line.strip())

		jsonFieldsDic = self.embedFieldsIntoPDF (can, inputBounds, inputValues)
		can.save()

		packet.seek(0)
		return PdfReader(packet), jsonFieldsDic

	#----------------------------------------------------------------
	#-- Embed fields info (key:value) into PDF doc
	#-- Info is embedded according to Azure format
	#----------------------------------------------------------------
	def embedFieldsIntoPDF (self, pdfCanvas, inputBounds, inputValues):
		if self.docType == "manifiesto":
			return self.embedFieldsIntoPDFManifiesto (pdfCanvas, inputBounds, inputValues)
		elif self.docType == "cartaporte":
			return self.embedFieldsIntoPDFCartaporte (pdfCanvas, inputBounds, inputValues)

		return None

	def embedFieldsIntoPDFManifiesto (self, pdfCanvas, inputBounds, inputValues):
		jsonFieldsDic = {}
		for key, params in inputBounds.items():
			fieldName    = params ["field"]
			value        = inputValues [key]
			jsonFieldsDic [fieldName] = {"value": value, "content": value}

		embedded_jsonData = json.dumps (jsonFieldsDic)
		pdfCanvas.setFont("Helvetica", 0)  # Set font size to 0 for hidden text
		pdfCanvas.drawString(100, 150, f"Embedded_jsonData: {embedded_jsonData}")

		return jsonFieldsDic

	def embedFieldsIntoPDFCartaporte (self, pdfCanvas, inputBounds, inputValues):
		jsonFieldsDic = {}
		gastosDic = {"value": {"ValorFlete":{"value":{}}, 
		                       "Seguro":{"value":{}}, 
							   "OtrosGastos":{"value":{}}, 
							   "Total":{"value":{}}}}
		for key, params in inputBounds.items():
			fieldName    = params ["field"]
			value        = inputValues [key]
			if "Gastos" in fieldName:
				res = re.findall ("\w+", fieldName)   #e.g ["ValorFlete", "MontoDestinatario"]
				tableName, rowName, colName = res [0], res [1], res[2]
				if value != "":
					gastosDic ["value"][rowName]["value"][colName] = {"value": value, "content": value}
			else:
				jsonFieldsDic [fieldName] = {"value": value, "content": value}

		jsonFieldsDic [tableName] = gastosDic

		embedded_jsonData = json.dumps (jsonFieldsDic)
		pdfCanvas.setFont("Helvetica", 0)  # Set font size to 0 for hidden text
		pdfCanvas.drawString(100, 150, f"Embedded_jsonData: {embedded_jsonData}")

		return jsonFieldsDic

	#----------------------------------------------------------------
	#-- Convert image box bounds to pdf box bounds
	#----------------------------------------------------------------
	def convertToImageToPdfBounds (self, imageBoxBounds):
		try:
			class Img: # Internal image used as background
				x, y          = imageBoxBounds [0], imageBoxBounds [1]
				width, height = imageBoxBounds [2], imageBoxBounds [3]

			class Pdf: # Bounds for output PDF
				x, y, width, height = None, None, None, None

			imgSize = self.getImageSize (self.backgroundImg)
			pdfSize = self.getPdfSize (self.backgroundPdf)

			pdfWidth, pdfHeight = pdfSize [0], pdfSize [1]
			imgWidth, imgHeight = imgSize [0], imgSize [1]

			conversionFactor = pdfWidth / float (imgWidth);
			Pdf.x = int (Img.x * conversionFactor);
			Pdf.y = pdfHeight - int (Img.y * conversionFactor) 
			#Pdf.y = 20 + pdfHeight - int (Img.y * conversionFactor);

			Pdf.width  = int (Img.width * conversionFactor);
			Pdf.width  = int (Pdf.width - 0.02*Pdf.width);
			Pdf.height = int (Img.height * conversionFactor);

			return (Pdf.x, Pdf.y, Pdf.width, Pdf.height)
		except:
			print (f"Error: No se pudo convertir coordenadas de la imagen a Pdf")
			raise

	#----------------------------------------------------------------
	#-- Merge pdf background image with text
	#----------------------------------------------------------------
	def merge_pdfs(self, backgroundPdf, text_pdf, outputPdfPath):
		output_pdf_writer = PdfWriter()

		for page_number in range(len (backgroundPdf.pages)):
			page = backgroundPdf.pages [page_number]
			page.merge_page(text_pdf.pages [page_number])
			output_pdf_writer.add_page(page)

		with open(outputPdfPath, 'wb') as output_pdf:
			output_pdf_writer.write(output_pdf)

	#----------------------------------------------------------------
	#----------------------------------------------------------------
	def getInputBoundsFromJsonFile (self, inputsJsonPath):
		inputBounds = {}
		with open (inputsJsonPath) as fp:
			inputBounds = json.load (fp)

		return inputBounds

	#----------------------------------------------------------------
	#----------------------------------------------------------------
	def getImageSize (self, imageObject):
		width, height = imageObject.size
		return width, height

	def getImageSizeFromFile (self, docPath):
		try:
			# Open the PNG image
			with Image.open(docPath) as img:
				return self.getImageSize (img)
		except Exception as e:
			print(f"Error: {e}")
			return None

	#----------------------------------------------------------------
	#----------------------------------------------------------------
	def getPdfSize (self, pdfObject):
		# Get the dimensions from the first page (assuming all pages have the same size)
		first_page = pdfObject.pages [0]
		width, height = first_page.mediabox.width, first_page.mediabox.height
		return width, height

	def getPdfSizeFromFile (self, pdfPath):
		try:
			# Open the PDF file in binary mode
			with open(pdfPath, 'rb') as pdf_file:
				# Create a PDF reader object
				pdf_reader = PdfReader(pdf_file)
				return self.getPdfSize (pdf_reader)
		except Exception as e:
			print(f"Error: {e}")
			return None

#--------------------------------------------------------------------
# Main
#--------------------------------------------------------------------
if __name__ == "__main__":
    backgroundPdfPath = "background.pdf"  # Provide the path to your background PDF
    outputPdfPath = "output.pdf"  # Provide the desired output PDF path

    # Define text and bounds (x, y) on the page
    inputBounds = {
        "Text1": (100, 200),
        "Text2": (300, 400),
        # Add more text bounds as needed
    }

    creadorPDF = CreadorPDF ("cartaporte")
    creadorPDF.crearPDF (backgroundPdfPath, inputBounds, outputPdfPath)

