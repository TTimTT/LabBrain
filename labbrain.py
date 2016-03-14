#!/usr/bin/env ipython3

#Import Module For UNITS handling
from pint import UnitRegistry

from labbfunc import *

######################
#Declaration of tables
######################
#Implicit Data
headers = list()

#If no parameter is given to the constructor, the unit registry is populated
#with the default list of units and prefixes
ureg = UnitRegistry()

#\\\\\\\\\\\\\\\\\\\\\\\\
#Read conf file & template
#////////////////////////
conf = SafeConfigParser()
conf.read('config')
sections = list()

#\\\\\\\\\\\\\\\\\\\\\\\\
#Fetch of conf in tables
#////////////////////////

for section in conf.sections():
	filenames = conf.get(section,'Filename').split(':')
	output = conf.get(section,'Output')
	typ = conf.get(section,'Type')
	caption = conf.get(section,'Caption')
	ptext = conf.get(section,'PText')
	ftext = conf.get(section,'FText')
	#Check which type of data is the last appended
	#Append empty element to Formula for index compability
	#Append empty element to Headers for index compability

	#TODO TODO modify if logic
	if not typ == 'Listing':
		analyse = conf.get(section,'Analyse')

	if typ == 'Listing':
		#Append empty element to Listings for index compability
		analyse = ''
		formula = ''
		header = {'Var': None, 'Unit': None, 'UNC': None}

	elif typ == 'Image':

		formula = ''
		header = {'Var': None, 'Unit': None, 'UNC': None}

	#Check which type of data is the last appended
	elif not typ == 'Image':

		#Get Formulas for Table & Plot
		formula = conf.get(section,'Formula')

#TODO HERE TO START OPENING AND FETCHING CSV DATA

		#Image files cannot be CSV:
		#csv module. Make a buffer TODO read the doc
		for filename in filenames:
			csv_data = open(filename,'r')
			reader = next(csv.reader(filter(lambda row: row[0]!='#', csv_data),delimiter='\t')) #TEMPORARY
			csv_data.close()
	
			header = list() #TEMPORARY
			for column in reader:
				#Fetch Vars, Units, Uncertainties
				#Append to List of Dict HEADERS
				header.append({'Var': column.partition('(')[0], 'Unit': column.partition('(')[-1].partition(')')[0], 'UNC': column.rpartition('(')[-1].rpartition(')')[0]})
			headers.append(header)

#\\\\\\\\\\\\\\\\\\\\\\\\
#Put conf in dict
#////////////////////////
#END TEST
	sections.append({'Section': section, 'Filename': filenames, 'Output': output, 'Type': typ, 'Caption': caption, 'Formula': formula, 'Analyse': analyse, '<<': ptext, '>>': ftext, 'Header': header})


#\\\\\\\\\\\\\\\\\\\\\\\\
#Prints All datas Testing:
#////////////////////////
#Sort By Outputs to place all Configs Key
sections = SortByOutputs(sections)

for index in range(len(sections)):
	SectionsPrint(sections[index])

#\\\\\\\\\\\\\\\\\\\\\\\\
#Handle Formulas:
#////////////////////////

	#Fetch New Headers From Formulas
	newheaders = [x.partition('=')[0] for x in sections[index]['Formula'].split(':')]

####################
#LaTeX Part Writing:
####################
	#Check/Create/Complete latex folders/files
	LaTeXSectionHandler(sections, index)

#\\\\\\\\\\\\\\\\\\\\\\\\
#LaTeX Part TODO complete:
#////////////////////////

	#Write LaTeX Text Previous Table
	#What has to be written
	latext = list()

	#TODO Move in more templated place

	if sections[index]['Type'] == 'Table':
		#Handle FText
		PFTextFileHandler(latext, sections, index, '<<')

		#Handle Formula for Units dimension computation
		formulas = FormulaHandler(sections[index]['Formula'],sections[index]['Header'],'Unit')

		#Computation of Units
		# TODO SECURE THIS TODO TODO TODO
		for i in range(len(formulas)):
			#Little hack to avoid the '1' which can be removed with .units
			#But the .units doesn't allow us to print in abreviations TODO
			#Make an issue?? TODO
			formula = '\ ($'+('{:L~}$)'.format(eval(formulas[i])).partition(' ')[2])
			newheaders[i] = newheaders[i]+formula

		#Create Table Header
		if not len(sections[index]['Filename']) == 1:
			#Adding extra column
			newheaders = [' '] + newheaders

		LaTeXTable(latext, 'begin', newheaders)

		#Open CSV Data second time for Row Reading
		for filename in sections[index]['Filename']:
			csv_data = open(filename,'r')
			reader = csv.reader(filter(lambda row: row[0]!='#', csv_data),delimiter='\t')
			# Skip the headers
			next(reader, None)

			if not len(sections[index]['Filename']) == 1:
				newrow = [filename]
			else:
				newrow = []

			for row in reader:
				#Remove multiple tabs
				row = [column for column in row if column != '']
				
				formulas = FormulaHandler(sections[index]['Formula'],sections[index]['Header'],'UNC')
				for formula in formulas:
					newrow.append(FormulaCompute(formula,row))

				newrow = [str(w).replace('+/-', ' \pm ') for w in newrow]
				LaTeXTable(latext, 'core', newrow)

				if not len(sections[index]['Filename']) == 1:
					newrow = [' ']
				else:
					newrow = []

			latext.append('\\hline \\hline')

		#Remove last extra hline hline
		del latext[-1]
		LaTeXTable(latext, 'end', caption = sections[index]['Caption'],label = sections[index]['Type']+':'+str(sections[index]['Filename'])+sections[index]['Output']+str(index))
	
		#END OF CSV READING
		csv_data.close()
	#END Table LaTeX WRITER

#Handle Table/Image/Figure
	elif sections[index]['Type'] == 'Image':

		#Handle FText
		PFTextFileHandler(latext, sections, index, '<<')

		#Write beginning part of LaTeX Image
		LaTeXFigure(latext, 'begin')

		for i in range(len(sections[index]['Filename'])):
			#Write core part of LaTeX Image
			label = sections[index]['Type']+':'+str(sections[index]['Filename'])+sections[index]['Output']+str(i)
			LaTeXFigure(latext, 'core', sections[index]['Filename'][i], ' ', label)

		#Write end part of LaTeX Image
		LaTeXFigure(latext, 'end',  caption=sections[index]['Caption'])
	#END Table LaTeX WRITER

#Handle Table/Image/Figure/Replaced
	elif sections[index]['Type'] == 'Plot':
		PlotHandler(sections,index)
		print('Plot')

#Handle Code 
	elif sections[index]['Type'] == 'Listing':
		for filename in sections[index]['Filename']:
			LaTeXListings(latext,filename,sections[index]['Caption'])


#Handle FPText:

	#Write LaTeX Text Following Table
	#Check that its not an empty analyse
	if not len(sections[index]['Analyse']) == 0:
		PFTextFileHandler(latext, sections, index, '>>')
	
	#Final Writing down
	#TODO Check for max RAM Size
	output=open('../Report/'+sections[index]['Output']+'.tex','a')
	output.write(''.join(latext))
	output.close()

