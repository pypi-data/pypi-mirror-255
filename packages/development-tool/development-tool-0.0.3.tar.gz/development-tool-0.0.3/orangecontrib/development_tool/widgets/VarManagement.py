import os
import sys

from orangecontrib.development_tool.widgets import shared_variables, MetManagement


def read_dict_variable(argself):
    """
    Cette fonction lit les variables globales à partir d'un fichier de configuration spécifique et les stocke dans un dictionnaire

    @argself

    return : Retourne 0 si la lecture est réussie et 1 en cas d'erreur.
    """
    current_metdir=MetManagement.current_met_directory(argself)

    if current_metdir=="":
        argself.error("error you need to save your ows file before")
        return 1

    argself.error("")
    file_name=current_metdir+"/dict_variable.met"
    if os.path.isfile(file_name)!=True:#
        shared_variables.dict_variable={}
        return 0
    test_string=[]
    try:
        with open(file_name, 'r') as f:
            test_string=f.readlines()
        f.close()
    except Exception as e:
        print(e, file=sys.stderr)
        print("error in reading file :", file_name, file=sys.stderr)
        argself.error("error in reading file :"+ file_name)
        return 1

    if len(test_string)!=1:
        print("error in reading file, nb line !=1:", file_name, file=sys.stderr)
        argself.error("error in reading file , nb line !=1 :"+ file_name)
        return 1
    test_string=test_string[0]
    if(len(test_string)<2):
        print("error in reading file, too small:", file_name, file=sys.stderr)
        argself.error("error in reading file , too small :"+ file_name)
        return 1
    test_string=str(test_string)
    shared_variables.dict_variable=eval(test_string)
    return 0

def write_dict_variable(argself):
    """
    Cette fonction écrit les variables globales stockées dans mes_variables_partagees.dict_variable dans un fichier de configuration.

     @argself

    return : Retourne 0 si la lecture est réussie et 1 en cas d'erreur.
    """
    current_metdir=MetManagement.current_met_directory(argself)
    if current_metdir=="":
        argself.error("error you need to save your ows file before")
        return 1
    argself.error("")
    file_name=current_metdir+"/dict_variable.met"
    try:
        with open(file_name, 'w') as f:
            f.write(str(mes_variables_partagees.dict_variable))
        f.close()
    except Exception as e:
        print(e, file=sys.stderr)
        print("error in writing file :", file_name, file=sys.stderr)
        argself.error("error in writing file :"+ file_name)
        return 1
    return 0
#
def set_value_to_dict_variable(argself,name,value):
    """
    Cette fonction permet de définir une valeur pour une variable globale spécifiée par son nom name.
    Elle vérifie également que le nom de la variable ne contient pas de caractères spéciaux.
    Elle utilise read_dict_variable pour lire les variables existantes, met à jour la variable spécifiée, puis utilise write_dict_variable pour écrire les modifications dans le fichier de configuration.

    """
    if 0!=read_dict_variable(argself):
        argself.error("error reading dict variable file")
        return
    argself.error("")
    if name == "":
        argself.error("VariableName = None")
        return
    special_characters = "!@#$%^&*()-+?_=,<>/\\&é{}[]%ù*$£¨|èçà?;:§ €"
    special_characters += "'"
    special_characters += '"'
    if any(c in special_characters for c in name):
        argself.error("special characters in VariableName ")
        return
    argself.error("")
    shared_variables.dict_variable[name] = float(value)

    return write_dict_variable(argself)

def get_all_name_from_dict_variable(argself):
    """
    Cette fonction retourne la liste de tous les noms de variables globales stockées dans mes_variables_partagees.dict_variable.
    Elle utilise read_dict_variable pour lire les variables.
    """
    if 0!=read_dict_variable(argself):
        argself.error("error reading dict variable file")
        return
    argself.error("")
    resultat=[]
    for key in shared_variables.dict_variable:
        resultat.append(str(key))
    return resultat

def get_value_from_dict_variable(argself,name):
    """
    Cette fonction retourne la valeur d'une variable globale spécifiée par son nom name.
    Elle utilise read_dict_variable pour lire les variables.
    """
    if 0!=read_dict_variable(argself):
        argself.error("error reading dict variable file")
        return
    argself.error("")
    return shared_variables.dict_variable[name]

def remove_value_from_dict_variable(argself,name):
    """
    Cette fonction permet de supprimer une variable globale spécifiée par son nom name du dictionnaire mes_variables_partagees.dict_variable.
    Elle utilise write_dict_variable pour écrire les modifications après la suppression.
    """
    if name in shared_variables.dict_variable:
        del shared_variables.dict_variable[name]
        write_dict_variable(argself)
