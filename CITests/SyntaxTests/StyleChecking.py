import codecs
import argparse
import os
import sys 
import platform
import time
from CI_Configuration.configuration import Config

class StyleCheck(Config):
	""" Class to Check the Style of Packages and Models
	Export a HTML-Log File"""
	
	def __init__(self, package, library, dymolaversion, changed_models):
		self.package = package
		self.library = library
		self.dymolaversion = dymolaversion
		self.changed_models = changed_models
		super().__init__()

		from dymola.dymola_interface import DymolaInterface  # Load modelica python interface
		from dymola.dymola_exception import DymolaException
		print(f'1: Starting Dymola instance')
		if platform.system() == "Windows":
			dymola = DymolaInterface()
		else:
			dymola = DymolaInterface(dymolapath="/usr/local/bin/dymola")
		self.dymola = dymola
		self.dymola_exception = DymolaException()
		self.dymola.ExecuteCommand(
			"Advanced.TranslationInCommandLog:=true;")  # Writes all information in the log file, not only the

	def _dym_check_lic(self):  # check the license
		dym_sta_lic_available = self.dymola.ExecuteCommand('RequestOption("Standard");')
		lic_counter = 0
		while dym_sta_lic_available is False:
			print(f'{self.CRED} No Dymola License is available {self.CEND} \n Check Dymola license after 180.0 seconds')
			self.dymola.close()
			time.sleep(180.0)
			dym_sta_lic_available = self.dymola.ExecuteCommand('RequestOption("Standard");')
			lic_counter += 1
			if lic_counter > 10:
				if dym_sta_lic_available is False:
					print(f'There are currently no available Dymola licenses available. Please try again later.')
					self.dymola.close()
					exit(1)
		print(f'2: Using Dymola port {str(self.dymola._portnumber)} \n {self.green} Dymola License is available {self.CEND}')

	def _check_library(self, library_check):
		if library_check == True:
			print(f'Found {self.library} library and start style check')
		elif library_check == False:
			print(f'Path of library {self.library} is wrong. Please Check Path.')
			exit(1)

	def _set_library_modelmanagement(self):
		if platform.system() == "Windows":  # Load ModelManagement
			self.dymola.ExecuteCommand(
				'cd("C:\Program Files\Dymola ' + self.dymolaversion + '\Modelica\Library\ModelManagement 1.1.8\package.moe");')
		else:
			self.dymola.ExecuteCommand(
				'cd("/opt/dymola-' + self.dymolaversion + '-x86_64/Modelica/Library/ModelManagement 1.1.8/package.moe");')


	def _style_check(self):
		print(f'Start Style Check. Check package or model: {self.package}')  # Start CheckLibrary in ModelManagement
		library_check = self.dymola.openModel(self.library)  # Load AixLib
		self._check_library(library_check=library_check)
		self._set_library_modelmanagement()
		self.dymola.ExecuteCommand('ModelManagement.Check.checkLibrary(false, false, false, true, "' + self.package + '", translationStructure=false);')
		logfile = self.library.replace("package.mo", self.package + "_StyleCheckLog.html")
		self.dymola.close()
		return logfile, model_list

	def _changed_style_check(self, model_list):
		changed_model_list = []
		if len(model_list) > 100:
			print("Over 100 changed models. Check all models in AixLib Library")
			print(f'Check AixLib Library: {self.package}')
			self.dymola.ExecuteCommand('ModelManagement.Check.checkLibrary(false, false, false, true, "' + self.package + '", translationStructure=false);')
			logfile = self.library.replace("package.mo", self.package + "_StyleCheckLog.html")
			self.changed_models = False
		else:
			path = self.library.replace("package.mo", "")
			for model in model_list:
				print(f'Check package or model {model}')
				self.dymola.ExecuteCommand('ModelManagement.Check.checkLibrary(false, false, false, true, "' + model + '", translationStructure=false);')
				log = codecs.open(f'{path}{model}_StyleCheckLog.html', "r", encoding='utf8')
				for line in log:
					changed_model_list.append(line)
				log.close()
				os.remove(f'{path}{model}_StyleCheckLog.html')
			all_logs = codecs.open(f'{path}ChangedModels_StyleCheckLog.html', "w", encoding='utf8')
			for model in changed_model_list:
				all_logs.write(model)
			all_logs.close()
			logfile = path + "ChangedModels_StyleCheckLog.html"
		self.dymola.close()
		return logfile, model_list

	def _sort_mo_models(self):
		changed_file = codecs.open(self.exit_file, "r", encoding='utf8')
		model_list = []
		lines = changed_file.readlines()
		for line in lines:
			if line.rfind(".mo") > -1:
				model = line[line.rfind(self.package):line.rfind(".mo")].replace(os.sep, ".")
				model = model.lstrip()
				model_list.append(model)
				continue
		changed_file.close()
		if len(model_list) == 0:
			print("No Models to check")
			exit(0)
		return model_list

	def _Style_Check_Log(self, inputfile, model_list):
		outputfile = inputfile.replace("_StyleCheckLog.html", "_StyleErrorLog.html")
		log_file = codecs.open(inputfile, "r", encoding='utf8')
		error_log = codecs.open(outputfile, "w", encoding='utf8')
		ErrorCount = 0
		for line in log_file:
			line = line.strip()
			if line.find("Check ok") > -1:
				continue
			if line.find("Library style check log") > -1:
				continue
			if self.changed_models is False:
				if line.find(f'HTML style check log for {self.package}') > -1:
					continue
			if self.changed_models is True:
				correct = 0
				for model in model_list:
					if line.find(f'HTML style check log for {model}') > -1:
						correct = correct + 1
						break 
				if correct > 0 :
					continue
			if len(line) == 0:
				continue
			else:
				print(f'{self.CRED}Error in model:\n{self.CEND}{line.lstrip()}')
				ErrorCount = ErrorCount + 1 
				error_log.write(line)
		log_file.close()
		error_log.close()
		if self.changed_models is False:
			if ErrorCount == 0:
				print(f'{self.green}Style check of model or package {self.package} was successful{self.CEND}')
				exit(0)
			elif ErrorCount > 0 :
				print(f'{self.CRED}Test failed. Look in {self.package}_StyleErrorLog.html{self.CEND}')
				exit(1)
		else:
			if ErrorCount == 0:
				for model in model_list:
					print(f'{self.green}\n Style check of model or package {model} was successful.{self.CEND}')
					continue
				exit(0)
			elif ErrorCount > 0 :
				print(f'{self.CRED}\nTest failed. Look in {outputfile.lstrip()}{self.CEND}')
				exit(1)
			
def _setEnvironmentVariables(var,value):  # Add to the environemtn variable 'var' the value 'value'
	if var in os.environ:
		if platform.system() == "Windows":
			os.environ[var] = value + ";" + os.environ[var]
		else:
			os.environ[var] = value + ":" + os.environ[var]
	else:
		os.environ[var] = value	

def _setEnvironmentPath(dymolaversion):
	if platform.system() == "Windows":  # Checks the Operating System, Important for the Python-Dymola Interface
		_setEnvironmentVariables("PATH", os.path.join(os.path.abspath('.'), "Resources", "Library", "win32"))
		sys.path.insert(0, os.path.join('C:\\',
                                        'Program Files',
                                        'Dymola ' + dymolaversion,
                                        'Modelica',
                                        'Library',
                                        'python_interface',
                                        'dymola.egg'))
	else:
		_setEnvironmentVariables("LD_LIBRARY_PATH",
                                 os.path.join(os.path.abspath('.'), "Resources", "Library", "linux32") + ":" +
                                 os.path.join(os.path.abspath('.'), "Resources", "Library", "linux64"))
		sys.path.insert(0, os.path.join('opt',
                                        'dymola-' + dymolaversion + '-x86_64',
                                        'Modelica',
                                        'Library',
                                        'python_interface',
                                        'dymola.egg'))
	print(f'operating system {platform.system()}')
	sys.path.append(os.path.join(os.path.abspath('.'), "..", "..", "BuildingsPy"))
	# The path to buildingspy must be added to sys.path to work on Linux.
    # If only added to os.environ, the Python interpreter won't find buildingspy

if  __name__ == '__main__':
	parser = argparse.ArgumentParser(description = "Check the Style of Packages")  # Configure the argument parser
	check_test_group = parser.add_argument_group("arguments to run check tests")
	check_test_group.add_argument('-s',"--single-package",metavar="AixLib.Package", help="Test only the Modelica package AixLib.Package")
	check_test_group.add_argument("-p","--path", default=".", help = "Path where top-level package.mo of the library is located")
	check_test_group.add_argument("-DS", "--dymolaversion",default="2020", help="Version of Dymola(Give the number e.g. 2020")
	check_test_group.add_argument("-CM", "--changed_models",default=False, action="store_true")
	args = parser.parse_args()  # Parse the arguments

	CheckStyleTest = StyleCheck(package=args.single_package,
								library=args.path,
								dymolaversion=args.dymolaversion,
								changed_models=args.changed_models)
	_setEnvironmentPath(dymolaversion=args.dymolaversion)

	CheckStyleTest._dym_check_lic()
	if args.changed_models is False:
		result = CheckStyleTest._style_check()
		CheckStyleTest._Style_Check_Log(inputfile=result[0], model_list=result[1])
	if args.changed_models is True:
		model_list = CheckStyleTest._sort_mo_models()
		result = CheckStyleTest._changed_style_check(model_list=model_list)
		CheckStyleTest._Style_Check_Log(inputfile=result[0], model_list=result[1])
