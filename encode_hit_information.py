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

# Return qtot and tbar from list of times
def qtot_tbar(times):
    if times:
        tbar = float(sum(times) / len(times))
        qtot = float(len(times))
        return qtot, tbar
    return 0.0, 0.0


# Constants

# Methods for encoding of bit string
STRING_METHODS = ["nolog_null", "nolog_nonull", "log_null", "log_nonull"]


# Class to generate bit strings
class BitString:
    def __init__(self, event_dict):
        self.string = ""
        self.event_dict = event_dict

    def nolog(self, null_hits):
        for dom in self.event_dict:
            times = self.event_dict[dom]
            qtot, tbar = qtot_tbar(times)
            # Include DOMs without a hit
            if null_hits:
                self.string += binary(qtot) + binary(tbar)      
            # Include only DOMs with a hit
            elif qtot > 0.0:
                self.string += domid_bin(dom[0], dom[1]) + binary(qtot) + binary(tbar)
        return self.string
                        
    def log(self, null_hits):
        if null_hits:
            pass
        else:
            pass


# Function to generate event dictionary with DOM and hit time
def GenerateSimulationStrings(geofile, hitsfile, method, output_filename):
    bit_strings = []
    
	# Initialize dictionary with IceCube DOMs from geofile
    geofile = np.genfromtxt(geofile)
    iterator = zip(geofile[:,5], geofile[:,6], geofile[:,2], geofile[:,3], geofile[:,4])
    event_dict = {tuple(map(float, tup[:2])) : [] for tup in iterator if tup[0] > 0.0 and tup[1] <= 60.0}

    # Read hits file and save hit information
    with open(hitsfile) as hf:
        for line in hf:
            # Hit was recorded
            if "HIT" in line:
                hitinfo = list(map(float, line.split(" ")[1:]))
                nstr, ndom = hitinfo[0], hitinfo[1]
                event_dict[(nstr, ndom)].append(hitinfo[2])
            # End of event
            elif "EE" in line:
                string = BitString(event_dict)
                if method == "nolog_null":
                    bit_strings.append(string.nolog(True))
                                
                elif method == "nolog_nonull":
                    bit_strings.append(string.nolog(False))

                elif method == "log_null":
                    bit_strings.append(string.log(True))

                elif method == "log_nonull":
                    bit_strings.append(string.log(False))

                event_dict = dict.fromkeys(event_dict.keys(), [])
        bit_strings = [string for string in bit_strings if string]
        print(bit_strings)
        print(len(''.join(bit_strings)))
        print(len(bit_strings))
        print([len(x) for x in bit_strings])
        np.save(output_filename, np.array(bit_strings, dtype=str))


# Main
if __name__ == "__main__":
    import argparse

    def is_npy(parser, filename):
        if not filename[-4:] == ".npy":
            parser("Output file must be a '.npy' file")
        else:
            return filename

    parser = argparse.ArgumentParser()
    parser.add_argument("-i", dest="hitsfile", type=str, default="mcp_hits.ppc",
                        help= "Input hits in PPC format")
    parser.add_argument("--input_hits", dest="hitsfile", type=str, default="mcp_hits.ppc",
                        help="Input hits in PPC format")
    parser.add_argument("-o", dest="output_filename", type=lambda x: is_npy(parser, x), default="bit_strings.npy",
                        help="Output filename")
    parser.add_argument("-g", dest="geometry", type=str, default="geo-f2k",
                        help="Input detector geometry in F2K format")
    parser.add_argument("-m", dest="method", type=str, default="nolog_null", choices=STRING_METHODS,
                        help="Method to encode bit string")

    args = parser.parse_args()
    GenerateSimulationStrings(args.geometry, args.hitsfile, args.method, args.output_filename)

