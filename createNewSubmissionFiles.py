import os

PathToGas = os.path.expanduser("~/Path/to/Gas/files")
PathToPCM = os.path.expanduser("~/Path/to/PCM/files")

G1 = os.path.join(PathToGas, "Step1Gas.txt")
G2 = os.path.join(PathToGas, "Step2Gas.txt")
G2b = os.path.join(PathToGas, "Step2bGas.txt")
G2c = os.path.join(PathToGas, "Step2cGas.txt")
G4 = os.path.join(PathToGas, "Step4Gas.txt")
G4b = os.path.join(PathToGas, "Step4bGas.txt")
submitAllGas = os.path.join(PathToGas,"SubmitAllGas.txt")

PCM1 = os.path.join(PathToPCM, "Step1PCM.txt")
PCM2 = os.path.join(PathToPCM, "Step2PCM.txt")
PCM3 = os.path.join(PathToPCM, "Step3PCM.txt")
PCM4 = os.path.join(PathToPCM, "Step4PCM.txt")
PCM4b = os.path.join(PathToPCM, "Step04bPCM.txt")
PCM4c = os.path.join(PathToPCM, "Step04cPCM.txt")
PCM5 = os.path.join(PathToPCM, "Step5.txt")
PCM5ESIPT = os.path.join(PathToPCM, "Step05ESIPT.txt")
PCM6 = os.path.join(PathToPCM, "Step6PCM.txt")
PCM6ESIPT = os.path.join(PathToPCM, "Step06ESIPT.txt")
submitESIPT = os.path.join(PathToPCM, "SubmitESIPT.txt")
submitAllPCM = os.path.join(PathToPCM, "SubmitAll.txt")

baseGasList = [G1, G2, G2b, G2c, G4, submitAllGas]
basePCMList = [PCM1, PCM2, PCM3, PCM4, PCM5, PCM6, submitAllPCM, PCM4b, PCM4c,PCM5ESIPT, PCM6ESIPT, submitESIPT]
allBasesList = [G1, G2, G4, submitAllGas, PCM1, PCM2, PCM3, PCM4, PCM5, PCM6]
molecule_list = ["Molecule1", "Molecule2"]
conformations = ["H", "Br"] # I used this to label substituted atoms on the same base molecule
solvents = ["Acetone", "TetraHydroFuran", "Methanol", "Toluene", "Acetonitrile", "Chloroform","n,n-DiMethylFormamide"] # or whatever solvents you want



def modifyBase(file,MN,conform, isolve, HAG, HOI):
    if not os.path.exists(file):
        print(f"Error: Template file not found at {file}")
        return None

    with open(file,'r', encoding='utf-8', errors='ignore') as f:
       content = f.read()

    content = content.replace('MN', MN)
    content = content.replace('conform', conform)
    content = content.replace('isolve', isolve)
    content = content.replace("HAG", str(int(HAG)))
    content = content.replace("HOI", str(int(HOI)))
    return content

def generateAllPCM(HAG,HOI):
    print("reading all files")
    files_created = 0
    for molecule in molecule_list:
        for solvent in solvents:
            for conform in conformations:
                for filePath in basePCMList:
                    custom_script = modifyBase(filePath, molecule, conform, solvent, HAG, HOI)
                    if custom_script is None:
                        continue

                    outputDir = os.path.join(PathToPCM, molecule, conform, solvent)
                    os.makedirs(outputDir, exist_ok=True)
                    baseName = os.path.splitext(os.path.basename(filePath))[0]

                    scriptName = f"{baseName}-{molecule}-{conform}-{solvent}.slurm"
                    finalPath = os.path.join(outputDir, scriptName)
                    with open(finalPath, 'w', encoding= 'utf-8') as f:
                        f.write(custom_script)

                    os.chmod(finalPath, 0o755)
                    files_created += 1

    print(f"\nSuccess! Generated {files_created} files for submission to Gaussian in folder: {PathToPCM}")
    print(f"\nRemember to add geometry to step 1 file and change the atom numbers in file 4b (marked with EWG and EAG)")

def generateAllGas(HAG, HOI):
    print("reading all Gas files")
    gas_files = 0
    for molecule in molecule_list:
        for conform in conformations:
            for filePath in baseGasList:
                custom_script = modifyBase(filePath, molecule, conform, '',HAG,HOI)
                if custom_script is None:
                    continue

                outputDir = os.path.join(PathToGas, molecule, conform)
                os.makedirs(outputDir, exist_ok=True)
                baseName = os.path.splitext(os.path.basename(filePath))[0]

                scriptName = f"{baseName}-{molecule}-{conform}-gas.sh"
                finalPath = os.path.join(outputDir, scriptName)
                with open(finalPath, 'w', encoding= 'utf-8') as f:
                    f.write(custom_script)

                os.chmod(finalPath, 0o755)
                gas_files += 1
    print(f"\nSuccess Generated {gas_files} files for submission to Gaussian in folder: {PathToGas}")
    print(f"\nRemember to add the geometry to step 1 file, and adjust the atom numbers marked with EWG and EAG")

def generateAllFiles(HAG, HOI):
    generateAllPCM(HAG, HOI)
    generateAllGas(HAG,HOI)


if __name__ == "__main__":
    generateAllGas("4","25")
    generateAllPCM("4","25")
    generateAllFiles("4", "25")





