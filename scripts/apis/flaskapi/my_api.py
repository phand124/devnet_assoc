from flask import Flask, request, jsonify, Response
from classes.mycar import Car
from functools import wraps

#Create a Flask application fromt the Flask class
app = Flask(__name__)

# Create first Flask Route
@app.route('/api', methods=['GET'])
# Hello, world for route
def hello():
    return jsonify({'message': 'Hello from Flask API'}) #Returns 200 - OK if not specified. 

#Create a POST request for a class
@app.route('/api/car', methods=['POST'])
#Take a payload to make a car classed object. 
def handle_car_request():
    data = request.json
    try:
        make = data.get("make")
        model = data.get("model")
        year = data.get("year")

        if not all([make,model,year]):
            return jsonify({'error': 'Missing required fields'}), 400 #Status code - Bad Request
        
        car = Car(make,model,year)
        return jsonify({'car' : car.__dict__}), 201 #Status code - Created
    except Exception as e:
        return jsonify({'error':str(e)}), 500 #Status code - Internal Server Error
            


######################
### BASIC AUTHENTICATION LOGIC ####
######################

VALID_USERNAME = 'admin'
VALID_PASSWORD = 'secret'

def check_auth(username,password):
    return username == VALID_USERNAME and password == VALID_PASSWORD

def authenticate():
    return Response("Could not validate your credentials", 401, {"WWW-Authenticate": 'Basic realm="Login required"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

@app.route('/protected')
@requires_auth
def protected():
    return jsonify({'message': 'You are authenticated'})


if __name__ == "__main__":
    app.run(debug=True)
