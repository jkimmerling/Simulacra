# SimulacrIoT
HVAC and IoT Device Simulator

This is meant to act as a simulator of a device/network of devices. Its primary uses cases are to test  
either data pipelines or fault detection algorithms.

# Work in progress  
Currently just a basic Flask Api interface  
Coming next:  
MQTT & Bacnet interfaces  
  
# Current Features  
Loads the trend data from CSVs  
Configurable to either use the data data directly (best for small data sets), or to use Redis to hold the data  
Can mimic different data intervals or be set to send new data each call  
Can be set to simulate any number of devices  
If you data from files, it can rotate through the trends to simulate more devices than the number of files available  
If you data from files, it can rotate through the provided trend to simulate more readings than the number of files available  

 

Credit for Dataset:  
The dataset used for this project: "Automated Fault Detection and Diagnostics Data Curation and Benchmarking"  
The authors: Jessica Granderson and Guanjing Lin  
Project Link: https://data.openei.org/submissions/910  
License Link: https://creativecommons.org/licenses/by/4.0/  
