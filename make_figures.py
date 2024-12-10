import pandas as pd 
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from pyrelimri import conn_icc
from glob import glob


def setup_icc(pconn_path, output_fig_path):
	# In order to guarantee paths are in the same order, glob one path then replace the pipeline with the other pipelines (assuming the path to the pconns have the same structure)
	abcd_paths = glob(pconn_path)
	abcd = {"ABCD": abcd_paths}
	paths_df = pd.DataFrame(abcd)
	paths_df["new"] =paths_df["ABCD"].apply(lambda x: x.replace("ABCD-BIDS","fMRIprep-23.2.1"))
	paths_df["lts"] =paths_df["ABCD"].apply(lambda x: x.replace("ABCD-BIDS","fMRIprep-LTS"))
	new_fMRIprep = paths_df["new"]
	fMRIprep_LTS = paths_df["lts"]
	abcd_bids = paths_df["ABCD"]
	
	# Calculate ICC for each comparison
	abcd_new_flat_vals = calc_icc(abcd_bids, new_fMRIprep)
	abcd_lts_flat_vals = calc_icc(abcd_bids, fMRIprep_LTS)
	new_lts_flat_vals = calc_icc(new_fMRIprep, fMRIprep_LTS)
	
	# Create new DF of flattened values to plot
	flat_vals = {"abcd_lts": abcd_lts_flat_vals, "abcd_new": abcd_new_flat_vals, "new_lts":new_lts_flat_vals}
	flat_df = pd.DataFrame(flat_vals)
	print("ICC ABCDvsLTS Values: \n", "Mean:", flat_df["abcd_lts"].mean(), " \n STD:", flat_df["abcd_lts"].std())
	print("ICC ABCDvs23.2 Values: \n", "Mean:", flat_df["abcd_new"].mean(), " \n STD:", flat_df["abcd_new"].std())
	print("ICC 23.2vsLTS Values: \n", "Mean:", flat_df["new_lts"].mean(), " \n STD:", flat_df["new_lts"].std())
	#plot_icc(flat_df, output_fig_path)
	
def calc_icc(pipeline1, pipeline2):
	# Grab ROI headers from one pconn created with header information
	headers=pd.read_csv("/home/rando149/shared/projects/rae_testing/nibabies_work/SfN_results/header_sub-NDARINV0VJZ6NZY_ses-baselineYear1Arm1_task-rest_run-2_pconn.csv", usecols=[0])
	rois = list(headers["Unnamed: 0"])
	
	icc_calc = conn_icc.edgewise_icc(multisession_list=[pipeline1, pipeline2],n_cols=353,col_names=rois,separator=',')
	icc_vals = pd.DataFrame(icc_calc["est"])
	
	# Flatten top half of triangle into vector
	top_vals = icc_vals.where(np.tril(np.ones(icc_vals.shape), k =-1).astype(bool))
	flat_vals = top_vals.stack().tolist()
	
	return flat_vals
	
def plot_icc(icc_vals, out_img):
	# Create Plots
	sns.set_context("paper",font_scale=4) 
	fig, (ax1,ax2,ax3) = plt.subplots(3,1,figsize=(10,14))
	sns.kdeplot(icc_vals["abcd_lts"],ax=ax1,linewidth=5,color="blue")
	sns.kdeplot(icc_vals["abcd_new"],ax=ax2,linewidth=5,color="blue")
	sns.kdeplot(icc_vals["new_lts"],ax=ax3,linewidth=5,color="blue")
	
	# Make consistent and clean up
	axes = [ax1,ax2,ax3]
	for ax in axes:
		ax.set_xlim(0,1)
		ax.set_ylim(0,20)
		ax.set_yticks([])
		# ax.legend_.remove() # AttributeError: 'NoneType' object has no attribute 'remove' since the dataframe structure is different maybe doesn't parse a legend to remove?
		ax.set_xlabel('')
		# Fill in line
		line = ax.lines[0]
		x = line.get_xydata()[:,0]
		y = line.get_xydata()[:,1]
		ax.fill_between(x,y,color="blue", alpha=0.3)
	
	ax1.set_xticks([])
	ax2.set_xticks([])
	
	ax1.set_ylabel('')
	ax2.set_ylabel('')
	ax3.set_ylabel('')
	
	plt.tight_layout()
	plt.savefig(out_img)
	
def plot_pearson(data, out_img):
	# Create Plots 
	sns.set_context("paper",font_scale=4)
	fig, (ax1,ax2,ax3) = plt.subplots(3,1,figsize=(10,14))
	sns.kdeplot(data["abcd_lts"],ax=ax1,linewidth=5,color="blue")
	sns.kdeplot(data["abcd_new"],ax=ax2,linewidth=5,color="blue")
	sns.kdeplot(data["new_lts"],ax=ax3,linewidth=5,color="blue")
	
	# Make consistent and clean up
	axes = [ax1,ax2,ax3]
	for ax in axes:
		ax.set_xlim(0,1)
		ax.set_ylim(0,20)
		ax.set_yticks([])
		ax.legend_.remove()
		ax.set_xlabel('')
		# Fill in line
		line = ax.lines[0]
		x = line.get_xydata()[:,0]
		y = line.get_xydata()[:,1]
		ax.fill_between(x,y,color="blue", alpha=0.3)
		
	
	ax1.set_xticks([])
	ax2.set_xticks([])
	
	ax1.set_ylabel('')
	ax2.set_ylabel('Distribution')
	ax3.set_ylabel('')
	
	
	plt.tight_layout()
	plt.savefig(out_img)
	
# Input CSV is 3 columns with flattened ICC values for each comparison
icc_vals = pd.read_csv("/home/rando149/shared/projects/rae_testing/nibabies_work/SfN_results/ICC_figure/flat_icc_vals.csv")
output_path = "/home/rando149/shared/projects/rae_testing/nibabies_work/SfN_results/ICC_figure/test_code_cleanup.png"
#plot_icc(icc_vals, output_path)
pconn_path = "/home/rando149/shared/projects/rae_testing/nibabies_work/SfN_results/ABCD-BIDS/csv_pconns/cleaned_*"
setup_icc(pconn_path,output_path)

pearson_vals = pd.read_csv("/home/rando149/shared/projects/rae_testing/nibabies_work/SfN_results/all_pearson_correlations.csv")
print("Corr ABCDvsLTS values: \n", "Mean:", pearson_vals["abcd_lts"].mean(), "SD:",pearson_vals["abcd_lts"].std())
print("Corr ABCDvs23.2 values: \n", "Mean:", pearson_vals["abcd_new"].mean(), "SD:",pearson_vals["abcd_new"].std())
print("Corr 23.2vsLTS values: \n", "Mean:", pearson_vals["new_lts"].mean(), "SD:",pearson_vals["new_lts"].std())
pearson_output = "/home/rando149/shared/projects/rae_testing/nibabies_work/SfN_results/paper_pearson_distributions.png"
#plot_pearson(pearson_vals,pearson_output)
