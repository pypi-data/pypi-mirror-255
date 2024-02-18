import pymedphys as pmp
import readline
import rlcompleter
import code
import numpy as np
from scipy.spatial import Delaunay
import pydicom as pd
import numpy as np
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
from numba import jit
from shutil import which
import subprocess
import os
import tempfile
import string


def get_patient_metadata(patient_data_sheet, patient_id):
	this_patient_row = -1
	# now we need to find the row with this patient id
	for row_i in range(1,1500):
		if str(patient_data_sheet["A{}".format(row_i)].value) == patient_id:
			this_patient_row = row_i
			break
	if this_patient_row == -1:
		print("Patient row not found in all patient data sheet for patiend id: {}.".format(patient_id))
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

def var_rbe_calculator(dose, let, model = "unkelbach", alphabeta_grid=[], c=0.04):
	if model.lower() == "unkelbach":
		rbe = 1 + c * let
		return rbe

def getROIContourSequence(structure, refROINumber):
	"""
	Returns the ROIContourSequence for a given ROI number of the structure given.
	"""
	for seq in structure.ROIContourSequence:	
		if refROINumber == seq.ReferencedROINumber:
			return seq

def ROIName2Number(struct,ROIName):
	return {a.ROIName : a.ROINumber for a in struct.StructureSetROISequence}[ROIName]
def getROIContourSequenceXyz(structure, refROINumber):
	"""
	Returns the contour xyz data in format [[xi,yi,zi]] for the given structure ROI number
	"""
	ROIContourSequence = getROIContourSequence(structure, refROINumber)
	xyz = []
	for seq in ROIContourSequence.ContourSequence:
		for j in range(int(len(seq.ContourData)/3)):
			x = seq.ContourData[3*j+0]
			y = seq.ContourData[3*j+1]
			z = seq.ContourData[3*j+2]
			xyz.append([x,y,z])
	return xyz


def make_coord_array(rtdose: pd.Dataset):
	x0,y0,z0 = rtdose.ImagePositionPatient
	dx, dy = rtdose.PixelSpacing
	dz = rtdose.SliceThickness
	if type(dz) != float:
		dz = rtdose.GridFrameOffsetVector[1] - rtdose.GridFrameOffsetVector[0]
	nx = rtdose.Columns; ny = rtdose.Rows;	nz = rtdose.NumberOfFrames

	x = np.linspace(x0+dx/2,x0+nx*dx-dx/2,nx)
	y = np.linspace(y0+dy/2,y0+ny*dy-dy/2,ny)
	z = np.linspace(z0,z0+(nz-1)*dz,nz)
	newgrid = np.array(np.meshgrid(x,y,z,indexing="ij")).T
	return newgrid

def is_tool(name):
    """Check whether `name` is on PATH and marked as executable."""

    # from whichcraft import which

    return which(name) is not None

def find_struct_indices_in_rtdose(rtstruct: pd.Dataset, rtdose: pd.Dataset, structure_name: str):

	# Currently has an error!!!
	# Should be swapped for a better implementation which doesn't overestimate the volume of structures.

	struct_contourXyz = getROIContourSequenceXyz(rtstruct,ROIName2Number(rtstruct, structure_name))
	coord_grid = make_coord_array(rtdose)
	def make_delaunay(contourXYZ):
		return Delaunay(contourXYZ)
	struct_delaunay = make_delaunay(struct_contourXyz)
	# structname_inds = np.where( (struct_delaunay.find_simplex(coord_grid) >= 0) == True) 
	structname_inds = np.where( (struct_delaunay.find_simplex(coord_grid) > 0) == True) 
	return structname_inds



def code_interact(globals, locals):
	vars = globals
	vars.update(locals)
	readline.set_completer(rlcompleter.Completer(vars).complete)
	readline.parse_and_bind("tab: complete")
	code.InteractiveConsole(vars).interact()	

def printStructures(structure):
	print("There are the following structures available in your RTSTRUCT:")
	for i, name in enumerate([a.ROIName for a in structure.StructureSetROISequence]):
		print("{0:2}: {1}".format(i,name))

def selectStructures(structure, selections):
	"""
		This function takes an RTSTRUCT and a list of wanted structure names
		It then tries to find them automagically based on their names,
		but if unable it will prompt the user for help.
		If one is not available the user can enter this
		and the function will return with the ones found.
		The function returns a list of strings corresponding to the structurenames.
	"""
	iii = -1
	for i, el in enumerate(selections):
		if el == "body":
			iii = i
			break
	if not iii == -1:
		del selections[iii]

	return_list = ["NOT_FOUND_YET"] * len(selections)
	# first we try to find the correct structures. Then only ask for what we need.
	listOfStructures = [a.ROIName for a in structure.StructureSetROISequence]
	for j,sel in enumerate(selections):
		if sel.lower() in [l.lower() for l in listOfStructures] \
		or sel.lower() in [l.lower().replace("_"," ") for l in listOfStructures] \
		or sel.lower().replace("_"," ") in [l.lower() for l in listOfStructures]:

			sel_indx = -1
			for i, name in enumerate(listOfStructures):
				if sel.lower() == name.lower() or sel.lower().replace("_"," ") == name.lower():
					sel_indx = j
					break
			if sel_indx != -1:
				return_list[sel_indx] = name
	if "NOT_FOUND_YET" not in return_list:
		return return_list
	
	missing_indices = []
	for i, struct in enumerate(return_list):
		if struct == "NOT_FOUND_YET":
			missing_indices.append(i)
	
	missing_structs = [selections[i] for i in missing_indices]
	printStructures(structure)
	print("Please select structures. Select the structures in the given order:")
	print("If you are unable to find a structure, write \"-1\" in that structures place")
	for organ in missing_structs:
		print("\""+organ+"\"" +" ",end="")
	print("")
	selection=input(">>> ").split(" ")
	selection_ints = []
	for indx in selection:
		if indx == "-1":
			continue
		if indx.isnumeric():
			selection_ints.append(int(indx))
	
	structure_names_chosen = [[a.ROIName for a in structure.StructureSetROISequence][indx] for indx in selection_ints]
	for missing_index, missing_struct in zip(missing_indices, structure_names_chosen):
		return_list[missing_index] = missing_struct
	# now we remove all "NOT_FOUND_YET" entries
	final_return_list = []
	for entry in return_list:
		if entry != "NOT_FOUND_YET":
			final_return_list.append(entry)
	return final_return_list

def eud_calculator_rtdose(rtdose, n):
	dose_array = rtdose.pixel_array * rtdose.DoseGridScaling
	return eud_calculator_dose_array(dose_array, n)

def eud_calculator_dose_array(dose_array, n):
	dose_step=0.1
	N = len(dose_array.flatten())
	eud = 0
	if np.prod(dose_array.shape) == 0:
		return 0
	try:
		for d in np.arange(0,np.max(dose_array), dose_step):
			subset = dose_array[np.where(dose_array>=d)] 
			subset = subset[np.where(subset <d+dose_step)]
			volume = len(subset.flatten()) / N
			eud += volume * (d + dose_step/2)**(1/n)
	except ValueError:
		print("ValueError in eud_calculator_dose_array")
		print("Entering interactive for investigation")
		code_interact(globals(), locals())
		exit()

	return eud**n

def get_differential_dvh(dose_array, dose_step):
	if np.prod(np.shape(dose_array)) == 0:
		return np.array([np.array([]),np.array([])])
	doses = np.arange(0,np.max(dose_array) + dose_step, dose_step)
	volumes, bin_edges = np.histogram(dose_array, bins  = doses)
	doses = np.arange(0,np.max(dose_array), dose_step)
	volumes = volumes/ np.prod(np.shape(dose_array))
	return np.array([doses,volumes])

def gaussian(x, x0, A, sigma):
	return A*np.exp(-np.power(x-x0,2)/(2*np.power(sigma,2)))


def effective_dose_calculator_dose_array(dose_array, n):
	dose_step=0.1
	N = len(dose_array.flatten())
	d_eff = 0
	if np.prod(dose_array.shape) == 0:
		return 0
	for d in np.arange(0,np.max(dose_array), dose_step):
		subset = dose_array[np.where(dose_array>=d)] 
		subset = subset[np.where(subset <d+dose_step)]
		volume = len(subset.flatten()) / N
		d_eff += (np.power(d,1/n) * volume)

	return np.power(d_eff,n)

def promptStructure(structure, wanted_structures):
	# print structures and ask for a number then return the structname
	printStructures(structure)
	successful = False
	good_numbers = []
	while not successful:
		struct_numbers = input("Please input numbers matching the structures: ", end="")
		for struct in wanted_structures:
			print("\""+struct+"\"" + " ", end = "")
		print("\n (seperate with spaces).\n>>> ")
		numbers = struct_numbers.split(" ")
		successful = True
		for struct_num in numbers:
			if struct_num.isnumeric():
				good_numbers.append(int(struct_num))
			else:
				print("The input: \"{}\" is not allowed. Try again.".format(struct_num))
				successful = False
		if len(good_numbers) == 0:
			print("No good numbers found. Try again")
			successful = False
	structs = [[a.ROIName for a in structure.StructureSetROISequence][struct_n] for struct_n in good_numbers]
	return structs



def numpy_interp(x0s,xs,ys):
	# first need to sort ys and xs, such that they are in order of xs ascending
	idx1 = np.argsort(xs)
	return np.interp(x0s, np.array(xs)[idx1], np.array(ys)[idx1])



def rotate_points(points, rx,ry,rz):
	points_test_arr = np.array(points)

	# rotates by degrees, so converting
	rx = rx / 180 * np.pi
	ry = ry / 180 * np.pi
	rz = rz / 180 * np.pi


	x0_t, y0_t, z0_t = np.mean(points_test_arr, axis=0)
	rotated_points = []
	for point in points:
			x,y,z = point
			# FIRST TRANSLATE TO (x0_t,y0_t,z0_t)
			x -= x0_t;	y -= y0_t;	z -= z0_t
			# see https://stackoverflow.com/questions/14607640/rotating-a-vector-in-3d-space for rotation stuff
			# rotate this point around (x0_t, y0_t, z0_t) by rz around z axis
			xn = x * np.cos(rz) - y * np.sin(rz)
			yn = x * np.sin(rz) + y * np.cos(rz)
			zn = z
			x=xn;y=yn;z=zn
			# rotate this point around (x0_t, y0_t, z0_t) by ry around y axis
			xn =  x * np.cos(ry) + z * np.sin(ry)
			yn =  y
			zn = -x * np.sin(ry) + z * np.cos(ry)
			x=xn;y=yn;z=zn
			# rotate this point around (x0_t, y0_t, z0_t) by rx around x axis
			xn = x
			yn = y * np.cos(rx) - z * np.sin(rx)
			zn = y * np.sin(rx) + z * np.cos(rx)
			x=xn;y=yn;z=zn
			x += x0_t 		# NOW TRANSLATE BACK TO WHERE WE WERE BEFORE
			y += y0_t
			z += z0_t
			rotated_points.append([x,y,z])
	return rotated_points
