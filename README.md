This is a Python script to convert a Swagger specification (developed against version 1.2) to WADL. I had a reason for doing this, is all I'll say.....

Notes:
* Not hugely feature rich;
* Needs some work to sort out error handling;
* Aimed at JSON with no XML support;
* Need to workout a decent referencing mechanism for JSON schema - some exist on the web - currently using a placeholder in the same manner described [here](http://java.dzone.com/articles/json-schema-wadl) but clearly not a complete implementation.

Usage:
```
python swagger2wadl.py [Swagger spec URL] [Real API host/port]
```

