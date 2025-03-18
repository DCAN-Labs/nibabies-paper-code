import pandas as pd 
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from pyrelimri import conn_icc
from glob import glob


def setup_icc(pconn_path, out_img):
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
	
	# Create new DF of flattened values to plot and prnit out mean and SD values
	flat_vals = {"abcd_lts": abcd_lts_flat_vals, "abcd_new": abcd_new_flat_vals, "new_lts":new_lts_flat_vals}
	flat_df = pd.DataFrame(flat_vals)
	print("ICC ABCDvsLTS Values: \n", "Mean:", flat_df["abcd_lts"].mean(), " \n STD:", flat_df["abcd_lts"].std())
	print("ICC ABCDvs23.2 Values: \n", "Mean:", flat_df["abcd_new"].mean(), " \n STD:", flat_df["abcd_new"].std())
	print("ICC 23.2vsLTS Values: \n", "Mean:", flat_df["new_lts"].mean(), " \n STD:", flat_df["new_lts"].std())
	fig_vals = flat_df[["abcd_lts", "abcd_new"]]
	plot_icc(fig_vals, out_img)
	
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
	# Reorganize data for plotting 
	new = pd.DataFrame(icc_vals["abcd_new"])
	old = pd.DataFrame(icc_vals["abcd_lts"])
	new.columns=["ICC"]
	old.columns=["ICC"]
	new["Pipeline"] = "abcd_new"
	old["Pipeline"] = "abcd_lts"
	
	# Combine into one df with ICC values and Pipeline columns
	kde_vals = pd.concat([old,new],axis=0,ignore_index=True)
	
	# Create Plots
	sns.set_context("paper",font_scale=4) 
	fig,ax = plt.subplots(figsize=(15,10))
	sns.kdeplot(kde_vals,x="ICC", hue="Pipeline",ax=ax,linewidth=5, fill=True)
	
	# Clean up Plots
	ax.set_xlim(0,1)
	ax.set_yticks([])
	ax.set_xlabel('')

	plt.savefig(out_img)
	
def plot_pearson(data, out_img):
	# Reorganize data for plotting 
	new = pd.DataFrame(data["abcd_new"])
	old = pd.DataFrame(data["abcd_lts"])
	new.columns=["Corr"]
	old.columns=["Corr"]
	new["Pipeline"] = "abcd_new"
	old["Pipeline"] = "abcd_lts"
	
	# Combine into one df with ICC values and Pipeline columns
	kde_vals = pd.concat([old,new],axis=0,ignore_index=True)
	
	# Create Plots
	sns.set_context("paper",font_scale=4) 
	fig,ax = plt.subplots(figsize=(15,10))
	sns.kdeplot(kde_vals,x="Corr", hue="Pipeline",ax=ax,linewidth=5, fill=True)
	
	# Clean up Plots
	ax.set_xlim(0,1)
	ax.set_yticks([])
	ax.set_xlabel('')

	plt.savefig(out_img)
	
def plot_qc_results(data, out_img):
	# Split out results csv into the different QC metrics and melt for the correct data format
	surface_qc = results[["Age group", "QC1 SR", "QC2 SR"]].melt(id_vars="Age group", var_name="Rater")
	spatial_qc = results[["Age group", "QC1 SN", "QC2 SN"]].melt(id_vars="Age group", var_name="Rater")
	dc_qc = results[["Age group", "QC1 DC", "QC2 DC"]].melt(id_vars="Age group", var_name="Rater")
	alignment_qc = results[["Age group", "QC1 FA", "QC2 FA"]].melt(id_vars="Age group", var_name="Rater")

	# Plot data 
	fig,((ax1,ax2),(ax3,ax4)) = plt.subplots(figsize=(20,20), ncols=2,nrows=2, layout="constrained")
	sns.despine(top=True,right=True)
	sns.stripplot(data=surface_qc,x="Age group",y="value",hue="Rater", dodge=True, alpha=.7, ax=ax1)
	sns.stripplot(data=spatial_qc,x="Age group",y="value",hue="Rater", dodge=True, alpha=.7, ax=ax2)
	sns.stripplot(data=dc_qc,x="Age group",y="value",hue="Rater", dodge=True, alpha=.7, ax=ax3)
	sns.stripplot(data=alignment_qc,x="Age group",y="value",hue="Rater", dodge=True, alpha=.7, ax=ax4)

	# Clean up plots
	for axis in [ax1,ax2,ax3,ax4]:
		axis.set_xlabel("Age Range (mo)")
		axis.set_ylabel("Rating")
		axis.set_yticks([1,1.5,2,2.5,3])
		axis.legend(title="Rater",labels=["Rater 1", "Rater 2"])
		
	ax1.set_title("Surface Reconstruction")
	ax2.set_title("Spatial Normalization")
	ax3.set_title("Distortion Correction")
	ax4.set_title("Functional Alignment")
	
	plt.savefig(out_img)

# Set paths for ICC calculations and plot
# Input path is where pconn files live, it is assumed that each pipeline has the same format of path, where only the pipeline name is different
output_path = "/home/rando149/shared/projects/rae_testing/nibabies_work/SfN_results/ICC_figure/combined_paper_figure.png"
pconn_path = "/home/rando149/shared/projects/rae_testing/nibabies_work/SfN_results/ABCD-BIDS/csv_pconns/cleaned_*"
setup_icc(pconn_path,output_path)

# Read in correlation csv, print out mean and SD values and plot
# Input csv is 3 columns (abcd_lts,abcd_new,new_lts) with pearson values for each subject
pearson_vals = pd.read_csv("/home/rando149/shared/projects/rae_testing/nibabies_work/SfN_results/all_pearson_correlations.csv")
print("Corr ABCDvsLTS values: \n", "Mean:", pearson_vals["abcd_lts"].mean(), "SD:",pearson_vals["abcd_lts"].std())
print("Corr ABCDvs23.2 values: \n", "Mean:", pearson_vals["abcd_new"].mean(), "SD:",pearson_vals["abcd_new"].std())
print("Corr 23.2vsLTS values: \n", "Mean:", pearson_vals["new_lts"].mean(), "SD:",pearson_vals["new_lts"].std())
pearson_output = "/home/rando149/shared/projects/rae_testing/nibabies_work/SfN_results/new_paper_pearson_distributions.png"
plot_pearson(pearson_vals,pearson_output)

# Read in QC results csv and create plot
# Input csv must at least have these columns: Age group, QC1 SR, QC2 SR, QC1 SN, QC2 SN, QC1 DC, QC2 DC, QC1 FA, QC2 FA
qc_csv = pd.read_csv("/home/rando149/shared/projects/rae_testing/nibabies_work/Nibabies_QC_results.csv")
qc_output = "/home/rando149/shared/projects/rae_testing/nibabies_work/paper_qc_plot.png"
plot_qc_results(qc_csv, qc_output)
