
RestAssured v0.0.1
==================================================

  API for setting up any web project. Interfaces' with Django's

  DB wrapper/API to provide full CRUD [ Create, Read, Update, Delete ]

  functionality for your project.

  The main API is in a sub-directory of restAssured the main directory: 

    ie restAssured/api

  A demo project is set up under 'thebear' that will extend the scrapper
  
  and tracker that I built to get top played tracks and rank them, hence

  providing an app that other developers can extend for use with the web,
  
  mobile etc.


API Usage:
======================

  For starters, I have created a web application called 'thebear' which

  you can find in directory restAssured. It is a spin-off of a hack that
  
  I created to track, rank and report about the songs played by 
  
  Edmonton radio station 'The Bear Rocks'.

  Getting started:

    + Make sure you have django installed on your system. If not visit:

	https://docs.djangoproject.com/en/dev/intro/install/	      
    
     for instructions on installation. 
      

  To build your own app:

    + Go to main directory 'restAssured', run:

      'django-admin.py startapp <Your_Project>'

      And then modify <Your_Project>/views.py to get the functionality

      of the API I have provided.

  Otherwise, to fire up the app I have started 'thebear':

    + Go to main directory 'restAssured', you will find a file 'manage.py'
    
    + Initialize your database by

	python manage.py syncdb
      You will also be prompted to create a super user for your project.
      
      The project is set up to also allow you to modify and view the data

      from your admin/super user page by visiting : <yoursite:port>/admin

	where you will enter your admin credentials

    + To fire up and start serving, run this command:
      
      python manage.py runserver <yourIp>:<desiredport>

      eg:

	For the purpose of explanation, let us spawn a server off

	  192.168.1.23 serving through port 8008

	    python manage.py runserver 192.168.1.23:8008

      Open a browser or access the url: 'http://192.168.1.23:8008/thebear'

      'thebear' has defined handlers to provide CRUD functionality to 
    
      tables defined in the database.

       ========================================
      | TableName         |    Handler Name    |
      ------------------------------------------
      | Song              |   songHandler      |
      ------------------------------------------
      | PlayTime	  |   playTimeHandler  |
      ------------------------------------------
      | SongEntry         |   entryHandler     |
      ------------------------------------------

      So to access table 'Song'

      Visit:
	http://192.168.1.23:8008/thebear/songHandler
      This should return you a JSON object like so:
      '{
	  "meta": {
	    "sort": "-id", "count": 4, "format": "short"
	  }, 
	  "data": [
	    {
	      "trackHash": "RDnLCqSMDEQsA", "artist": "Nicki Minaj", 
	      "url": "https://www.youtube.com/watch?v=EmZvOhHF85I&list=RDnLCqSMDEQsA", "title": "Beez in the trap", "id": 4
	    }, 
	    {
	      "trackHash": "v=ep0hay4Qw54", "artist": "Kendrick Lamar", 
	      "url": "http://www.youtube.com/watch?v=ep0hay4Qw54", "title": "HiiiPower", "id": 3
	    }, 
	    {
	      "trackHash": "bek1y2uiQGA", "artist": "Avicii vs Nicki Romero", 
	      "url": "https://www.youtube.com/watch?v=bek1y2uiQGA", "title": "I could be the one", "id": 2
	    }, 
	    {
	      "trackHash": "YgGLl8CanQo", "artist": "Dr. Dre", 
	      "url": "https://www.youtube.com/watch?v=YgGLl8CanQo", "title": "Still Dre", "id": 1
	    }
	]
      }'

      Looking at the sample JSON notice that the JSON consists of the meta and data sections

      In the meta section, we have the sort-ing method, element count and format

      Explanation:
	'sort' => Is any attribute present for the object eg

	  Song contains attributes: Artist, TrackHash, Url, Title, Id

	  Note:
	    + With no key sort key provided, the default key will be Id but reversed so that the newest

	      objects are always displayed first.

	    + To sort in ascending order, the sort-by key will be passed in, as is ie /?sort=foo

	    + To sort in descending/reverse order, the sort-by key is suffixed by _r

	      in as is ie /?sort=foo_r

	  For example:

	    http://192.168.1.23.8008/thebear/songHandler/?sort=artist

	  Sorting in reverse order:

	    http://192.168.1.23.8008/thebear/songHandler/?sort=artist_r

	'count' => The number of elements present in the DB.

	'format' => Options are 'short' or 'long'

	  'long' implies that any table that contains the current resource as a foreign key will be returned

	  eg: Repeating the query but with the format set to 'long' yields a JSON like so:

	  '{
	    "meta": {
		"sort": "artist", "count": 4, "format": "long"
	    }, 
	    "data": [
		{
		  "trackHash": "RDnLCqSMDEQsA", 
		  "songentry_set": [
		      {
			"playTime_id": "3", 
			"playTime": {
			   "timeSinceEpoch": "1348574.88", "id": 3
			}, 
			"song_id": "4", "id": 8
		      }
		  ], 
		  "artist": "Almonds", "url": "https://www.youtube.com/watch?v=EmZvOhHF85I&list=RDnLCqSMDEQsA", 
		  "title": "Beez in the trap", "id": 4
		}, 
		{
		  "trackHash": "bek1y2uiQGA", 
		  "songentry_set": [
		    {
		      "playTime_id": "1", 
		      "playTime": {
			"timeSinceEpoch": "13808737.82", "id": 1
		      }, 
		      "song_id": "2", "id": 5
		    }, 
		    {
		      "playTime_id": "2",
		      "playTime": {
			"timeSinceEpoch": "13808738.92", "id": 2
		      }, 
		      "song_id": "2", "id": 6
		    }
		  ], 
		  "artist": "Avicii vs Nicki Romero", "url": "https://www.youtube.com/watch?v=bek1y2uiQGA", 
		  "title": "I could be the one", "id": 2
		}, 
		{
		  "trackHash": "YgGLl8CanQo", 
		  "songentry_set": [
		    {
		      "playTime_id": "1", "playTime": {
			  "timeSinceEpoch": "13808737.82", "id": 1
		      }, 
		      "song_id": "1", "id": 2
		    }, 
		    {
		      "playTime_id": "1", 
		      "playTime": {
			"timeSinceEpoch": "13808737.82", "id": 1
		      }, 
		      "song_id": "1", "id": 3
		    }
		  ], 
		  "artist": "Dr. Dre", "url": "https://www.youtube.com/watch?v=YgGLl8CanQo", "title": "Still Dre", "id": 1
		}, 
		{
		  "trackHash": "v=ep0hay4Qw54", 
		  "songentry_set": [
		    {
		      "playTime_id": "3", 
		      "playTime": {
			"timeSinceEpoch": "1348574.88", "id": 3
		      }, 
		      "song_id": "3", "id": 7
		    }
		  ], 
		  "artist": "Kendrick Lamar", "url": "http://www.youtube.com/watch?v=ep0hay4Qw54", "title": "HiiiPower", "id": 3
		}
	    ]
	  }'

	 *** Please note for starters, the field timeSinceEpoch was entered through the admin site manually for tests ***

    For those of you script junkies:

      you can achieve the same by:

	via your javaScript console:
	GET:
	  $.ajax({
	    url:"http://192.168.1.23.8008/thebear/songHandler/?sort=artist_r", 
	    method:"GET"
	  });
	POST:
	  $.ajax({
	    url:'http://192.168.1.64:8000/thebear/songHandler', method:'POST',
	    data:"url=http://www.youtube.com/watch?v=wW3jyZRDlII&title=River below&artist=Billy Talent&trackHash=v=wW3jyZRDlII"
	  }); 

	python:
	GET:
	  import urllib.request

	  dataIn = urllib.request.urlopen("http://192.168.1.23.8008/thebear/songHandler/?sort=artist_r")
