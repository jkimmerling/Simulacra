# SimulacrIoT
HVAC and IoT Device Simulator

This is meant to act as a simulator of a device/network of devices. Its primary uses cases are to test either data pipelines or fault detection algorithms.  

# Current Features  
* Loads the trend data from CSVs  
* Redis backend support
* Configurable to either use the data data directly (best for small data sets), or to use backend DB to hold the data
* Can mimic different data intervals or be set to send new data each call  
* Can be set to simulate any number of devices  
* If the data is loaded in from files, it can rotate through the trends to simulate more devices than the number of files available  
* If the data is loaded in from files,  it can rotate through the provided trend to simulate more readings than the number of files available  
* Uses a Flask Api to return the readings in JSON format  

# Planned Features  
* Add MQTT interface
* Add Bacnet interface
* Add ability to randomly generate readings
* Add MySQL backend support
* Add MongoDB backend support
* Ceate docker compose to have everything in one quickly deployable package

 
# Credits
Credit for Dataset:  
The dataset used for this project: "Automated Fault Detection and Diagnostics Data Curation and Benchmarking"  
The authors: Jessica Granderson and Guanjing Lin  
Project Link: https://data.openei.org/submissions/910  
License Link: https://creativecommons.org/licenses/by/4.0/  
