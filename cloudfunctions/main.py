from flask import jsonify, make_response
from google.cloud import firestore


def _get_item_quantity(request):
    item = _get_item(request)
    request_json = request.get_json(silent=True)
    # we already know content type is json
    if 'quantity' in request_json:
        quantity = request_json['quantity']
        return item, quantity
    else:
        raise ValueError("JSON is invalid, or missing property quantity")


def _get_item(request):
    content_type = request.headers['content-type']
    if content_type == 'application/json':
        request_json = request.get_json(silent=True)
        if request_json and 'item' in request_json:
            item = request_json['item']
            return item
        else:
            raise ValueError("JSON is invalid, or missing property item")
    else:
        raise ValueError("Content type not allowed: {}".format(content_type))


def _add_response_headers(response):
    response.headers['Access-Control-Allow-Origin'] = "https://inventoryapp-276220.web.app"
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    return response


def _handle_preflight_request(request):
    print("Preflight request")
    if request.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': 'https://inventoryapp-276220.web.app',
            'Access-Control-Allow-Methods': 'PUT,GET,POST,DELETE,OPTIONS',
            'Access-Control-Allow-Headers': 'Accept,Content-Type,Authorization,Origin,Referer,User-Agent',
            'Access-Control-Max-Age': '3600',
            'Access-Control-Allow-Credentials': 'true'

        }

        resp = make_response('', 204)
        resp.headers = headers
        return resp


def get_database_client():
    return firestore.Client()


def get(request):
    """ Method that handles all requests to get items
    from the database"""
    try:
        _handle_preflight_request(request)
        db = get_database_client()
        coll_ref = db.collection('items')

        if request.method == 'GET':
            print("GET request received")
            request_args = request.args
            if request_args and 'item' in request_args:
                item = request_args['item']
                print("Item requested %s" % item)
                doc_ref = coll_ref.document(item)
                doc = doc_ref.get()
                if doc.exists:
                    print("Item found %s" % str(doc.to_dict()))
                    return _add_response_headers(make_response(
                        jsonify(doc.to_dict()), 200))
                else:
                    print("Item not found %s" % item)
                    return _add_response_headers(make_response("Item not found %s".format(item), 404))
            else:
                print("Get all items")
                docs = coll_ref.stream()
                all_docs = list()
                for doc in docs:
                    doc_dict = {doc.id: doc.to_dict()}
                    all_docs.append(doc_dict)
                print("Found %d items" % len(all_docs))
                response = make_response(jsonify(all_docs), 200)
                response_with_headers = _add_response_headers(response)
                return response_with_headers
        else:
            return _add_response_headers(make_response("Request type not allowed", 400))
    except Exception as e:
        print(e)


def put(request):
    """ Method that handles all requests add to items
    to the database"""
    try:
        _handle_preflight_request(request)
        db = get_database_client()
        coll_ref = db.collection('items')

        if request.method == 'PUT':
            print("PUT request received")
            try:
                (item, quantity) = _get_item_quantity(request)
                doc_ref = coll_ref.document(item)
                doc = doc_ref.get()
                if doc.exists:
                    print("Item %s already exists, ignoring" % item)
                    return _add_response_headers(make_response("Item already exists %s".format(item), 409))
                else:
                    print("Adding item %s with quantity %d" % (item, quantity))
                    doc_ref.set({
                        'quantity': quantity
                    })
                    doc = doc_ref.get()
                    return _add_response_headers(make_response(
                        jsonify(doc.to_dict()), 201))
            except ValueError as e:
                print("Error %s" % e)
                return _add_response_headers(make_response("Error: %s".format(e), 400))
        else:
            return _add_response_headers(make_response("Request type not allowed", 400))
    except Exception as e:
        print(e)


def post(request):
    """ Method that handles all requests to update items
    to the database"""

    try:
        _handle_preflight_request(request)
        db = get_database_client()
        coll_ref = db.collection('items')

        if request.method == 'POST':
            print("POST request received")
            try:
                (item, quantity) = _get_item_quantity(request)
                print("Updating item %s with quantity %d" % (item, quantity))
                doc_ref = coll_ref.document(item)
                try:
                    doc_ref.update({
                        'quantity': quantity
                    })
                    doc = doc_ref.get()
                    return _add_response_headers(make_response(
                        jsonify(doc.to_dict()), 200))
                except Exception as not_found:
                    return _add_response_headers(make_response("Error {}".format(not_found), 404))
            except ValueError as e:
                print("Error %s" % e)
                return _add_response_headers(make_response("Error {}".format(e), 400))
        else:
            return _add_response_headers(make_response("Request type not allowed", 400))
    except Exception as e:
        print(e)


def delete(request):
    """ Method that handles all requests to delete items
    from the database"""
    try:
        _handle_preflight_request(request)
        db = get_database_client()
        coll_ref = db.collection('items')

        if request.method == 'DELETE':
            print("DELETE request received")
            try:
                item = _get_item(request)
                print("Deleting item %s" % item)
                try:
                    coll_ref.document(item).delete()
                    return _add_response_headers(make_response("OK", 200))
                except Exception as not_found:
                    print("Error %s" % not_found)
                    return _add_response_headers(make_response("Error {}".format(not_found), 404))
            except ValueError as e:
                print("Error %s" % e)
                return _add_response_headers(make_response("Error {}".format(e), 400))
        else:
            return _add_response_headers(make_response("Request type not allowed", 400))
    except Exception as e:
        print(e)
