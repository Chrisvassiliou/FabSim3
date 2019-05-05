# Install an application remotely from your laptop to the cluster

## Basic informations

In machine.yml or machine_user.yml, the 'app_repository' variable must be set on the remote you want to install the application. 
'app_repository' is the path of the repository, on the remote, that will contain the sources of the application and its dependencies. 

All the information about the application has to be define in deploy/application.yml like below :

> QCG-PilotJob:
>	repository: https://github.com/vecma-project/QCG-PilotJob.git   # github repository
>	name : QCGPilotManager  # Name of the downloaded zip with pip  
>	version: 0.1	# last release version


The application will be install to the '--user' path.

## Examples 

fab genji install_app:QCG-Pilotjob

Will install PilotJobManager on Genji supercomputer 


Warning: Currently, it only works with python application.
