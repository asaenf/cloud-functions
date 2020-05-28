from flask import jsonify, make_response
from google.cloud import firestore


def _get_item_quantity(request):
    content_type = request.headers['content-type']
    if content_type == 'application/json':
        request_json = request.get_json(silent=True)
        if request_json and 'item' in request_json and 'quantity' in request_json:
            item = request_json['item']
            quantity = request_json['quantity']
            return item, quantity
        else:
            raise ValueError("JSON is invalid, or missing property item or quantity")
    else:
        raise ValueError("Content type not allowed: {}".format(content_type))


def get_database_client():
    return firestore.Client()


def get(request):
    """ Method that handles all requests to get items
    from the database"""

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
                return make_response(
                    jsonify(doc.to_dict()), 200)
            else:
                print("Item not found %s" % item)
                return make_response("Item not found %s".format(item), 404)
        else:
            print("Get all items")
            docs = coll_ref.stream()
            all_docs = list()
            for doc in docs:
                doc_dict = {doc.id: doc.to_dict()}
                all_docs.append(doc_dict)
            print("Found %d items" % len(all_docs))
            return make_response(jsonify(all_docs), 200)
    else:
        return make_response("Request type not allowed", 400)


def put(request):
    """ Method that handles all requests add to items
    to the database"""

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
                return make_response("Item already exists %s".format(item), 409)
            else:
                print("Adding item %s with quantity %d" % (item, quantity))
                doc_ref.set({
                    'quantity': quantity
                })
                doc = doc_ref.get()
                return make_response(
                    jsonify(doc.to_dict()), 201)
        except ValueError as e:
            print("Error %s" % e)
            return make_response("Error: %s".format(e), 400)
    else:
        return make_response("Request type not allowed", 400)


def post(request):
    """ Method that handles all requests to update items
    to the database"""

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
                return make_response(
                    jsonify(doc.to_dict()), 200)
            except Exception as not_found:
                return make_response("Error {}".format(not_found), 404)
        except ValueError as e:
            print("Error %s" % e)
            return make_response("Error {}".format(e), 400)
    else:
        return make_response("Request type not allowed", 400)