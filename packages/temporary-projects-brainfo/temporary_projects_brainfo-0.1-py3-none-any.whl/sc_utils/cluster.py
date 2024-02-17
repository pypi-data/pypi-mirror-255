import scanpy as sc
### add local forder to python lib
import scanpy_utils as su
import os
import argparse
import pandas as pd

parser = argparse.ArgumentParser()

parser.add_argument('-i','--work_dir', action='store', dest='wd', help='working directory')
parser.add_argument('-p','--project_name', action='store', dest='pname', help='output fastq folder')

paras = parser.parse_args()

os.chdir(f'{paras.wd}')

project_name = f'{paras.pname}'
workdir = f'{paras.wd}'
loomdir = f'{workdir}expression'

filter_params = {
    'min_counts':5000, 'min_genes':500, 'max_genes' : 20000, 'percent_mt':15, 'percent':10, 'filter_mt':True
}

## a test ver for only one batch smartseq3

adata = sc.read_loom(f'{loomdir}/{project_name}.umicount.inex.all.loom')
gene_df = pd.read_csv(f'{loomdir}/{project_name}.gene_names.txt', sep = '\t')
mapping = dict(gene_df[['gene_id', 'gene_name']].values)
adata.var_names = adata.var_names.map(mapping)
adata.var_names_make_unique('+')
su.qc(adata, f'{project_name}', 'mt')
adata_filter = su.filter_adata(adata, **filter_params)

adata_filter.layers["raw"] = adata_filter.X.copy()
su.norm_hvg(adata_filter, project_name, 10000)
sc.pp.regress_out(adata_filter, 'pct_counts_mt')

su.tsne_and_umap(adata_filter, project_name, n_comps=6)
sc.tl.leiden(adata_filter, resolution=0.2)
sc.pl.umap(adata_filter, color='leiden', save=f'{project_name}_leiden.pdf')