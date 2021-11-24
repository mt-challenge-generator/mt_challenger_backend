# MT Challenger backend

To run the backend, clone the repo and then  install the dependencies in _requirements.txt_ (with pip or otherwise). Once everything is installed, set up the backend as follows (in the top directory)
- python3 manage.py makemigrations backend
- python3 manage.py migrate
- python3 manage.py runserver

The server should now start at http://127.0.0.1:8000/

# Endpoints of interest
List test sets: GET http://127.0.0.1:8000/testsets/

List test items in test set: GET http://127.0.0.1:8000/testsets/{testset_id}

List buckets (includes bucket items for each bucket): GET http://127.0.0.1:8000/buckets/

Add bucket item to bucket: POST http://127.0.0.1:8000/bucket-items/:
  {
    "token": "dummy_token",
    "bucket": "http://127.0.0.1:8000/buckets/1/"
  }
 
Add new bucket: POST http://127.0.0.1:8000/buckets/:
  {
    "description": "dummy_bucket",
    "bucket_category": "http://127.0.0.1:8000/bucket-categories/1/"
}

Modify test item: PUT /testitems/{testitem_id}/:
  {
    "generation_time": "2021-11-10",
    "source_sentence": "updated dummy source",
    "testset": "http://127.0.0.1:8000/testsets/1/",
    "phenomenon": "http://127.0.0.1:8000/phenomena/1/"
  }

# How to import an existing test suite
1. Download legacy test suite in JSON format: https://cloud.dfki.de/owncloud/index.php/s/bpGgZ3powDCd6ia
2. Run the following command 
```
  python manage.py import_json testsuite_en-de.json 
```

