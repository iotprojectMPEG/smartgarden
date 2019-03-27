close all; clc; clear;

channelID = 741610;

fileID = fopen('readAPI', 'r');
readAPI = fscanf(fileID, '%s')
fclose(fileID);

fileID = fopen('writeAPI', 'r');
writeAPI = fscanf(fileID, '%s')
fclose(fileID);

data =[20 21 14]
data = thingSpeakWrite(channelID, data,  'WriteKey', writeAPI)
data = thingSpeakRead(channelID, 'ReadKey', readAPI)