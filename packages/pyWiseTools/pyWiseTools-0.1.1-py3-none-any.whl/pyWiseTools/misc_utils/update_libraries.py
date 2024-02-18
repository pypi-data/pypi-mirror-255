import subprocess

def update_libraries():
    # Read the library names from requirements.txt
    with open('requirements.txt', 'r') as file:
        libraries = [line.strip() for line in file.readlines()]

    # Get the versions of the libraries installed on your computer
    installed_libraries = subprocess.check_output(['pip', 'freeze']).decode().split('\n')

    # Dictionary to store the versions
    versions = {}

    for lib in installed_libraries:
        # Split the line to get the library name and version
        if '==' in lib:
            name, version = lib.split('==', 1)
            versions[name] = version

    # Update the requirements.txt file with specific versions
    with open('requirements.txt', 'w') as file:
        for lib in libraries:
            if lib in versions:
                file.write(f"{lib}=={versions[lib]}\n")
            else:
                file.write(f"{lib}\n")

    print("Updated file: requirements.txt")
