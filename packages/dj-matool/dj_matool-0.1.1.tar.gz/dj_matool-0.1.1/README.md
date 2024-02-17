**RELEASE FEATURES:**

**End Users (New Features)**

*  In the template screen it is not compulsory to verify all the templates before proceeding for pack generation. Users can generate packs for whichever templates they have verified.

![image alt text](image_0.png)

Users can proceed with the pack generation of the first three patient. Users can always come back later and proceed with pack generation after verifying the templates for the remaining two patients.

* The pack generation process is much master. It takes approx **45** seconds to generate a random collection of 100 packs. In the old version it takes approx **540** seconds to generate 100 packs. 

**Developers(New Features):**

* We have migrated our code from python 2.7 to python 3.5. This means in the future we will be able to use all the new features released by python community as well take advantage of the asynchronous programming in python.

* The new version has separate layers for business logic, models and controllers . This will give us to flexibility to migrate to any futuristic for any layer. We can easily migrate to flask or sqlalchemy or any async server without having to go through all the nightmares.

* Better error handling with a error module. New dosepack python package to handle all the common functionality across different dosepack application. Better code quality than the previous version.

* A complete new database schema. The current database will be highly normalized as compared to previous versions.

* The entire pack label will be printed from the dosepack database. Previously we used to rely on IPS to get most of the data for label.

* Multithreaded pack generation algorithm with other speedups.

* Documentation for all the webservices being exposed.(*/docs/index.html*)

* Better code commenting as compared to previous version and the commenting format can be used by tools like sphinx to generate auto documentation for the code. (In Process)

* Detailed tracking of the pack lifecycle from end to end.

* Single migration script to migrate from old database version to new database version.

**Instructions for Support**:

* Once a file is generated and it does not show up on the user screen see the fileheader table.

* To check the templates generated check the templatemaster table.

* Once a pack is generated for a file or a patient check the packdetails table to get the information.

* To check the communication with IPS and the responses received from it check packlifecycle table.

* To report any issues please attach the log files for that data along with the screenshot of the issue.

**Instructions for running new backend in dosepack server**** :**

Different flags and their values:

* -m --mode - It defines the log level. 0 indicates debug mode. 1 indicates info mode. 2 indicates error mode.

* -t --type - It indicates if we want to start the server in test, local or live mode. 0 indicates to be run in live mode. 1 indicates when we want to run the server locally. 2 indicates when we want to run the server in our amazon test server and 3 indicates when we want it to run in in our dosepack test server. According to type different paths are defined.

* If we run the server in local mode or 1 we assume we do not have IPS installed in our system. To replicate the behaviour of IPS locally we will start the program local_ips_server.py.

* -p --port - It defines the port in which server is to be run. This flag is optional. By default type 0 runs in port 10005 , type 1 and 2 runs in port 10008 and type 3 runs in the port 10009 and type 4 runs in 10012.

* -db --database - It defines the database key which we want to connect our server. The keys are present in config.json file.We have version associated with database. Make sure the key in the config file has version 2.0.

* To start the server from cmd under the project directory run : python app.py -t 2 -m 0 -db database_autobot

* We will also need to start printing service and file scheduling service. To start them from the project directory run: python print_queue.py -t 2  and python file_scheduler.py  -t 2.

* We can also start all the services simultaneously using run.bat file. Simply double click on that file to run it. If you want to modify the flags inside the file you can edit the file and modify it.

* If you ever face path problems please look into settings file and app file and verify if paths are correct.

* We assume you have all the third party and dosepack package installed. Incase not contact Manish.

**Instructions for database migration from version 1.1 to 2.0**

* Most probably these step would have already been done for you. So do not attempt it unless required.

* The basic requirement for database migration is you should be able to connect to version 1.1 of database and also the IPS database.

* To migrate from version 1.1 to 2.0 simply run in your project directory - python migrate.py -old 1.1dbname -new any_name -ips ips_databasename

* We have more than 3 million rows in our database version of 1.1. So it takes some time to complete the migration. Approx time is 15000 seconds. To ease the migration process we have savepoints. So if during middle of the migration if anything goes bad we can always come back later and resume the migration from the last saved checkpoint.

* The migration is  interactive script so please follow the instructions. 

**Instructions for IPS****:**

* We need to make sure we have updated version of IPS where we have the template for new file.

**End to End Cycle Testing:**

* Generate some sample files from IPS for filling.

* The files should be present in the Dosepack File Header Screen.

* Do the templates for the file.

* Generate the packs.

* Fill the packs from robot (Minimum 8 packs)

* Verify the labels printed.

* Verify the packs in the verification screen.

* Verify in the Rph screen of IPS if data is properly reflected for packs in it.

**Installation Instructions****:**

* Unless we have a docker container ready we will follow these steps for installation.

* We can create a virtual environment if we want to run old version along with new version or we can simply download Anaconda3 to run new version.

* The new version strictly supports python3.5+.

* To create a virtualenv in existing env run in the project directory: conda create -n venv python**=**3.5 anaconda

* To activate it run : activate venv

* Install the requirements using: pip install -r requirements.txt

* Make sure you have config.json and directories like drug_images, ips_files, pack_labels, patient_images, pharmacy_files, pharmacy_files/{pending & processed & error}, drug_images, slot_files, verification-app-setup in your project directory.

* start the server.

* Link: http://localhost:port

**File scheduler**

* For file pull feature, make sure you give correct server IP to BASE_URL_APP in settings.py


# Deployment 
- Check [deployment.md](/deployment.md)


	   

