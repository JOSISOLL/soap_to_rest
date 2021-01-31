from flask import Flask, jsonify, render_template, request, session, url_for, redirect
from zeep import Client, helpers
import json
from functools import wraps
import datetime
import jwt

client = Client(wsdl="http://webservices.oorsprong.org/websamples.countryinfo/CountryInfoService.wso?wsdl")
app = Flask(__name__)

app.config['SECRET_KEY'] = "test_secret_key"

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'x-access-token' in session:
            token = session['x-access-token'] 
        if not token:
            return render_template('authenticate.html', error='Invalid credentials! Please authenticate'), 401

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
            current_user = data['username']
        except:
            return render_template('authenticate.html', error='Invalid credentials! Please authenticate'), 401

        return f(current_user, *args, **kwargs)

    return decorated


@app.route("/", methods=['GET', 'POST'])
def main():
	session.clear()
	error = ''
	try:
		if request.method == "POST":
			if request.form['username'] == "admin":
				
				token = jwt.encode(
                    {'username': request.form['username'], 'exp': datetime.datetime.utcnow(
                    ) + datetime.timedelta(hours=12)},
                    app.config['SECRET_KEY'])
				
				session['x-access-token'] = token.decode('UTF-8')
				
				return redirect(url_for('home'))		
			else:
				error = "Invalid Credential!"
				return render_template("authenticate.html",error=error)
		else:
			return render_template("authenticate.html", error=error)
	except Exception as e:
		error = "Error occured. Please try again!"
		return render_template("authenticate.html", error=error)



@app.route('/home', methods = ['GET', 'POST'])
@token_required
def home(current_user):
	try:
		if request.method == 'POST':
			input_data = request.form['countryCode'].upper()
			response = helpers.serialize_object(client.service.CountryCurrency(input_data))
			result = json.loads(json.dumps(response))
			# Uncomment the next line to get the result as a JSON format
			# return jsonify({'result': result})
			return render_template("home.html", result={'result': result})
		else:
			return render_template("home.html")
	except Exception as e:
		return render_template("authenticate.html")

if __name__ == "__main__":
	app.run(debug=True)