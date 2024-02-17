import subprocess
import sys
import os
from distutils.spawn import find_executable
# from TEMPy.protein.structure_parser import PDBParser
from TEMPy.maps.map_parser import MapParser
from TEMPy.protein.structure_parser import mmCIFParser
import TEMPy.protein.scoring_functions as scf
from collections import OrderedDict


def create_folder(output_path):
    """
        create smoc output folder inside va directory

    :return: model related path of strudel folder
    """

    fullname = '{}'.format(output_path)

    if not os.path.isdir(fullname):
        os.mkdir(fullname, mode=0o777)
    else:
        print('{} is exist'.format(fullname))




def run_smoc(full_modelpath, full_mappath, res, output_path):
    """

        smoc score

    :return:
    """

    errlist = []
    result_dict = {}
    try:
        create_folder(output_path)
        map = MapParser.readMRC(full_mappath)
        model = mmCIFParser.read_mmCIF_file(full_modelpath)
        sc = scf.ScoringFunctions()
        smoc_result = sc.SMOC(map, float(res), model)
        model_name = os.path.basename(full_modelpath)
        result_dict = smoc_todict(model_name, smoc_result)
    except AssertionError:
        sys.stderr.write('emringer executable is not there.\n')

    return result_dict, errlist

def smoc_tocolor(residue_smoc):
    """
        Generate the color hex code of residue by given smoc score
    :param residue_smoc: float residue smoc score
    :return: hex color code
    """

    numlist = [-1 if i < 0 else i for i in residue_smoc]
    rgbs = [[122, int(num * 255), int(num * 255)] if num >= 0 else [255, 0, 255] for num in residue_smoc]
    resultlist = ['#%02X%02X%02X' % (rgb[0], rgb[1], rgb[2]) for rgb in rgbs]

    return resultlist


def smoc_todict(model_name, smoc_result):
    """
        Save SMOC results into json file
    :param smoc_result:
    :return: json file name
    """

    colors = []
    smocs = []
    residues = []
    chain_smocs = OrderedDict()
    for chain in smoc_result[0].keys():
        chain_all = smoc_result[0][chain]
        chain_smoc = 0.
        chain_length = len(chain_all)
        for residue_no, residue_smoc in chain_all.items():
            chain_smoc += residue_smoc
            residue_type = smoc_result[2][chain][residue_no][0]
            residue_color = smoc_tocolor([residue_smoc])[0]
            residue_string = '{}:{} {}'.format(chain, residue_no, residue_type)
            colors.append(residue_color)
            smocs.append(float('%.3f' % residue_smoc))
            residues.append(residue_string)
        chain_smocvalue = chain_smoc / chain_length if chain_length != 0. else 0.
        chain_smoccolor = smoc_tocolor([chain_smocvalue])[0]
        chain_smocs[chain] = {'value': float('%.3f' % chain_smocvalue), 'color': chain_smoccolor}

    average_smoc = float('%.3f' % (sum(smocs)/len(smocs)))
    average_smoc_color = smoc_tocolor([average_smoc])[0]

    data = {'averagesmoc': average_smoc, 'averagesmoc_color': average_smoc_color, 'color': colors,
            'smoc_scores': smocs, 'residue': residues, 'chainsmoc': chain_smocs}

    result_dict = {'name': model_name, 'data': data}

    return result_dict
