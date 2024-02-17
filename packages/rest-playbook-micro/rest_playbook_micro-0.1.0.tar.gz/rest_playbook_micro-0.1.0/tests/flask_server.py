from flask import Flask, json, Response, request

companies = [{"id": 1, "name": "Company One"},
             {"id": 2, "name": "Company Two"}]

api = Flask(__name__)


@api.route('/200', methods=['GET'])
def get_200():
    return Response("", status=200, mimetype='application/json')


@api.route('/201', methods=['GET'])
def get_201():
    return Response("", status=201, mimetype='application/json')


@api.route('/companies', methods=['GET'])
def get_companies():
    return json.dumps(companies)

@api.route('/', methods=['GET'])
def get_index():
    print(request.data)
    return Response("", status=200, mimetype='application/json')


def run_server():
    api.run(port=3876)


if __name__ == '__main__':
    api.run(port=3876)
