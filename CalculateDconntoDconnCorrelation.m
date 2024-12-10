function [dconn_corr] = CalculateDconntoDconnCorrelation(varargin)

%%%
%modified May 2024 to not exclude NaNs when creating the voctors and instead only correlating complete rows
%%%

%CalculateDconntoDconnCorrelation calculates a correlation between dconns
% this function loads two dconns/pconns, calculates their correlation and
% writes the resulting matrix as a .txt file to the output directory
%
% Usage: [dconn_corr] = CalculateDconntoDconnCorrelation(varargin)
%
%   Required inputs:
%   dconn_one <path>               :  path to first pconn/dconn to load
%   dconn_two <path>       :  path to second pconn/dconn to load
%   wb_command <path>       :  path to workbench command
%   OutputDirectory <path> : path to output directory
%   GIFTI_path <path> : path to GIFTI tool box
%   CIFTI_path <path> : path to CIFTI tool box

%% declare optional input defaults then parse varargin
p = inputParser;
addParamValue(p,'DconnOne','./dummy');
addParamValue(p,'DconnTwo','./dummytwo');
addParamValue(p,'OutputDirectory','./');
addParamValue(p,'wb_command','wb_command');
addParamValue(p,'CIFTI_path','/home/faird/shared/code/internal/utilities/cifti-matlab');
addParamValue(p,'GIFTI_path','/home/faird/shared/code/internal/utilities/gifti/');

parse(p,varargin{:})

addpath(genpath('/home/miran045/shared/code/internal/utilities/Matlab_CIFTI'));
addpath(genpath('/home/miran045/shared/code/internal/utilities/CIFTI/'));
addpath(genpath('/home/miran045/shared/code/internal/utilities/gifti'));

%% parse the inputs
output_directory=p.Results.OutputDirectory;
wb_command=p.Results.wb_command;
addpath(genpath(p.Results.CIFTI_path))
addpath(genpath(p.Results.GIFTI_path))
dconn_one=p.Results.DconnOne;
dconn_two=p.Results.DconnTwo;

%% load dconn one and select upper triangle

dconn_one_conn = ciftiopen(dconn_one,wb_command);
dconn_one_data = dconn_one_conn.cdata;
if (dconn_one_data(1,1) > 7)
    dconn_one_data = tanh(dconn_one_data);
end
clear dconn_one_conn
%dconn_one_vector = zeros(length(dconn_one_data)*(length(dconn_one_data)-1)/2,1);
%dconn_one_vector(:,1) = dconn_one_data(abs(triu(dconn_one_data,1)) > 0);
dconn_one_vector= dconn_one_data(abs(triu(dconn_one_data,1)) ~= 0);
clear dconn_one_data

%% load dconn two and select upper triangle
dconn_two_conn = ciftiopen(dconn_two,wb_command);
dconn_two_data = dconn_two_conn.cdata;
if (dconn_two_data(1,1) > 7)
    dconn_two_data = tanh(dconn_two_data);
end
clear dconn_two_conn
% dconn_two_vector = zeros(length(dconn_two_data)*(length(dconn_two_data)-1)/2,1);
% dconn_two_vector(:,1) = dconn_two_data(abs(triu(dconn_two_data,1)) > 0);
dconn_two_vector= dconn_two_data(abs(triu(dconn_two_data,1)) ~= 0);
clear dconn_two_data

%% calculate correlation and write to file
dconn_corr = corr(dconn_one_vector,dconn_two_vector, 'rows','complete');
% define fitting string for output name (cannot be too long) --> should be refined for more general usage purposes
[~,dconn_one_short]=fileparts(dconn_one); 
str_ind1=strfind(dconn_one_short, '_task');
str_ind2=strfind(dconn_one_short, 'nii');
dconn_one_short=dconn_one_short([1:str_ind1-1, str_ind2+3:end]);

[~,dconn_two_short]=fileparts(dconn_two); 
str_ind1=strfind(dconn_two_short, '_task');
str_ind2=strfind(dconn_two_short, 'nii');
dconn_two_short=dconn_two_short([1:str_ind1-1, str_ind2+3:end]);

%dlmwrite(strcat(output_directory,'/',dconn_one_short,'_CorrTo_',dconn_two_short,'.txt'),dconn_corr);
%writematrix(dconn_corr, strcat(output_directory,'/',dconn_one_short,'_CorrTo_',dconn_two_short,'.txt'));
end

