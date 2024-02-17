import os
from pathlib import Path
import scanpy as sc
import warnings
MODULE_PATH = Path(__file__).parent
warnings.filterwarnings("ignore")

zenodo_accession = '8196645'


################
#     Human    #
################


def human_gex_reference_v2():
    """
    Load the human gex reference v2
    """
    default_path = os.path.join(MODULE_PATH, '../data/datasets/human_gex_reference_v2.h5ad')
    if os.path.exists(
        default_path
    ):
        return sc.read_h5ad(default_path)
    else:
        os.system(f"curl -o {default_path} https://zenodo.org/record/{zenodo_accession}/files/human_gex_reference_v2.h5ad?download=1")
    
def human_gex_reference_v2_cd4():
    """
    Load the human gex reference v2 CD4 subset
    """
    default_path = os.path.join(MODULE_PATH, '../data/datasets/human_gex_reference_v2_cd4.h5ad')
    if os.path.exists(
        default_path
    ):
        return sc.read_h5ad(default_path)
    else:
        os.system(f"curl -o {default_path} https://zenodo.org/record/{zenodo_accession}/files/human_gex_reference_v2_cd4.h5ad?download=1")

def human_gex_reference_v2_cd8():
    """
    Load the human gex reference v2 CD8 subset
    """
    default_path = os.path.join(MODULE_PATH, '../data/datasets/human_gex_reference_v2_cd8.h5ad')
    if os.path.exists(
        default_path
    ):
        return sc.read_h5ad(default_path)
    else:
        os.system(f"curl -o {default_path} https://zenodo.org/record/{zenodo_accession}/files/human_gex_reference_v2_cd8.h5ad?download=1")


def human_gex_reference_v2_zheng_2020_cd4():
    """
    Load the human gex reference v2 merged with Zheng et al. 2020 CD4 subset
    """
    default_path = os.path.join(MODULE_PATH, '../data/datasets/human_gex_reference_v2_zheng_2020_cd4.h5ad')
    if os.path.exists(
        default_path
    ):
        return sc.read_h5ad(default_path)
    else:
        os.system(f"curl -o {default_path} https://zenodo.org/record/{zenodo_accession}/files/human_gex_reference_v2_zheng_2020_cd4.h5ad?download=1")

def human_gex_reference_v2_zheng_2020_cd8():
    """
    Load the human gex reference v2 merged with Zheng et al. 2020 CD8 subset
    """
    default_path = os.path.join(MODULE_PATH, '../data/datasets/human_gex_reference_v2_zheng_2020_cd8.h5ad')
    if os.path.exists(
        default_path
    ):
        return sc.read_h5ad(default_path)
    else:
        os.system(f"curl -o {default_path} https://zenodo.org/record/{zenodo_accession}/files/human_gex_reference_v2_zheng_2020_cd8.h5ad?download=1")

def human_gex_multi_atlas_v1_cd4():
    """
    Load the human gex multi atlas v1 CD4 subset
    """
    default_path = os.path.join(MODULE_PATH, '../data/datasets/human_gex_multi_atlas_v1_cd4.h5ad')
    if os.path.exists(
        default_path
    ):
        return sc.read_h5ad(default_path)
    else:
        raise FileNotFoundError("Dataset has not been published online. Please contact the author for more information.")
    
def human_gex_multi_atlas_v1_cd8():
    """
    Load the human gex multi atlas v1 CD8 subset
    """
    default_path = os.path.join(MODULE_PATH, '../data/datasets/human_gex_multi_atlas_v1_cd8.h5ad')
    if os.path.exists(
        default_path
    ):
        return sc.read_h5ad(default_path)
    else:
        raise FileNotFoundError("Dataset has not been published online. Please contact the author for more information.")


################
#     Model    #
################


def download_model_weights():
    os.system(f"curl -o ../data/pretrained_weights/human_bert_tcr_768_v2.ckpt https://zenodo.org/record/{zenodo_accession}/files/human_bert_tcr_768_v2.ckpt?download=1")
    os.system(f"curl -o ../data/pretrained_weights/human_bert_tcr_pca_v2.pkl https://zenodo.org/record/{zenodo_accession}/files/human_bert_tcr_pca_v2.pkl?download=1")

