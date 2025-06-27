from flask import Flask, request, jsonify
from ariadne import load_schema_from_path, make_executable_schema, graphql_sync
from ariadne.explorer import ExplorerGraphiQL
from flask_cors import CORS, cross_origin
from py3.apps.backend.resolvers import resolvers

type_defs = load_schema_from_path("/app/graphql/schema.graphql")
schema = make_executable_schema(type_defs, *resolvers)
explorer_html = ExplorerGraphiQL().html(None)

app = Flask(__name__)

cors = CORS(app, resources={r"/graphql": {"origins": "http://localhost:3000"}}) # allow CORS from local development
app.config['CORS_HEADERS'] = 'Content-Type'


@app.route("/graphql", methods=["GET"])
def graphql_playground():
    return explorer_html, 200

@app.route("/graphql", methods=["POST"])
@cross_origin()
def graphql_server():
    data = request.get_json()
    success, result = graphql_sync(
        schema,
        data,
        context_value=request,
        debug=True
    )
    status_code = 200 if success else 400
    return jsonify(result), status_code
