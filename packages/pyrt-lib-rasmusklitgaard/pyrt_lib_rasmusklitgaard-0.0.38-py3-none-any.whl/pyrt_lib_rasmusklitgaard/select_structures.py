from .helpers import selectStructures
import sys
import pydicom as pd

def select_actual_structures(rtstruct, wanted_structures):
	actual_structurenames_dict = {}
	actual_structures = selectStructures(rtstruct, wanted_structures)
	for key, value in zip(wanted_structures, actual_structures):
			actual_structurenames_dict[key] = value
			print("{}:{}".format(key,value))
	return actual_structurenames_dict

if __name__ == "__main__":
	def helpmessage():
		print("You should use this program like:")
		print("python3 select_structures.py /path/to/RTSTRUCT.dcm -o /path/to/outputfile/ structure_name_1, structure_name_2 ....")
	if len(sys.argv) < 4 or "-h" in sys.argv or "--help" in sys.argv or "-o" not in sys.argv:
		helpmessage()
		exit()
	outputfile = ""
	for i,arg in enumerate(sys.argv):
		if arg == "-o":
			ind=i+1
			if ind >= len(sys.argv):
				helpmessage()
				exit()
			outputfile = sys.argv[ind]
			del(sys.argv[ind])
			del(sys.argv[i])
	rtstruct_path = sys.argv[1]
	rtstruct = pd.read_file(rtstruct_path)
	wanted_structures = sys.argv[2:]
	structure_dict = select_actual_structures(rtstruct, wanted_structures)
	with open(outputfile, 'w') as file:
		for key, value in structure_dict.items():
			file.write(f'{key}: {value}\n')
