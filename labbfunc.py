#Import Module For INI config file handling
from configparser import SafeConfigParser
#Import Module For CSV handling
import csv
#Import Module For FILEPATH handling
import os.path
 #Import Module For UNCERTAINTIES handling
from uncertainties import  *
from uncertainties.umath import *
#For random selection of pftext
from random import randint

#For plotting
from datalabplot import *

#########################
#Declaration of functions
#########################
#Printing Sections Info
def SectionsPrint(section):

	print('General Config:')
	print(' Section:',section['Section'])

	for filename in section['Filename']:
		print(' Filename:',filename)

	print(' Output:',section['Output'])
	print(' Type:',section['Type'])
	print(' Caption:',section['Caption'])

	if not section['Type'] == 'Listing':
		if not section['Type'] == 'Image':
			print(' Formula:',section['Formula'])

			print(' Analyse:',section['Analyse'])

			print('\nImplicit Config:')
			print(' Header:',section['Header'])

	print('\nText Config:')
	print(' PText:',section['<<'])
	print(' FText:',section['>>'],'\n')


#END

#Quick Sort
def SortByOutputs(lists):
	"""Quicksort using list comprehensions"""
	if lists == []: 
		return []
	else:
		pivot = lists[0]
		lesser = SortByOutputs([x for x in lists[1:] if x['Output'] < pivot['Output']])
		greater = SortByOutputs([x for x in lists[1:] if x['Output'] >= pivot['Output']])

		return lesser+[pivot]+greater

#END

#Template Symbol not function
def InvertPFTextSymbol(symbol):
	if symbol == '<<':
		return '>>'
	elif symbol == '>>':
		return '<<'
#END

#LaTeX Listing Listings
def LaTeXListings(latext,filename, caption= 'N/A'):

	ext = filename.partition('.')[2]
	latext.append('\lstinputlisting[caption='+caption+',style='+ext+']{"./Data/'+filename+'"}\n')

#END

#LaTeX Image Builder
def LaTeXFigure(latext, state, filename='N/A', caption='N/A', label='N/A'):

	if state == 'begin':
		latext.append('\\begin{figure}[h!]\n')
		latext.append('\t\\centering\n')

	elif state == 'core':
		latext.append('\t\\begin{subfigure}[b]{0.49\\textwidth}\n')
		latext.append('\t\t\\includegraphics[width=\\textwidth]{'+filename+'}\n')
		latext.append('\t\t\\caption{'+caption+'}\n')
		latext.append('\t\t\\label{'+label+'}\n')
		latext.append('\t\\end{subfigure}\n')

	elif state == 'end':
		#TODO support for Main Captions and Labels
		latext.append('\t\\caption{'+caption+'}\n')
		latext.append('\t\\label{'+label+'}\n')
		latext.append('\\end{figure}\n')
#END	
#TODO Harmonise all functions return or no?
#LaTeX Table builder
def LaTeXTable(latext, state, row=None, caption='N/A',label='N/A'):
	#Remove extra tabs
	if state == 'begin':
		latext.append('\\begin{table}[h!]\n')
		latext.append('\t\\centering\n')
		latext.append('\t\\begin{tabular}{'+'|c'*len(row)+'|}\n')
		latext.append('\t\t\\hline \n')
		latext.append('\t\t'+' & '.join(filter(None,row))+' \\\\\n')
		latext.append('\t\t\\hline \\hline \n')

	elif state == 'core':
		latext.append('\t\t$ '+' $ & $ '.join(map(str,row))+' $ \\\\\n')

	elif state == 'end':
		latext.append('\t\t \\hline \n')
		latext.append('\t\\end{tabular}\n')
		latext.append('\t\\caption{'+caption+'}\n')
		latext.append('\t\\label{'+label+'}\n')
		latext.append('\\end{table}\n')
#END

#LaTeX Itemize builder
def LaTeXItemize(text, items):

	text.append('\\begin{itemize}\n')
	for item in items:
		text.append('\t\\item '+item+' \n')
	text.append('\\end{itemize}\n')
	return text
#END


#LaTeX Folder/File/Sections writer
def LaTeXSectionHandler(sections, index):
	# Change absolute path TODO
	# Find good place to put python file TODO
	# Define aboslute and numbers
	if not os.path.isfile('../Report/'+sections[index]['Output']+'.tex'):
		os.makedirs(os.path.dirname('../Report/'+sections[index]['Output']+'.tex'), exist_ok=True)
		output=open('../Report/'+sections[index]['Output']+'.tex','a')
		output.write('\\'+'sub'*(len(sections[index]['Output'].split('/'))-1)+'section{'+os.path.basename(os.path.normpath(sections[index]['Output']))+'}\n')
		output.close()

		fsection=open(os.path.dirname('../Report/'+sections[index]['Output'])+'.tex','a')
		fsection.write('\\input{"./Report/'+sections[index]['Output']+'.tex'+'"}\n')
		fsection.close()
		#append subsection in Experiment
#END


#Math Eval FUNCTION Part TODO remove????? its uselss!
def FormulaCompute(formula,row):
	#Change {x} by the numeric in CSV file
	#Evaluate with Python
	#Set for Each Element in List
	return eval(formula.format(*row))
#END

#Handle Formulas:
def FormulaHandler(formulas, headers, default='default'):
	#TODO OPTIMISATION AVOID SWITCH AND MAKE FUNCTION RETURN STRING to replace
	formula = formulas
	for i in range(len(headers)):
		if default == 'default':
			print('default formula handler, change this TODO')

		elif default == 'UNC':
			formula = formula.replace(headers[i]['Var'], 'ufloat({'+str(i)+'},'+headers[i]['UNC']+')')

		elif default == 'Unit':
			formula = formula.replace(headers[i]['Var'], 'ureg("'+headers[i]['Unit']+'")')

	return [x.partition('=')[2] for x in formula.split(':')]
#END

#\\\\\\\\\\\\\
#Handle FPText:
#/////////////
def PFTextFileHandler(latext, sections, index, TxtType=None):
	#TODO put this in config file section
	#Partition X~Y@file.ptxt / Extract 'file.ptxt'
	f_text = sections[index][TxtType].partition('@')[2]
	#Extract 'X~Y'
	xy_text = sections[index][TxtType].partition('@')[0]
	#Extract 'X'
	x_text = xy_text.partition('~')[0]
	#Extract 'Y'
	y_text = xy_text.partition('~')[2]
	#Predecleration
	l_text = ''

	#If X is alone
	if not y_text == '':
	#Make Rand between X~Y
		x_text = randint(int(x_text),int(y_text))

	#Interactive mode for populating template database
	if x_text == 'i':
		l_text = input('Add another sentences:')+'\n'
		#Check if empty line to escape mode
		if not l_text == '\n':
			output = open(f_text,'a')
			output.write(TxtType+l_text)
			output.close()
		else:
			#Set Default Value
			l_text = ''
			x_text = '0'
			print('Interact mode escaped!')

	#Normal mode fetching from file
	if l_text == '':
		text = open(f_text,'r')
		#Fetch only TxtType starting lines and take the Xth one
		#Ignore comments '#'
		#Acces desired X lines
		# the '+1' is to avoid the '' from splitting
		l_text = (''.join([line for line in text if not line.startswith('#') and not line.startswith(InvertPFTextSymbol(TxtType))])).split(TxtType)[int(x_text)+1]

		#Closing File
		text.close()

	##//Replace Special Chars for custom templating
	# '~' --> ~\ref{TYPE:Outputs}
	# '$' --> length of Analyse
	amount = str(len(sections[index]['Analyse']))

	#For Refs:
	label = list()
	for i in range(len(sections[index]['Filename'])):
		label.append('~\\ref{'+sections[index]['Type']+':'+str(sections[index]['Filename'])+sections[index]['Output']+str(i)+'}')

	#Replacing
	l_text = l_text.replace('~',','.join(label))
	l_text = l_text.replace('$',amount)

	#ADD Description DATA for >>
	if TxtType == '>>':
		l_text = ''.join(LaTeXItemize([l_text],sections[index]['Analyse']))

	#Add LaTeX end paragraph replace last '\n' by
	#'\\ \n' for pretty output
	elif TxtType == '<<':
		l_text = l_text[:-1]+'\\\\\n'

		#Add Paragraph if Asked with '¶': ALTGR + R
		if sections[index]['Section'][0] == '¶':
			l_text = '\paragraph{'+sections[index]['Section'][1:]+'} ' + l_text

	latext.append(l_text)
#END



#DEV 
def PlotHandler(sections,index):

	#List of Different Text Files
	datas = []
	errors = []

	for filename in sections[index]['Filename']:
		#Open CSV Data second time for Row Reading
		csv_data = open(filename,'r')
		reader = csv.reader(filter(lambda row: row[0]!='#', csv_data),delimiter='\t')
		# Skip the headers
		next(reader, None)

		#Handle Formula for Units dimension computation
		formulas = FormulaHandler(sections[index]['Formula'],sections[index]['Header'],'Unit')
		#List of lines of files
		data = []
		error = []
		for row in reader:
			#Remove multiple tabs
			row = [column for column in row if column != '']
	
			newrow = []	
			formulas = FormulaHandler(sections[index]['Formula'],sections[index]['Header'],'UNC')
			for formula in formulas:
				newrow.append(FormulaCompute(formula,row))

			#Fetch nominal values
			data.append([nominal_value(row) for row in newrow])
			#Fetch respective deviation
			error.append([std_dev(row) for row in newrow])

		#END OF CSV READING
		csv_data.close()

		#Fetch New Headers From Formulas
		newheaders = [x.partition('=')[0] for x in sections[index]['Formula'].split(':')]

		#Transpose data
		#Plots Columns
		datas.append(list(map(list, zip(*data))))
		errors.append(list(map(list, zip(*error))))

	#Send dats to plotting file functions
	LabDataPlot(newheaders, datas, errors)
	

