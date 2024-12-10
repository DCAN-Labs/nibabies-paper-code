%purpose of script: calculate correlation values between parcellated
%timeseries to have initial results for SfN abstract

% the script will read in the names of individual pconn files, correlate
% them and save the correlation values in a matrix
%statistis can be run from there. 

clear all

addpath(genpath('/home/rando149/shared/projects/rae_testing/nibabies_work/SfN_results/code'));
input_path='/home/rando149/shared/projects/rae_testing/nibabies_work/SfN_results/'
output_mat=NaN(100,3);
input23=dir([input_path, '/fMRIprep-23.2.1/pconns/*nii']);
inputLTS=dir([input_path, '/fMRIprep-LTS/pconns/*nii']);
inputABCD=dir([input_path, '/ABCD-BIDS/pconns/*nii']);


for n=1:100
%step 1, define pconn filenames
pconn23=[input23(n).folder, '/', input23(n).name];
pconnLTS=[inputLTS(n).folder, '/', inputLTS(n).name];
pconnABCD=[inputABCD(n).folder, '/', inputABCD(n).name];

%step2: correlate
%corr1= fmroprep23 vs. LTS
%corr2=fmriprep23 vs. abcd-bids
%corr3=LTS vs. abcd-bids


corr1=CalculateDconntoDconnCorrelation('DconnOne', pconn23, 'DconnTwo', pconnLTS, 'wb_command','/home/faird/shared/code/external/utilities/workbench/1.4.2/workbench/bin_rh_linux64/wb_command', ...
    'CIFTI_path','/home/faird/shared/code/external/utilities/cifti-matlab', ...
    'GIFTI_path','/home/faird/shared/code/external/utilities/gifti/');
corr2=CalculateDconntoDconnCorrelation('DconnOne', pconn23, 'DconnTwo', pconnABCD, 'wb_command','/home/faird/shared/code/external/utilities/workbench/1.4.2/workbench/bin_rh_linux64/wb_command', ...
    'CIFTI_path','/home/faird/shared/code/external/utilities/cifti-matlab', ...
    'GIFTI_path','/home/faird/shared/code/external/utilities/gifti/');
corr3=CalculateDconntoDconnCorrelation('DconnOne', pconnLTS, 'DconnTwo', pconnABCD, 'wb_command','/home/faird/shared/code/external/utilities/workbench/1.4.2/workbench/bin_rh_linux64/wb_command', ...
    'CIFTI_path','/home/faird/shared/code/external/utilities/cifti-matlab', ...
    'GIFTI_path','/home/faird/shared/code/external/utilities/gifti/');
output_mat(n,1)=corr1;
output_mat(n,2)=corr2;
output_mat(n,3)=corr3;
end

save('correlation_matrixes','output_mat');

%possible statistiacl test: two paired sample ttests
%similarity fmriprep-LTS and abcd-bids vs similarity fmriprep23 and
%ABCD-bids
[h,p] = ttest(output_mat(:,3),output_mat(:,2))
