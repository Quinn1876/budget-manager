from flask import Flask, request, jsonify
from ariadne import load_schema_from_path, make_executable_schema, graphql_sync
from ariadne.explorer import ExplorerGraphiQL
from py3.apps.backend.resolvers import resolvers

type_defs = load_schema_from_path("/app/graphql/schema.graphql")
schema = make_executable_schema(type_defs, *resolvers)
explorer_html = ExplorerGraphiQL().html(None)

app = Flask(__name__)

@app.route("/graphql", methods=["GET"])
def graphql_playground():
    return explorer_html, 200

@app.route("/graphql", methods=["POST"])
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
