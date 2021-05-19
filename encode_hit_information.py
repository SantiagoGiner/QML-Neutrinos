import struct
import numpy as np

# Helper functions

# Generate a DOM ID in binary representation
def domid_bin(nstr, ndom):
	maxexp = 13
	domid = 86 * (int(nstr) - 1) + 60 * (int(ndom) - 1)
	return ("0" * maxexp + bin(domid)[2:])[-1 - maxexp:]

# Convert decimal number to single-point representation
def binary(num):
	return "".join("{:0>8b}".format(c) for c in struct.pack("!f", num))

# Class to generate bit strings
class BitString:
	def __init__(self, event_dict):
		self.string = ""
		self.event_dict = event_dict

	def nolog(self, null_events):
		for dom in self.event_dict:
			times = self.event_dict[dom]
			domid = domid_bin(dom[0], dom[1])
			if times:
				tbar = float(sum(event_times) / len(event_times))
				qtot = float(len(event_times))
			elif null_events:
			    qtot, tbar = 0.0, 0.0

			elif not null_events:
				pass
			self.string += domid + binary(qtot) + binary(tbar)
		return self.string
			
	def log(self, null_events):
		if null_events:
			pass
		else:
			pass


# Function to generate event dictionary with DOM and hit time
def GenerateSimulationStrings(geofile="./PPC/geo-f2k", hitsfile="mcp_hits.ppc", method="nolog_null"):
	bin_strings = []
	
	# Initialize dictionary with IceCube DOMs from geofile
	geofile = np.genfromtxt(geofile)
	iterator = zip(geofile[:,5], geofile[:,6], geofile[:,2], geofile[:,3], geofile[:,4])
	event_dict = {tuple(tup[:2]) : [] for tup in iterator if tup[0] > 0 and tup[1] <= 60}
	print(event_dict)

	# Read hits file and save hit information
	with open(hitsfile) as hf:
		for line in hf:
			# Hit was recorded
			if "HIT" in line:
				hitinfo = list(map(float, line.split(" ")[1:]))
				nstr, ndom = hitinfo[0], hitinfo[1]
				event_dict[(nstr, ndom)].append(hitinfo[2])

			elif "EE" in line:
				string = BitString(event_dict)
				if method == "nolog_null":
					bin_strings.append(string.nolog(True))
				
				elif method == "nolog_nonull":
					bin_strings.append(string.nolog(False))
	
				elif method == "log_null":
					bin_strings.append(string.log(True))

				elif method == "log_nonull":
					bin_strings.append(string.log(False))

				event_dict = dict.fromkeys(event_dict.keys())

GenerateSimulationStrings()

