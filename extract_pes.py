import sys
import cclib

def extract_pes_geometries(output_file, xyz_file):
    '''finds ALL the geometry optimization steps into a .xyz file'''
    print(f"Parsing {output_file}...")
    
    data = cclib.io.ccread(output_file)
    
    if not hasattr(data, 'atomcoords'):
        print("Error: No atomic coordinates found in this file.")
        return
        

    atom_symbols = [cclib.parser.utils.PeriodicTable().element[num] for num in data.atomnos]
    
    if hasattr(data, 'optsteps'):
        optimized_indices = data.optsteps
    else:

        print("Warning: Could not isolate final step optimizations. Exporting all frames.")
        optimized_indices = list(range(len(data.atomcoords)))

    num_atoms = len(atom_symbols)
    
    with open(xyz_file, 'w', encoding='utf-8', errors='ignore') as f:
        for step_idx, coord_idx in enumerate(optimized_indices):
            f.write(f"{num_atoms}\n")
            f.write(f"PES Scan Step {step_idx} (Internal Frame {coord_idx})\n")
            
            for atom_str, coords in zip(atom_symbols, data.atomcoords[coord_idx]):
                f.write(f"{atom_str:<4} {coords[0]:12.6f} {coords[1]:12.6f} {coords[2]:12.6f}\n")
                
    print(f"Success! Extracted {len(optimized_indices)} steps to {xyz_file}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 extract_pes.py <input_gaussian.out> <output_trajectory.xyz>")
    else:
        extract_pes_geometries(sys.argv[1], sys.argv[2])
