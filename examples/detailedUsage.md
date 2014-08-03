

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

      So to access table 'Song'

      Visit:

	        http://192.168.1.23:8008/thebear/songHandler
      This should return you a JSON object like so: * Columns may vary
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

      + Explanation:
	'sort' => Is any attribute present for the object eg

	  Song contains attributes: Artist, TrackHash, Url, Title, Id

	  Note:
	    + With no key sort key provided, the default key will be Id but reversed so that the newest

	      objects are always displayed first.

	    + To sort in ascending order, the sort-by key will be passed in, as is ie /?sort=foo

	    + To sort in descending/reverse order, the sort-by key is suffixed by _r

	      in as is ie /?sort=foo_r

	  For example:

	    http://192.168.1.23.8008/thebear/songHandler/?sort=id

	  Sorting in reverse order:

	    http://192.168.1.23.8008/thebear/songHandler/?sort=id_r

	'count' => The number of elements present in the DB.

	'format' => Options are 'short' or 'long'

	  'long' implies that any table that contains the current resource as a foreign key will be returned

	  eg: Repeating the query but with the format set to 'long' yields a JSON like so:

	  '{
            dataType: "json",
            mimeType: "application/json",
            meta: {
                sort: "id",
                count: 4,
                offset: 0,
                limit: 4,
                format: "long"
            },
            data: [
                {
                    trackHash: "6U7rdWY06C4",
                    artist: "Stromae",
                    url: "https://www.youtube.com/watch?v=6U7rdWY06C4",
                    title: "Alors On Danse",
                    dateCreated: "Thu Mar 20 06:37:59 2014",
                    playTime: "1395292019.49584",
                    lastEditTime: "Thu Mar 20 06:37:59 2014",
                    id: 1
                },
                {
                    trackHash: "WEkuqv1V4n4",
                    artist: "OutKast",
                    url: "https://www.youtube.com/watch?v=WEkuqv1V4n4",
                    title: "Sorry Miss Jackson",
                    dateCreated: "Thu Mar 20 07:07:33 2014",
                    playTime: "1395292045.49584",
                    lastEditTime: "Thu Mar 20 07:07:33 2014",
                    id: 2
                },
                {
                    trackHash: "f8zR30qTd8Y1",
                    artist: "Billy Talent",
                    url: "https://www.youtube.com/watch?v=f8zR30qTd8Y",
                    title: "River below",
                    dateCreated: "Thu Mar 20 07:08:55 2014",
                    playTime: "1395299310.74394",
                    lastEditTime: "Thu Mar 20 07:08:55 2014",
                    id: 3
                },
                {
                    trackHash: "SlvLUcaRdGI",
                    artist: "Cash Out",
                    url: "https://www.youtube.com/watch?v=SlvLUcaRdGI",
                    title: "Cashin Out",
                    dateCreated: "Thu Mar 20 07:22:16 2014",
                    playTime: "1395299310.74394",
                    lastEditTime: "Thu Mar 20 07:22:16 2014",
                    id: 4
                },
            ],
            currentTime: 1395299339.137992
	    }'

    + To perform a select ie populate only specific attributes:

        supply the keyword 'select' + '=' then a list of attributes separated

        by a comma  eg:

          To populate just  the 'lastEditTime' and 'artist'

            https://192.168.1.23:8008/thebear/songHandler/?select=lastEditTime,artist

            That should return you in the 'meta' data section a list of

            attributes that were allowed for the select


    + For those of you script junkies:

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
        PUT:
          $.ajax({
            url:'http://192.168.1.64:8000/thebear/songHandler', method:'PUT',
            data:"url=http://gutenNacht.com&id=1"
          });
        DELETE:
          $.ajax({
            url:'http://192.168.1.64:8000/thebear/songHandler', method:'PUT',
            data:"id=2&title='Excellence'"
          });

	python:
	GET:
	  import urllib.request

	  getUse = urllib.request.urlopen("http://192.168.1.23.8008/thebear/songHandler/?sort=artist_r")
	  deleteUse = urllib.request.urlopen(
            "http://192.168.1.23.8008/thebear/songHandler/", data=bytes({"method":"DELETE","id":"7"})
          )
	  putUse = urllib.request.urlopen(
            "http://192.168.1.23.8008/thebear/songHandler/", data=bytes({"id":"7", "method":"PUT"})
          )
