import numpy as np
from scipy.integrate import quad
from .patient import Patient, Cohort
from .helpers import eud_calculator_dose_array, find_struct_indices_in_rtdose, code_interact
import pydicom as pd

def calculate_lkb(eud, d50, m):
	t = (eud - d50) / (m * d50)
	front_factor = 1/np.sqrt(2* np.pi)
	def function_to_integrate(x):
		return np.exp(-1/2*x*x)
	integral = quad(function_to_integrate, -np.Infinity, t)
	ntcp = front_factor * integral[0]
	return ntcp



def calculate_ntcp(patient : Patient, structure_of_interest, lkb_params, rbe_weighed_dose_model = "") -> float:

	n,m,d50 = lkb_params

	rtdose = patient.rtdose_dose
	if rbe_weighed_dose_model != "":
		match rbe_weighed_dose_model:
			case "unkelbach":
				if hasattr(patient, "unkelbach_rbe_weighed_dose"):
					rtdose = patient.unkelbach_rbe_weighed_dose
				else:
					patient.set_unkelbach_rbe_weighed_dose()
					rtdose = patient.unkelbach_rbe_weighed_dose
			case other:
				pass

	dosegrid = rtdose.pixel_array * rtdose.DoseGridScaling


	structure_name = patient.actual_structure_names[structure_of_interest]
	structure_indices = find_struct_indices_in_rtdose(patient.rtstruct, rtdose, structure_name)

	dose_array_in_structure = dosegrid[structure_indices]

	if np.isnan(np.sum(dose_array_in_structure)):
		print("Dosegridscaling is nan")
		code_interact(globals(), locals())

	eud_in_structure = eud_calculator_dose_array(dose_array_in_structure, n)
	lkb_ntcp = calculate_lkb(eud_in_structure, d50, m)

	return lkb_ntcp


def calculate_mean_let_over_threshold_rectum(patient : Patient, structure_of_interest, dose_threshold) -> float:
	flk_dicom_paths = [s for s in patient.list_of_dicom_file_paths if s.split("/")[-1][:3] == "FLK"]
	flk_biodose_dicom_path = [s for s in flk_dicom_paths if s.split("/")[-1][:12] == "FLK_Bio-dose"][0]
	flk_letd_dicom_path = [s for s in flk_dicom_paths if s.split("/")[-1][:8] == "FLK_LETd"][0]

	flk_biodose_dicom = pd.read_file(flk_biodose_dicom_path)
	flk_letd_dicom = pd.read_file(flk_letd_dicom_path)

	dosegrid = flk_biodose_dicom.pixel_array * flk_biodose_dicom.DoseGridScaling
	letdgrid = flk_letd_dicom.pixel_array * flk_letd_dicom.DoseGridScaling


	structure_name = patient.actual_structure_names[structure_of_interest]
	structure_indices = find_struct_indices_in_rtdose(patient.rtstruct, flk_biodose_dicom, structure_name)

	letd_array_in_structure = letdgrid[structure_indices]
	dose_array_in_structure = dosegrid[structure_indices]


	if np.isnan(np.sum(letd_array_in_structure)):
		print("Dosegridscaling is nan in letd")
		code_interact(globals(), locals())

	letd_array_in_structure = letd_array_in_structure[dose_array_in_structure>dose_threshold]
	dose_array_in_structure = dose_array_in_structure[dose_array_in_structure>dose_threshold]
	


	return np.mean(letd_array_in_structure)


def calculate_volume_above_let_and_dose_rel(patient : Patient, structure_of_interest, dose_threshold, let_threshold) -> float:
	flk_dicom_paths = [s for s in patient.list_of_dicom_file_paths if s.split("/")[-1][:3] == "FLK"]
	flk_biodose_dicom_path = [s for s in flk_dicom_paths if s.split("/")[-1][:12] == "FLK_Bio-dose"][0]
	flk_letd_dicom_path = [s for s in flk_dicom_paths if s.split("/")[-1][:8] == "FLK_LETd"][0]

	flk_biodose_dicom = pd.read_file(flk_biodose_dicom_path)
	flk_letd_dicom = pd.read_file(flk_letd_dicom_path)

	dosegrid = flk_biodose_dicom.pixel_array * flk_biodose_dicom.DoseGridScaling
	letdgrid = flk_letd_dicom.pixel_array * flk_letd_dicom.DoseGridScaling


	structure_name = patient.actual_structure_names[structure_of_interest]
	structure_indices = find_struct_indices_in_rtdose(patient.rtstruct, flk_biodose_dicom, structure_name)

	letd_array_in_structure = letdgrid[structure_indices]
	dose_array_in_structure = dosegrid[structure_indices]
	total_number_of_voxels = np.prod(dose_array_in_structure.shape)

	if np.isnan(np.sum(letd_array_in_structure)):
		print("Dosegridscaling is nan in letd")
		code_interact(globals(), locals())

	letd_array_in_structure = letd_array_in_structure[dose_array_in_structure>dose_threshold]
	dose_array_in_structure = dose_array_in_structure[dose_array_in_structure>dose_threshold]
	

	letd_array_in_structure_above_let_threshold = letd_array_in_structure[letd_array_in_structure >= let_threshold]
	number_of_voxels = np.prod(letd_array_in_structure_above_let_threshold.shape)
	rel_volume = number_of_voxels / total_number_of_voxels * 100
	return rel_volume



def calculate_volume_above_let_and_dose(patient : Patient, structure_of_interest, dose_threshold, let_threshold) -> float:
	flk_dicom_paths = [s for s in patient.list_of_dicom_file_paths if s.split("/")[-1][:3] == "FLK"]
	flk_biodose_dicom_path = [s for s in flk_dicom_paths if s.split("/")[-1][:12] == "FLK_Bio-dose"][0]
	flk_letd_dicom_path = [s for s in flk_dicom_paths if s.split("/")[-1][:8] == "FLK_LETd"][0]

	flk_biodose_dicom = pd.read_file(flk_biodose_dicom_path)
	flk_letd_dicom = pd.read_file(flk_letd_dicom_path)

	dosegrid = flk_biodose_dicom.pixel_array * flk_biodose_dicom.DoseGridScaling
	letdgrid = flk_letd_dicom.pixel_array * flk_letd_dicom.DoseGridScaling


	structure_name = patient.actual_structure_names[structure_of_interest]
	structure_indices = find_struct_indices_in_rtdose(patient.rtstruct, flk_biodose_dicom, structure_name)

	letd_array_in_structure = letdgrid[structure_indices]
	dose_array_in_structure = dosegrid[structure_indices]


	if np.isnan(np.sum(letd_array_in_structure)):
		print("Dosegridscaling is nan in letd")
		code_interact(globals(), locals())

	letd_array_in_structure = letd_array_in_structure[dose_array_in_structure>dose_threshold]
	dose_array_in_structure = dose_array_in_structure[dose_array_in_structure>dose_threshold]
	
	dx,dy = flk_biodose_dicom.PixelSpacing
	dz = flk_biodose_dicom.SliceThickness
	if (type(dz) is not float) or (type(dz) is not int):
		dz = flk_biodose_dicom.GridFrameOffsetVector[1]-flk_biodose_dicom.GridFrameOffsetVector[0]

	voxel_size = dx * dy * dz

	letd_array_in_structure_above_let_threshold = letd_array_in_structure[letd_array_in_structure >= let_threshold]
	number_of_voxels = np.prod(letd_array_in_structure_above_let_threshold.shape)
	abs_volume = number_of_voxels * voxel_size
	return abs_volume


def calculate_rectal_volume(patient: Patient, structure_of_interest):
	flk_dicom_paths = [s for s in patient.list_of_dicom_file_paths if s.split("/")[-1][:3] == "FLK"]
	flk_biodose_dicom_path = [s for s in flk_dicom_paths if s.split("/")[-1][:12] == "FLK_Bio-dose"][0]

	flk_biodose_dicom = pd.read_file(flk_biodose_dicom_path)

	dosegrid = flk_biodose_dicom.pixel_array * flk_biodose_dicom.DoseGridScaling

	structure_name = patient.actual_structure_names[structure_of_interest]
	structure_indices = find_struct_indices_in_rtdose(patient.rtstruct, flk_biodose_dicom, structure_name)

	dose_array_in_structure = dosegrid[structure_indices]

	total_volume = np.prod(dose_array_in_structure.shape)

	dx,dy = flk_biodose_dicom.PixelSpacing
	dz = flk_biodose_dicom.SliceThickness
	if (type(dz) is not float) or (type(dz) is not int):
		dz = flk_biodose_dicom.GridFrameOffsetVector[1]-flk_biodose_dicom.GridFrameOffsetVector[0]

	voxel_volume = dx*dy*dz

	return voxel_volume * total_volume / 1000


def calculate_organ_v_let(patient: Patient, structure_of_interest, let_cutoff):
	flk_dicom_paths = [s for s in patient.list_of_dicom_file_paths if s.split("/")[-1][:3] == "FLK"]
	flk_letd_dicom_path = [s for s in flk_dicom_paths if s.split("/")[-1][:8] == "FLK_LETd"][0]

	flk_letd_dicom = pd.read_file(flk_letd_dicom_path)

	letdgrid = flk_letd_dicom.pixel_array * flk_letd_dicom.DoseGridScaling

	structure_name = patient.actual_structure_names[structure_of_interest]
	structure_indices = find_struct_indices_in_rtdose(patient.rtstruct, flk_letd_dicom, structure_name)


	letd_array_in_structure = letdgrid[structure_indices]

	total_volume = np.prod(letd_array_in_structure.shape)

	dx,dy = flk_letd_dicom.PixelSpacing
	dz = flk_letd_dicom.SliceThickness
	if (type(dz) is not float) or (type(dz) is not int):
		dz = flk_letd_dicom.GridFrameOffsetVector[1]-flk_letd_dicom.GridFrameOffsetVector[0]

	voxel_volume = dx*dy*dz

	v_letd = np.prod(letd_array_in_structure[letd_array_in_structure>=let_cutoff].shape)
	rel_vol = v_letd/total_volume * 100
	return rel_vol




def calculate_rectal_v75gy(patient: Patient, structure_of_interest, absoluteVolume=False):
	flk_dicom_paths = [s for s in patient.list_of_dicom_file_paths if s.split("/")[-1][:3] == "FLK"]
	flk_biodose_dicom_path = [s for s in flk_dicom_paths if s.split("/")[-1][:12] == "FLK_Bio-dose"][0]

	flk_biodose_dicom = pd.read_file(flk_biodose_dicom_path)

	dosegrid = flk_biodose_dicom.pixel_array * flk_biodose_dicom.DoseGridScaling

	structure_name = patient.actual_structure_names[structure_of_interest]
	structure_indices = find_struct_indices_in_rtdose(patient.rtstruct, flk_biodose_dicom, structure_name)

	dose_array_in_structure = dosegrid[structure_indices]
	dx,dy = flk_biodose_dicom.PixelSpacing
	dz = flk_biodose_dicom.SliceThickness
	if (type(dz) is not float) or (type(dz) is not int):
		dz = flk_biodose_dicom.GridFrameOffsetVector[1]-flk_biodose_dicom.GridFrameOffsetVector[0]

	voxel_volume = dx*dy*dz

	if not absoluteVolume:
		original_v75gy = len(dose_array_in_structure[dose_array_in_structure>=75]) / len(dose_array_in_structure) * 100
	else:
		original_v75gy = len(dose_array_in_structure[dose_array_in_structure>=75]) * voxel_volume / 1000
		
	return original_v75gy
def calculate_relative_change_in_v75gy_when_applying_lwd(patient: Patient, structure_of_interest, dose_threshold):
	flk_dicom_paths = [s for s in patient.list_of_dicom_file_paths if s.split("/")[-1][:3] == "FLK"]
	flk_biodose_dicom_path = [s for s in flk_dicom_paths if s.split("/")[-1][:12] == "FLK_Bio-dose"][0]
	flk_letd_dicom_path = [s for s in flk_dicom_paths if s.split("/")[-1][:8] == "FLK_LETd"][0]

	flk_biodose_dicom = pd.read_file(flk_biodose_dicom_path)
	flk_letd_dicom = pd.read_file(flk_letd_dicom_path)

	dosegrid = flk_biodose_dicom.pixel_array * flk_biodose_dicom.DoseGridScaling
	letdgrid = flk_letd_dicom.pixel_array * flk_letd_dicom.DoseGridScaling

	structure_name = patient.actual_structure_names[structure_of_interest]
	structure_indices = find_struct_indices_in_rtdose(patient.rtstruct, flk_biodose_dicom, structure_name)

	letd_array_in_structure = letdgrid[structure_indices]
	dose_array_in_structure = dosegrid[structure_indices]


	lwd_rbe = 1+0.055 * letd_array_in_structure
	lwd_dose_in_structure = lwd_rbe / 1.1 * dose_array_in_structure

	original_v75gy = len(dose_array_in_structure[dose_array_in_structure>=75]) / len(dose_array_in_structure)
	lwd_rbe_v75gy = len(lwd_dose_in_structure[lwd_dose_in_structure>=75]) / len(lwd_dose_in_structure)

	return lwd_rbe_v75gy / original_v75gy * 100

def calculate_let_percentage_over_threshold_rectum(patient : Patient, structure_of_interest, dose_threshold, percentage) -> float:
	flk_dicom_paths = [s for s in patient.list_of_dicom_file_paths if s.split("/")[-1][:3] == "FLK"]
	flk_biodose_dicom_path = [s for s in flk_dicom_paths if s.split("/")[-1][:12] == "FLK_Bio-dose"][0]
	flk_letd_dicom_path = [s for s in flk_dicom_paths if s.split("/")[-1][:8] == "FLK_LETd"][0]

	flk_biodose_dicom = pd.read_file(flk_biodose_dicom_path)
	flk_letd_dicom = pd.read_file(flk_letd_dicom_path)

	dosegrid = flk_biodose_dicom.pixel_array * flk_biodose_dicom.DoseGridScaling
	letdgrid = flk_letd_dicom.pixel_array * flk_letd_dicom.DoseGridScaling


	structure_name = patient.actual_structure_names[structure_of_interest]
	structure_indices = find_struct_indices_in_rtdose(patient.rtstruct, flk_biodose_dicom, structure_name)

	letd_array_in_structure = letdgrid[structure_indices]
	dose_array_in_structure = dosegrid[structure_indices]


	if np.isnan(np.sum(letd_array_in_structure)):
		print("Dosegridscaling is nan in letd")
		code_interact(globals(), locals())

	letd_array_in_structure = letd_array_in_structure[dose_array_in_structure>dose_threshold]
	dose_array_in_structure = dose_array_in_structure[dose_array_in_structure>dose_threshold]
	

	return np.percentile(letd_array_in_structure,percentage)