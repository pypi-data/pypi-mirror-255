import os

def installPackage(Name):

    """
    Install a PIP package
    """

    os.system("pip install " + Name)

def uninstallPackage(Name):

    """
    Uninstalls a PIP package
    """

    os.system("pip uninstall " + Name)

def run(Name):

    """
    Runs a python file
    """

    os.system("python.exe " + Name)

def deleteFile(Name):

    """
    Deletes a file
    """

    os.system("del " + Name)

def changeDir(Path):

    """
    Change directory of command prompt
    """

    os.system("cd " + Path)

def changeDrive(Drive):

    """
    Changes drive of command prompt
    """

    os.system(Drive)

def showDir(Path = ""):

    """
    Shows the content in directory
    """

    os.system("dir " + Path)

def makeDir(Name):

    """
    Make a folder in directory
    """

    os.system("mkdir " + Name)

def command(Cmd):

    """
    Make a command in command prompt
    """

    os.system(Cmd)

def echo(Cmd):

    """
    Make a echo command in command prompt
    """

    os.system("echo " + Cmd)