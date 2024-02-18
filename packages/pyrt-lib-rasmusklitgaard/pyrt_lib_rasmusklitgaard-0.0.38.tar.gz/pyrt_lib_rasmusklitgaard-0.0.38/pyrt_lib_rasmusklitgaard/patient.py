from asyncore import write
from dataclasses import is_dataclass
import pydicom as pd
import numpy as np
import os
import openpyxl
import string
import operator
from typing import List, Dict
from .helpers import *
from scipy.spatial import Delaunay
import copy
import SimpleITK as sitk
import time
import copy

# comment 10 / 08 / 2022





class Cohort():
	def __init__(self):
		self.list_of_patients : List[Patient]
		self.list_of_patients = []
		self.dict_of_patients_by_id : Dict[Patient]
		self.dict_of_patients_by_id = {}
		self.n = 0
	def add_patient(self, patient : 'Patient'):
		self.list_of_patients.append(patient)
		self.dict_of_patients_by_id[patient.patient_id] = patient
		self.n += 1

	def get_patient_by_id(self, id : str) -> 'Patient':
		return self.dict_of_patients_by_id[id]
	def merge_cohorts(self, other_cohort : 'Cohort'):
		for patient in other_cohort.list_of_patients:
			self.add_patient(patient)
	def merge_many_cohorts(self, list_of_other_cohorts : List['Cohort']):
		for cohort in list_of_other_cohorts:
			self.merge_cohorts(cohort)
	def make_subcohort_gamma(self, requirements : list) -> 'Cohort':

		ops = {'>': operator.gt,
        	   '<': operator.lt,
          	   '>=': operator.ge,
          	   '<=': operator.le,
          	   '==': operator.eq}

		subcohort = Cohort()

		struct    = 	 requirements[0]
		criterium = 	 requirements[1]
		comp 	  =  ops[requirements[2]]
		req_value = 	 requirements[3]
		for patient in self.list_of_patients:
			if comp(patient.dict_of_gamma_passes[struct][criterium], float(req_value)):
				subcohort.add_patient(patient)
		return subcohort

		
	def make_subcohort_dvh(self, requirements) -> 'Cohort':
		# makes a subcohort of all patients that fulfill the requirement
		# requirement is list of strings like [struct, model, dvh_param, comparator, value]
		# so something like, ["rectal_wall", "carabe", "v20gy", ">=", "20"]

		subcohort = Cohort()
		ops = {'>': operator.gt,
        	   '<': operator.lt,
          	   '>=': operator.ge,
          	   '<=': operator.le,
          	   '==': operator.eq}

		struct 		= 		requirements[0]
		model 		= 		requirements[1]
		dvh_key 	= 		requirements[2]
		comp 		= 	ops[requirements[3]]
		req_value 	= 		requirements[4]
		
		for patient in self.list_of_patients:
			# code_interact(globals(),locals())
			if comp(patient.get_dvh_param(struct, model, dvh_key), float(req_value)):
				subcohort.add_patient(patient)
		return subcohort
	
	def make_subcohort_meta(self, requirement) -> 'Cohort':
		# requirement is [meta data key, comparator, meta data value]
		subcohort = Cohort()
		ops = {'>': operator.gt,
        	   '<': operator.lt,
          	   '>=': operator.ge,
          	   '<=': operator.le,
          	   '==': operator.eq}

		meta_data_key 	= 		requirement[0]
		comp 			= 	ops[requirement[1]]
		meta_data_value = 		requirement[2]

		for patient in self.list_of_patients:
			if comp(str(patient.metadata[meta_data_key]), str(meta_data_value)):
				subcohort.add_patient(patient)
		return subcohort
	
	def get_dvh_param_for_all(self, structure, model, key):
		# returns a list of this dvh param for all the patients
		return np.array([patient.get_dvh_param(structure, model, key) for patient in self.list_of_patients])

class Patient():
	# class to hold all info on a patient.
	def __init__(self, 
				patient_folder_path: str,
				wanted_structures: list = "default",
				xlsx_workbook: openpyxl.workbook.workbook.Workbook = None) -> None:
		t0=time.time()
		self.rtdose_letd = None
		self.rtdose_dose = None
		self.rtstruct	 = None
		t1=time.time()
		self.path_to_rtdose_letd = None
		self.path_to_rtdose_dose = None
		self.path_to_rtstruct	 = None
		self.unkelbach_rbe_weighed_dose = None
		t2=time.time()
		self.wanted_structures = wanted_structures
		self.patient_folder_path 			= patient_folder_path
		self.list_of_file_paths 			= self.get_list_of_file_paths()
		self.list_of_dicom_file_paths		= self.get_list_of_dicom_file_paths()
		self.list_of_dvh_paths				= self.get_list_of_dvh_paths()
		self.list_of_gamma_pass_paths		= self.get_list_of_gamma_pass_paths()
		self.dict_of_dvhs					= self.get_dict_of_dvhs()
		t3=time.time()
		#self.dict_of_dicoms				= self.get_dict_of_dicoms()
		self.models_with_dvhs				= self.get_all_models_available()
		self.structures_with_dvhs			= self.get_all_structures_available()
		self.structures_with_gamma_passes	= self.get_structures_with_gamma_passes()
		t4=time.time()
		self.dict_of_gamma_passes			= self.get_gamma_pass_dict()
		self.all_dvhs_by_model				= self.get_all_dvhs_by_model()
		self.all_dvhs_by_structure			= self.get_all_dvhs_by_structure()
		self.patient_id						= self.get_patient_id()
		self.metadata						= self.collect_metadata(xlsx_workbook)

		t5=time.time()
		self.set_default_rtdoses()
		t6=time.time()

		try:
			if self.wanted_structures == "default":
				self.wanted_structures = ["ctv", "bladder", "bladder wall", "rectum", "rectal wall", "Bladder Wall", "Rectal Wall", "Rectum", "Bladder", "CTV", "Rectal_Wall", "Bladder_Wall"]
			self.actual_structure_names = self.get_actual_structure_names(self.wanted_structures)
		except AttributeError:
			print("THERE HAS BEEN AN ATTRIBUTE ERROR")
			code_interact(globals(),locals())
		t7=time.time()

		self.set_structure_indices()
		t8=time.time()


	def get_dvh_param(self, structure, model, key) -> float:
		# in this case, model could also be "let" and is in that case in units 
		# of kev/um and describes dose averaged let

		# perhaps if patient is missing this specific DVH, we could try to create one 
		# using the makedvh program?

		if structure not in self.structures_with_dvhs:
			if structure.replace(" ","_") in self.structures_with_dvhs:
				structure = structure.replace(" ","_")
			else:
				print(self.list_of_file_paths)
				raise IndexError("This patient (patient_id = {}) does not have a DVH for model {}".format(self.patient_id,model))
		if model not in self.models_with_dvhs:
			print(self.list_of_file_paths)
			raise IndexError("This patient (patient_id = {}) does not have a DVH for model {}".format(self.patient_id,model))
		if not key:
			return
		# now select the correct dvh
		dvh = self.all_dvhs_by_model[model][structure]
		doses = dvh[:,0]
		vols  = dvh[:,1]
		if key[0].lower() == "v":
			# looking for a dose level
			if key[-1] != "%":
				if key[-2:].lower() != "gy":
					if not key[-1].isnumeric():
						raise NotImplementedError("You can only supply dose levels in Gy or %, nothing else - and you have to choose one.")
			elif key[-1] == "%":
				dose_percent = key[1:-1]
				dose_level = float(dose_percent) / 100 * np.max(doses[np.where(vols!=0)])
			if key[-2:].lower() == "gy":
				dose_level = float(key[1:-2])


			volume_level = np.interp(dose_level, doses, vols)

			return volume_level

		elif key[0].lower() == "d":
			if key[-1] != "%":
				if not key[-1].isnumeric():
					raise NotImplementedError("You can only supply volume levels in %%, nothing else. Unspecified means %% as well.")
				
			elif key[-1:].lower() == "%":
				vol_level_perc = float(key[1:-1])
			if key[-1].lower() != "%":
				vol_level_perc = float(key[1:])
				
			# code_interact(globals(), locals())

			# first need to sort volumes and doses.
			dose_level = numpy_interp(vol_level_perc, vols, doses)


			return dose_level
		else:
			raise IndexError("Supply a key as dXX or vYY with the correct suffix. Uppercase also OK.")

	def get_list_of_file_paths(self) -> list:
		list_of_file_paths = []
		for root, dirs, files in os.walk(self.patient_folder_path):
			for file in files:
				list_of_file_paths.append(os.path.join(root,file))
		return list_of_file_paths

	# def structure_volume_dict(self):
	# 	volume_dict = {}
	# 	rtstruct = ""
	# 	for path in self.list_of_dicom_file_paths:
	# 		if path.split("/")[-1][:8] == "RTSTRUCT":
	# 			rtstruct = path
	# 			break
	# 	for struct in self.structures_with_dvhs:
	# 		# find the volume of this struct.
	# 		# we need the dx, dy, dz and the coordinates.
	# 		# we sum it up by layers.




	def get_list_of_dicom_file_paths(self) -> list:
		# if filename ends with dcm it is a dicom file
		list_of_dicom_filepaths = [file for file in self.list_of_file_paths if file[-4:] == ".dcm"] 
		return list_of_dicom_filepaths
	
	def get_dict_of_dicoms(self) -> list:
		# returns a dict of pydicom read dicom files with a structure
		# dict [ dicom_filename ] = pydicom dataset
		dict_of_dicoms = {dicom_file_path : pd.read_file(dicom_file_path) for dicom_file_path in self.list_of_dicom_file_paths}
		return dict_of_dicoms

	def get_list_of_dvh_paths(self) -> list:
		# if filename ends with ".txt" and starts with "dvh-" it is a dvh
		list_of_dvh_paths = [file for file in self.list_of_file_paths if ((file[-4:] == ".txt") and (file.split("/")[-1][:4] == "dvh-"))]
		return list_of_dvh_paths

	def get_list_of_gamma_pass_paths(self) -> list:
		return [file for file in self.list_of_file_paths if (file.split("/")[-1][:10] == "gamma_pass") and (file[-4:] == ".txt")]
	
	def get_structures_with_gamma_passes(self) -> list:
		# returns a list of all structures that have gamma pass values calculated
		try:
			gamma_pass_file = [file for file in self.list_of_gamma_pass_paths if file.split("/")[-1][:10] == "gamma_pass"][0]
		except IndexError:
			print("Patient failed. No gamma pass files: {}".format(self.patient_folder_path))
			exit(0)
		structs = []
		with open(gamma_pass_file, "r") as f:
			for line in f:
				if line[:6] == "Gamma:":
					struct = line.split(":")[-1].split("=")[0].strip()
					structs.append(struct)
		return structs


	def get_gamma_pass_dict(self) -> dict:
		# returns a dict of structure:
		# gamma_pass_dict [ structure ] = dict [ criterium ] = gamma pass value in %
		gamma_pass_dict = {}
		for structure in self.structures_with_gamma_passes:
			this_struct_dict = {}
			for file in self.list_of_gamma_pass_paths:
				criterium = file.split("/")[-1].split(".")[0].split("_")[-1]
				this_crit = -1
				for i in [1,2,3]:
					if criterium == "{0}{0}".format(i):
						this_crit = i
						break
				if this_crit == -1:
					raise FileNotFoundError("Gamma pass file not found for patient.")
				# now find the value for the structure and this criterium!
				with open(file, "r") as f:
					for line in f:
						if line.split(":")[-1].split("=")[0].strip() == structure:
							gamma_pass_value = line.split(":")[1].split("=")[1].replace("%","").replace("\n","").strip()
							if not gamma_pass_value.replace(".","").isnumeric():
								gamma_pass_value = 0

							this_struct_dict[this_crit] = float(gamma_pass_value)
			gamma_pass_dict[structure] = this_struct_dict
		return gamma_pass_dict

	def get_dict_of_dvhs(self) -> dict:
		# dict with structure
		# dict [ dvh_filename ] = ndarray of shape N,2. 0th column is dose, 1st is volume percent
		dict_of_dvhs = {}
		for this_dvh_file_path in self.list_of_dvh_paths:
			this_dvh_array = self.load_dvh(this_dvh_file_path)
			dict_of_dvhs[this_dvh_file_path] = this_dvh_array
		return dict_of_dvhs

	def load_dvh(self, dvh_file_path : str) -> np.ndarray:
		dvh_array = np.loadtxt(dvh_file_path)
		return dvh_array

	def get_patient_id(self) -> str:
		return str(pd.read_file(self.list_of_dicom_file_paths[0]).PatientName)
		# return self.dict_of_dicoms[list(self.dict_of_dicoms.keys())[0]].PatientName


	def get_all_dvhs_for_given_model(self, model : str) -> dict:
		# returns dict with structure:
		# dict for model [ struct ] = ndarray of shape N,2. 0th column is dose, 1st is volume percent
		dvhs_for_given_model = {}
		for dvh_path in self.list_of_dvh_paths:
			if dvh_path.split("_")[-1].split(".")[0] == model: 
				# now we know that this DVH path is using the model we are after
				# so now, just put the DVH in the dict under this model.
				dvh_array = self.dict_of_dvhs[dvh_path]
				
				struct = ""
				for string in dvh_path.split("-")[-1].split(".")[0].split("_")[:-1]:
					struct += string + "_"
				struct = struct[:-1]  # and remove the trailing underscore

				dvhs_for_given_model[struct] = dvh_array
		return dvhs_for_given_model
	
	def get_all_dvhs_for_given_structure(self, structure : str) -> dict:
		# returns dict with structure:
		# dict for struct [ struct ] = ndarray of shape N,2. 0th column is dose, 1st is volume percent
		dvhs_for_given_structure = {}
		for dvh_path in self.list_of_dvh_paths:
			if "_".join(dvh_path.split("-")[-1].split("_")[:-1]) == structure: 
				# now we know that this DVH path is using the structure we are after
				# so now, just put the DVH in the dict under this structure.
				dvh_array = self.dict_of_dvhs[dvh_path]
				model = dvh_path.split("_")[-1].split(".")[0]
				dvhs_for_given_structure[model] = dvh_array
		return dvhs_for_given_structure
	
	def get_all_models_available(self) -> list:
		# returns a list with all different models used for dvh's
		set_of_models = set()
		for dvh_path in self.list_of_dvh_paths:
			set_of_models.add(dvh_path.split("_")[-1].split(".")[0])
		return list(set_of_models)

	def get_all_structures_available(self) -> list:
		# returns a list with all different models used for dvh's
		set_of_structures = set()
		for dvh_path in self.list_of_dvh_paths:

			# the structure name is in general something like "firstname_middle_name_last_name"
			# so the full filename would be "dvh-firstname_middle_name_last_name_model.txt"
			# So we need to split it like this

			structure_name = ""
			for string in dvh_path.split("-")[-1].split(".")[0].split("_")[:-1]:
				structure_name += string + "_"
			structure_name = structure_name[:-1]  # and remove the trailing underscore

			set_of_structures.add(structure_name)
		return list(set_of_structures)

	def get_all_dvhs_by_model(self) -> dict:
		# returns dict of all dvhs in patient
		# dict of dvhs by model [ model ] = dict for model [ struct ] = ndarray of shape N,2. 0th column is dose, 1st is volume percent
		return {model : self.get_all_dvhs_for_given_model(model) for model in self.models_with_dvhs}

	def get_all_dvhs_by_structure(self) -> dict:
		# returns dict of all dvhs in patient
		# dict of dvhs by structure [ struct ] = dict for structure [ model ] = ndarray of shape N,2. 0th column is dose, 1st is volume percent
		return {structure : self.get_all_dvhs_for_given_structure(structure) for structure in self.structures_with_dvhs}
	
	def collect_metadata(self, xlsx_workbook=None):

		if xlsx_workbook == None:
			path_to_main_patient_data_xlsx = "/media/rasmus/3tb_backup/ufhpti_all_data/main_patient_data_numerical.xlsx"
			xlsx_workbook = openpyxl.load_workbook(filename=path_to_main_patient_data_xlsx, data_only=True)
		patient_data_sheet = xlsx_workbook["Sheet1"]
		this_patient_row = -1
		# now we need to find the row with this patient id
		for row_i in range(1,2000):
			if str(patient_data_sheet["A{}".format(row_i)].value) == self.patient_id:
				this_patient_row = row_i
				break
		if this_patient_row == -1:
			print("Patient row not found in all patient data sheet for patiend id: {}.".format(self.patient_id))
			return {}
		column_ids = list(string.ascii_uppercase)
		column_ids.extend([i+b for i in column_ids for b in column_ids])
		

		column_headers = {}
		column_idx = 0
		while patient_data_sheet["{}{}".format(column_ids[column_idx],1)].value:
			column_headers[column_ids[column_idx]] = patient_data_sheet["{}{}".format(column_ids[column_idx], 1)].value
			column_idx += 1
		
		# code_interact(globals(),locals())

		patient_metadata = {}
		for column_id, column_header in column_headers.items():
			this_value = patient_data_sheet["{0}{1}".format(column_id, this_patient_row)].value
			patient_metadata[column_header] = this_value

		return patient_metadata

	def get_actual_structure_names(self, wanted_structures: list):
		if not wanted_structures:
			return None
		if self.rtstruct == None or self.rtdose_dose == None or self.rtdose_letd == None:
			self.set_default_rtdoses()

		actual_structurenames_found = False
		actual_structurenames_file = ""
		actual_structurenames_dict = {}
		for file in self.list_of_file_paths:
			if file.split("/")[-1] == "actual_structure_names.txt":
				actual_structurenames_file = file
				actual_structurenames_found = True
				break
		if actual_structurenames_found:
			with open(actual_structurenames_file, "r") as f:
				for line in f:
					key = line.split(":")[0]
					val = line.split(":")[-1].replace("\n","")
					actual_structurenames_dict[key] = val
			for wanted_struct in wanted_structures: 
				if wanted_struct not in list(actual_structurenames_dict.keys()):
					act_struct = selectStructures(self.rtstruct, [wanted_struct])[0]
					actual_structurenames_dict[wanted_struct] = act_struct
					with open(actual_structurenames_file, "a") as f:
						f.write("{}:{}\n".format(wanted_struct, act_struct))
			add_these = list(actual_structurenames_dict.values())
			for value in add_these:
				actual_structurenames_dict[value] = value
			return actual_structurenames_dict


		actual_structures = selectStructures(self.rtstruct, wanted_structures)
		writepath = ""
		writepath = writepath + self.patient_folder_path
		if not self.patient_folder_path[-1] == "/":
			writepath = writepath + "/"
		writepath = writepath + "actual_structure_names.txt"
		with open(writepath, "w") as f:
			for key, value in zip(wanted_structures, actual_structures):
				actual_structurenames_dict[key] = value
				f.write("{}:{}\n".format(key,value))
		return actual_structurenames_dict
	def set_default_rtdoses(self):
		for path in self.list_of_dicom_file_paths:
			if path.split("/")[-1][:8] == "FLK_LETd":
				self.rtdose_letd= pd.read_file(path)
				self.path_to_rtdose_letd = path
				continue
			if path.split("/")[-1][:7] == "FLK_Bio":
				self.rtdose_dose= pd.read_file(path)
				self.path_to_rtdose_dose = path
			if path.split("/")[-1][:8] == "RTSTRUCT":
				self.rtstruct= pd.read_file(path)
				self.path_to_rtstruct = path
	def dvh_above_let_value(self, let_value, structure, pydicom_rtdose="this", relative_volume=True, dose_is_let = False, delta_dose = 0.1):
		import time
		t00 = time.time()
		if self.rtdose_letd == None:
			self.rtdose_letd = pd.read_file(self.rtdose_letd)
		if self.rtdose_dose == None:
			self.rtdose_dose = pd.read_file(self.rtdose_dose)
		if self.rtstruct == None:
			self.rtstruct = pd.read_file(self.rtstruct)
		t0 = time.time()
		usethis_rtdose = pydicom_rtdose
		if pydicom_rtdose=="this":
			usethis_rtdose = self.rtdose_dose

		if structure not in self.actual_structure_names.values() and structure in self.actual_structure_names.keys():
			structure_name = self.actual_structure_names[structure].strip()
		elif structure in self.actual_structure_names.values():
			structure_name = structure

		organ_inds = self.structure_indices[self.actual_structure_names[structure_name]]
		t1 = time.time()
		dosegrid1 = usethis_rtdose.pixel_array * usethis_rtdose.DoseGridScaling
		letdgrid1 = self.rtdose_letd.pixel_array * self.rtdose_letd.DoseGridScaling

		dosegrid = dosegrid1
		letdgrid = letdgrid1
		if dose_is_let:
			dosegrid = letdgrid1
			letdgrid = dosegrid1

		dosegrid_in_organ = dosegrid[organ_inds]
		letdgrid_in_organ = letdgrid[organ_inds]
		t2 = time.time()
		dosegrid_in_organ_above_let = dosegrid_in_organ[np.where(letdgrid_in_organ>=let_value)]

		total_inds = np.prod(dosegrid_in_organ.shape)
		dvh_doses = []
		dvh_indic = []
		t3 = time.time()
		if np.prod(dosegrid_in_organ_above_let.shape) == 0:
			return np.array([[0,0],[0,0]])
		t4 = time.time()
		# for dos in np.arange(0, np.max(dosegrid_in_organ_above_let), delta_dose):
		for dos in np.arange(0, 120, delta_dose):
			dvh_doses.append(dos)
			dvh_indic.append( np.prod( (dosegrid_in_organ_above_let[np.where(dosegrid_in_organ_above_let>=dos)]).shape ) )
		t5 = time.time()
		dx, dy = self.rtdose_dose.PixelSpacing
		dz = self.rtdose_dose.GridFrameOffsetVector[1] - self.rtdose_dose.GridFrameOffsetVector[0]
		volume_per_voxel = dx * dy * dz / 10 / 10 / 10
		dvh_volume = np.array(dvh_indic) * volume_per_voxel
		if relative_volume:
			dvh_volume = np.array(dvh_indic) / total_inds * 100
		dvh_doses = np.array(dvh_doses)
		dvh = np.array([dvh_doses, dvh_volume])
		# print("t0-t00 = {} s".format(t0-t00))
		# print("t1-t0 = {} s".format(t1-t0))
		# print("t2-t1 = {} s".format(t2-t1))
		# print("t3-t2 = {} s".format(t3-t2))
		# print("t4-t3 = {} s".format(t4-t3))
		# print("t5-t4 = {} s".format(t5-t4))
		# print("total time: {} s".format(t5-t00))
		return dvh.T
	
	def calculate_dvh_parameter(self, structure : str, dvh_parameter : str, **kwargs) -> float:
		# Parsing string.
		# Is it asking for a volume or a dose/let?
		match dvh_parameter[0]:
			case "V":
				# Volume case
				# Generalized looks like: V_X_[%,Gy]((_Y_[%,kev/um])) -- (()) is optional.
				# Example: "V_20_Gy", "V_30_%", "V_10_Gy_2_kev/um", "V_50_Gy_5_%"

				return self.calculate_dvh_volume(structure, dvh_parameter)
			case "L":
				# LET case
				pass
			case "D":
				# Dose case
				p = dvh_parameter.split("_")[1]
				dvh = self.dvh_above_let_value(0,structure, **kwargs)
				doses = dvh[:,0]
				vols = dvh[:,1]
				return numpy_interp(p, vols, doses)

	def calculate_mean_let_above_dose(self,structure, dose):

		if structure not in self.actual_structure_names.values() and structure in self.actual_structure_names.keys():
			structure_name = self.actual_structure_names[structure].strip()
		elif structure in self.actual_structure_names.values():
			structure_name = structure
		else:
			raise ValueError("The supplied structure is not found for this patient. You supplied {} and for this patient (patient_ID = {}) the following are valid (both keys and values): {}".format(structure, self.patient_id,self.actual_structure_names))

		if hasattr(self, "{}_indices".format(structure_name)):
			structure_indices = getattr(self, "{}_indices".format(structure_name))
		else:
			structure_indices = self.get_indices_in_structure(structure_name)
			setattr(self, "{}_indices".format(structure_name), structure_indices)

		dose_array = self.rtdose_dose.pixel_array * self.rtdose_dose.DoseGridScaling
		letd_array = self.rtdose_letd.pixel_array * self.rtdose_letd.DoseGridScaling
		dose_in_structure = dose_array[structure_indices]
		letd_in_structure = letd_array[structure_indices]
		letd_above_threshold = letd_in_structure[dose_in_structure > float(dose)]
		if np.prod(letd_above_threshold.shape) == 0:
			return 0
		return np.mean(letd_above_threshold)
	
	def calculate_dvh_volume(self, structure : str, dvh_parameter : str, percentage=True) -> float:
		# Volume case
		# Generalized looks like: V_X_[%,Gy]_Y_[%,kev/um] -- You can omit either dose or LET requirement.
		# Examples: "V_20_Gy", "V_30_%", "V_10_Gy_2_kev/um", "V_50_Gy_5_%"
		# 			"V_2_kev/um" ... 
		split_param = dvh_parameter.split("_")
		if len(split_param) not in [3,5]:
			raise ValueError("DVH volume parameter not valid. It should have 3 or 5 values seperated by underscores V_X_[%,Gy]_Y_[%,kev/um]. You supplied: {}".format(dvh_parameter))
		if structure not in self.actual_structure_names.values() and structure in self.actual_structure_names.keys():
			structure_name = self.actual_structure_names[structure].strip()
		elif structure in self.actual_structure_names.values():
			structure_name = structure
		else:
			raise ValueError("The supplied structure is not found for this patient. You supplied {} and for this patient (patient_ID = {}) the following are valid (both keys and values): {}".format(structure, self.patient_id,self.actual_structure_names))
		if hasattr(self, "{}_indices".format(structure_name)):
			structure_indices = getattr(self, "{}_indices".format(structure_name))
		else:
			structure_indices = self.get_indices_in_structure(structure_name)
			setattr(self, "{}_indices".format(structure_name), structure_indices)
		match len(split_param):
			case 3:
				# "V_20_Gy", "V_30_%" "V_2_kev/um" and so on
				match split_param[2]:
					case "Gy":
						# Load dosegrid in structure
						dose_array = self.rtdose_dose.pixel_array * self.rtdose_dose.DoseGridScaling
						dose_in_structure = dose_array[structure_indices]
						dose_above_threshold = dose_in_structure[dose_in_structure > float(split_param[1])]
						volume_fraction = np.prod(np.shape(dose_above_threshold)) / np.prod(np.shape(dose_in_structure))
						if percentage == True:
							return 100*volume_fraction
						elif percentage == False:
							return volume_fraction
					case "%": # assumes dose
						raise NotImplementedError("This has not been implemented yet.")
						pass
					case "kev/um":
						# Load dosegrid in structure
						letd_array = self.rtdose_letd.pixel_array * self.rtdose_letd.DoseGridScaling
						letd_in_structure = letd_array[structure_indices]
						letd_above_threshold = letd_in_structure[letd_in_structure > float(split_param[1])]
						volume_fraction = np.prod(np.shape(letd_above_threshold)) / np.prod(np.shape(letd_in_structure))
						if percentage == True:
							return 100*volume_fraction
						elif percentage == False:
							return volume_fraction
					case other:
						raise ValueError("The DVH parameter supplied is not valid. You supplied {}".format(dvh_parameter))
			case 5:
				# "V_10_Gy_2_kev/um" cases and so on
				match (split_param[2], split_param[4]):
					case ("Gy","kev/um"):
						dose_array = self.rtdose_dose.pixel_array * self.rtdose_dose.DoseGridScaling
						letd_array = self.rtdose_letd.pixel_array * self.rtdose_letd.DoseGridScaling
						dose_in_structure = dose_array[structure_indices]
						letd_in_structure = letd_array[structure_indices]

						letd_threshold = float(split_param[3])
						dose_threshold = float(split_param[1])
						letd_in_structure_above_dose_threshold = letd_in_structure[dose_in_structure > dose_threshold]

						letd_array_in_structure_above_dose_and_letd_threshold = letd_in_structure_above_dose_threshold[letd_in_structure_above_dose_threshold > letd_threshold]
						voxels_above_dose_and_letd_threshold = np.prod(np.shape(letd_array_in_structure_above_dose_and_letd_threshold))
						volume_fraction = voxels_above_dose_and_letd_threshold / np.prod(np.shape(dose_in_structure))
						
						if percentage == True:
							return 100*volume_fraction
						elif percentage == False:
							return volume_fraction
					case ("%","kev/um"):
						raise NotImplementedError("This has not been implemented yet.")
					case ("Gy","%"):
						raise NotImplementedError("This has not been implemented yet.")
					case ("%","%"):
						raise NotImplementedError("This has not been implemented yet.")
	
	def set_unkelbach_rbe_weighed_dose(self, **kwargs):
		letd_grid = self.rtdose_letd.pixel_array * self.rtdose_letd.DoseGridScaling
		dose_grid = self.rtdose_dose.pixel_array * self.rtdose_dose.DoseGridScaling
		rbe = var_rbe_calculator(dose_grid, letd_grid, "unkelbach", **kwargs)
		rbe_weighed_dose = dose_grid * rbe / 1.1
		rbe_rtdose = copy.deepcopy(self.rtdose_dose)
		dgs = np.max(rbe_weighed_dose) / (2**16 -1)
		rbe_weighed_dose = rbe_weighed_dose / dgs

		rbe_rtdose.BitsAllocated = 16
		rbe_rtdose.BitsStored = 16
		rbe_rtdose.HighBit = 15
		rbe_rtdose.DoseGridScaling = dgs
		rbe_rtdose.PixelData = rbe_weighed_dose.astype(np.uint16).tobytes()


		self.unkelbach_rbe_weighed_dose = rbe_rtdose
	
	def set_structure_indices(self): # sets rectum and bladder structures
		indices = {}
		bladder = self.get_indices_in_structure(self.actual_structure_names["Bladder"])
		bladder_wall = self.get_indices_in_structure(self.actual_structure_names["Bladder Wall"])
		rectum  = self.get_indices_in_structure(self.actual_structure_names["Rectum"])
		rectal_wall  = self.get_indices_in_structure(self.actual_structure_names["Rectal Wall"])
		CTV  = self.get_indices_in_structure(self.actual_structure_names["CTV"])
		indices[self.actual_structure_names["Bladder"]] = bladder
		indices[self.actual_structure_names["Bladder Wall"]] = bladder_wall
		indices[self.actual_structure_names["Rectum"]] = rectum
		indices[self.actual_structure_names["Rectal Wall"]] = rectal_wall
		indices[self.actual_structure_names["CTV"]] = CTV
		self.structure_indices = indices

	def get_indices_in_structure(self, structure):
		if structure not in self.actual_structure_names.values() and structure in self.actual_structure_names.keys():
			structure_name = self.actual_structure_names[structure].strip()
		elif structure in self.actual_structure_names.values():
			structure_name = structure
		else:
			raise ValueError("The supplied structure is not found for this patient. You supplied {} and for this patient (patient_ID = {}) the following are valid (both keys and values): {}".format(structure, self.patient_id,self.actual_structure_names))
		mask_image = -1
		mask_path = ""
		# Check if patient folder has the wanted structure as a .nrrd file
		if hasattr(self, "list_of_file_paths"):
			mask_path = [a for a in self.list_of_file_paths if a.split("/")[-1][:-5] == structure_name]
			# If no masks found could be due to slashes in structure name looking like slashes in 
			# mask paths
			if mask_path == []:
				if "/" in structure_name:
					search_for_this_name = structure_name.split("/")[-1]
					mask_path = [a for a in self.list_of_file_paths if a.split("/")[-1][:-5] == search_for_this_name]

					
			if len(mask_path) == 1:
				mask_path = mask_path[0]
			if type(mask_path) == list and len(mask_path) > 1:
				# We need to pick one in a clever way.
				# Let us pick the one with the fewest folders leading to it
				number_of_dirs = [len(p.split("/")) for p in mask_path]
				if len(np.unique(number_of_dirs)) == 1:
					mask_path=mask_path[0]
				else:
					mask_path=mask_path[np.argmin(number_of_dirs)]
		if mask_path != "" and mask_path != []:
			mask_images = [sitk.ReadImage(mask_path)]
		else:
			print("We could not find this structure mask.")
			raise ValueError("Structure mask for {} not found for patient id: {}".format(structure_name, self.patient_id))
		# This can also be done using pyplastimatch, should maybe be converted.
		if is_tool("plastimatch"):
			# cp the structure file with some things removed

			# list of temp rtstructs []
			# for i in range 1 : max(length of contoursequence over 1 CT UID) // this will be the maximum number of contours in a slice
				# make a copy of the rtstruct
				# Now we only keep the i'th contoursequence per CT UID
				# If we delete the only one we remove the entire CT UID slice
				# list of temp rtstructs <- save this as a temporary rtstruct file
			# now we have a list of temp rtstructs
			# use plastimatch to mask each individual one
			# for each structure check how many of the mask files have it inside.
			# If it is an even number it is not inside
			# If odd number it is inside
			# 

			temporary_rtstructs = []
			# first find the ReferencedROINumber
			structure_index = -1
			max_number_of_contours_in_one_slice = -1


			# For some reason this needs to be done, otherwise we end up with weakrefs
			# Dont think it is too memory expensive
			rtstruct = copy.deepcopy(self.rtstruct) 

			for item in rtstruct.StructureSetROISequence:
				if item.ROIName == structure_name:
					structure_index = item.ROINumber
					break
			# Now find the correct ROIContourSequence
			delete_these_rois = []
			for iii, ROIcontourSequence in enumerate(rtstruct.ROIContourSequence):
				if ROIcontourSequence.ReferencedROINumber != structure_index:
					delete_these_rois.append(iii)
					continue
				# This is now the correct one
				uids = [a.ContourImageSequence[0].ReferencedSOPInstanceUID for a in ROIcontourSequence.ContourSequence]
				max_number_of_contours_in_one_slice = max([uids.count(i) for i in uids])

			# In case there is no need of this duplication process
			# Then this structure is verified non hollow and we can use
			if max_number_of_contours_in_one_slice != 1:

				if max_number_of_contours_in_one_slice == -1:
					print("Something is very wrong here.")
					raise ValueError("Problem with ROI Contour Sequence in the RTSTRUCT file.")
				# print("We are creating {} new rtstructs.".format(max_number_of_contours_in_one_slice))
				for i in range(max_number_of_contours_in_one_slice):
					temporary_rtstructs.append(copy.deepcopy(rtstruct))
				
				for i, ds in enumerate(temporary_rtstructs):
					for index in delete_these_rois[::-1]:
						del ds.ROIContourSequence[index]
					for ROIcontourSequence in ds.ROIContourSequence:
						if ROIcontourSequence.ReferencedROINumber != structure_index:
							continue
						# print("We started with {} contours in this one. (we are keeping the {}th)".format(len(ROIcontourSequence.ContourSequence),i))
						current_uid = ROIcontourSequence.ContourSequence[0].ContourImageSequence[0].ReferencedSOPInstanceUID
						instances = 0
						delete_these = []
						for j, contourSequence in enumerate(ROIcontourSequence.ContourSequence):
							if contourSequence.ContourImageSequence[0].ReferencedSOPInstanceUID != current_uid:
								instances = 0
								current_uid = contourSequence.ContourImageSequence[0].ReferencedSOPInstanceUID
							if instances != i:
								delete_these.append(j)
							# print("instances variable = {}".format(instances))
							instances += 1
						# Now we have looped through all contourSequences and have logged the ones not need
						# Now we just delete those ones because this is a temporary RTSTRUCT.
						# We delete from behind / the largest index first to preserve order
						for index in delete_these[::-1]:
							del ROIcontourSequence.ContourSequence[index]
						# print("We are ending with {} contours in this one. (we kept the {}th)".format(len(ROIcontourSequence.ContourSequence),i))
				
							


				with tempfile.TemporaryDirectory() as temp_dir:
					# save each rtstruct temporarily
					filenames = []
					for i,ds in enumerate(temporary_rtstructs):
						# Since the first one will be the outer shell, 
						# no need to do this as this has already been done
						if i == 0:
							continue
						filename = "temporary_rtstruct_{}_{}.dcm".format(structure_name.replace(" ","_"), i)
						filenames.append(filename)
						pd.dcmwrite(temp_dir+"/"+filename, ds)
					
					for i,ds in enumerate(temporary_rtstructs):
						# Since the first one will be the outer shell, 
						# no need to do this as this has already been done
						if i == 0:
							continue
						filename = temp_dir+"/"+"temporary_rtstruct_{}_{}.dcm".format(structure_name.replace(" ","_"), i)
						command = "plastimatch convert --input "
						command += "\"{}\" ".format(filename)
						command += "--output-prefix {} --prefix-format nrrd ".format(temp_dir+"/"+str(i), temp_dir+"/"+str(i))
						command += "--input-dose-img \"{}\"".format(self.path_to_rtdose_dose) + " > /dev/null 2> /dev/null"
						
						subprocess.run(command, shell=True)
					
					mask_paths = [temp_dir+"/"+str(i)+"/"+structure_name+".nrrd" for i in range(1,len(temporary_rtstructs))]

					mask_images = mask_images + [sitk.ReadImage(mask_path) for mask_path in mask_paths]
		
		mask_arrays = []
		for mask_image in mask_images:
			if mask_image != -1:
				dose_transform = list(self.rtdose_dose.ImageOrientationPatient) 
				dose_transform += list(self.rtdose_dose.ImagePositionPatient)
				dose_transform = np.array(dose_transform)
				dose_transform = dose_transform.reshape((3, 3))

				direction_cosine_matrix = list(dose_transform.flatten())
				mask_image.SetDirection(direction_cosine_matrix)
				mask_array = sitk.GetArrayFromImage(mask_image) # 1s inside structure, 0s outside
				mask_arrays.append(mask_array)
		
		# the mask arrays are 1 inside the contours.
		# if it is inside 2, then it is really outside, and 4 ans so on.
		# Opposite for odd numbers
		final_mask_array = sum(mask_arrays)%2
		return np.where(final_mask_array==1)

