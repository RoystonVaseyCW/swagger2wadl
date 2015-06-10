This is a Python script to convert a Swagger specification (developed against version 1.2) to WADL. I had a reason for doing this, is all I'll say.....

Notes:
* Not hugely feature rich 
* Needs some work to sort out error handling:
* Clearly aimed at JSON, need to workout a decent referencing mechanism for JSON schema - some exist on the web - currently using a placeholder in the same way described [here](http://java.dzone.com/articles/json-schema-wadl) but I've yet to add a way that works for my needs

Usage:
```
python swagger2wadl.py [Swagger spec URL] [Real API host/port]
```
