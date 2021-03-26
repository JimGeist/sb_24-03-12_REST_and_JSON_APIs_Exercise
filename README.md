# sb_24-03-12_REST_and_JSON_APIs_Exercise - Cupcakes


## Assignment Details
Assignment involved creation of an api to perform create, read, update, and delete operations on a database table with cupcake information using Python, Flask, SQL Alchemy, JavaScript, and jQuery. Once the API was in place, a simple web page and route was added. The web page was built out with JavaScript and jQuery and AJAX / axios calls to get all cupcakes and to add new cupcakes. Delete and updates web routes were not built. All api calls were extensively vetted and tested with RESTED. unittests were expanded to include PATCH (update) and DELETE tests.

Add, update and delete functions are in model.py. unittests specific to model.py were not created but there was some coverage in the provided unittests and the update and delete did test to ensure the messages were correctly rendered.

Flask toolbar debugging statements were included but are commented out.
```sh
# from flask_debugtoolbar import DebugToolbarExtension
    . . . .
# debug = DebugToolbarExtension(app)```
# app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
```

A seed file, seed.py, is included with 3 cupcakes. 
- The database name is ```cupcakes```  
- The test database name is ```cupcakes_test```


### ENHANCEMENTS
- Messages and error handling. 


### DIFFICULTIES 
- Getting stuck in my own head and including things that complicatify the assignment. The hopes at times is that some of the things that I am learning will eventually pay off. I was happy to find 
```sh
    {
        validateStatus: function (status) {
            // Resolve when the status code is less than 500
            return status < 500;
        }
    }
```
in axios documentation because, on quite a few exercises, only the successful operations had a return code and I could not figure out why. What good is coding for 404 in the api when axios blocks it!?
- Proper handling of '' and None. The default image was not getting added because '' is not None. 
- I looked into mapping fields. A workaround was to declare an empty dictionary in the model.py that is imported into app.py. A serialize function was created in the Cupcake model and in some cases the serialized dictionary was also used to map values.
- Completely forgot about spreading!
- Some datatype disconnects and how to properly verify that the source fields are the correct type before they are placed in an object and used for an update/delete/create operation. 
- I got hung up in JavaScript because the form default action kept refreshing the page even though I was using code I used before . . and I made the same mistake I made previously too -- the async function needs to have something to wait for (the api call was not yet in place for the add) and the form would submit/reset on the button click. The issue went away once the api call was in place.
- If an API is expecting JSON, is the a way to message back to say they need to use JSON? RESTED was helpful, but the headers for Content-Type = application/json had to get added.



