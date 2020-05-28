# Google cloud functions

Playing around with google cloud functions by implementing a few simple functions that adds, reads and updates items in\
in a Firestore database.

## Test
```
pytest -s  cloudfunctions/main_test.py
```

## Deploy

cd to package cloudfunctions

```
gcloud functions deploy [function name] --runtime python37 --trigger-http
```                                                                      
for example
```
gcloud functions deploy get --runtime python37 --trigger-http
```   

## Call
To call for example put function
```
curl -H "Authorization: Bearer $(gcloud auth print-identity-token)" -H "Content-Type: application/json" -X PUT -d '{"item":"myitem", "quantity":6}' https://YOUR_REGION-YOUR_PROJECT_ID.cloudfunctions.net/put
```
Requires that key in file credentials.json has been added:

```
gcloud auth activate-service-account --key-file=credentials.json
```