% J. Davis
% script to read in and convert CDIP036.mat to a Py-friendly format

load('CDIP036_spectra_Jul2021.mat')


for i = 1:length(CDIP)
    if i==1
        fieldNames = fields(CDIP(i).wavespectra);
        wavespectraTable =  table('Size',[0,size(fieldNames,1)],... 
	        'VariableNames', fieldNames.',...
            'VariableTypes', repelem(["string"],length(fieldNames)));
        t0 = datestr(CDIP(i).time,'mmmyyyy');
    end
    for f = 1:length(fieldNames)
        currField = fieldNames(f); currField = currField{1};
        fieldStringArr = string(CDIP(i).wavespectra.(currField)).';
        strList = strcat("[",strjoin(fieldStringArr,','),"]");
        wavespectraTable.(currField)(i) = strList;
    end
    t = datetime(CDIP(i).time,'ConvertFrom','datenum');
    CDIP(i).time = datestr(t,'yyyy-mm-dd HH:MM:SS');
end

T = struct2table(rmfield(CDIP,'wavespectra'));

writetable([T wavespectraTable],['CDIP036_',t0,'.csv'],'Delimiter',';')