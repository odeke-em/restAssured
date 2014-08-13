
RestAssured  [![wercker status](https://app.wercker.com/status/ed37425ce64eb4c9f78c7a5f3212df2f/m "wercker status")](https://app.wercker.com/project/bykey/ed37425ce64eb4c9f78c7a5f3212df2f)
==================================================

  API for setting up any web project. Interfaces' with Django's

  DB wrapper/API to provide full CRUD [ Create, Read, Update, Delete ]

  functionality for your project.

  The main API is in a sub-directory of restAssured the main directory: 

    ie restAssured/api


Embedding RestAssured in an application:
========================================

  The official API can be found here: [resty](https://github.com/odeke-em/resty.git "Resty")


Getting started:
=======================

    + Make sure you have django installed on your system. If not visit:

	https://docs.djangoproject.com/en/dev/intro/install/	      
    
     for instructions on installation. 
      

  To build your own app:

    + Go to main directory 'restAssured', run:

      'django-admin.py startapp <Your_Project>'

      And then modify <Your_Project>/views.py to get the functionality

      of the API I have provided.

  Otherwise, to fire up the app:

    + Go to main directory 'restAssured', you will find a file 'manage.py'
    
    + Initialize your database by

	    python manage.py syncdb

      You will also be prompted to create a super user for your project.
      
      The project is set up to also allow you to modify and view the data

      from your admin/super user page by visiting : <yoursite:port>/admin

	where you will enter your admin credentials

    + To fire up and start serving, run this command:
      
      python manage.py runserver <yourIp>:<desiredport>


Detailed Walkthrough and example:
=================================

   Present here: [detailedUsage.md](https://github.com/odeke-em/restAssured/blob/master/examples/detailedUsage.md "Detail Usage")
