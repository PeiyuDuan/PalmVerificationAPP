from flask import Flask
from app import palm_print_routes
from flask_swagger_ui import get_swaggerui_blueprint
from flask_cors import CORS

# Initialize Flask app
app = Flask(__name__)
CORS(app)

SWAGGER_URL = '/swagger'  # URL for accessing Swagger UI
API_URL = '/static/swagger.json'  # Path to Swagger JSON

swaggerui_blueprint = get_swaggerui_blueprint(SWAGGER_URL, API_URL, config={'app_name': "Palm Print API"})
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

# Register the Blueprint for routes
app.register_blueprint(palm_print_routes, url_prefix='/api')

if __name__ == '__main__':
    app.run('0.0.0.0', debug=False)
