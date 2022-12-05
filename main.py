from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
import random
from flask import jsonify,session
from sqlalchemy.sql.expression import func


app = Flask(__name__)

##Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


##Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self):
    #     # Method 1.
    #     dictionary = {}
    #     # Loop through each column in the data record
    #     for column in self.__table__.columns:
    #         # Create a new dictionary entry;
    #         # where the key is the name of the column
    #         # and the value is the value of the column
    #         dictionary[column.name] = getattr(self, column.name)
    #     return dictionary

     # Method 2. Used Dictionary Comprehension to do the same thing.
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/random")
def random():
    random_cafe = db.session.query(Cafe).order_by(func.random()).first()
    # kjo cafe= perpra duhet patjetr sepse eshte formati i json file
    return jsonify(cafe=random_cafe.to_dict())

@app.route("/all")
def get_all():
    all_cafes={}
    cafes = db.session.query(Cafe).all()
    for cafe in cafes:
        all_cafes[cafe.name]=cafe.to_dict()
    return jsonify(cafe=all_cafes)


#SEARCH FOR A PARTICULAR LOCATION IN THE DB COFFEES
@app.route("/search")
def search():
    location=request.args.get("loc")
    cafes = db.session.query(Cafe).all()
    found_cofes=[]
    for cafe in cafes:
        if cafe.location==location:
            found_cofes.append(cafe.to_dict())
    if len(found_cofes)==0:
        not_found={}
        not_found["Not Found"]="Sorry we can't find a coffee at this specific location."
        found_cofes.append(not_found)
    return jsonify(cafe=found_cofes)

#Duke provuar nje http post request, me ndihmen e app postman qe na krijon nje form virtuale,nkte rast me name "name" dhe "map_url

@app.route("/add",methods=["POST","GET"])
def add():
    if request.method == "POST":
        new_cafe = Cafe(
            name=request.form.get("name"),
            map_url=request.form.get("map_url"),
            img_url=request.form.get("img_url"),
            location=request.form.get("loc"),
            has_sockets=bool(request.form.get("sockets")),
            has_toilet=bool(request.form.get("toilet")),
            has_wifi=bool(request.form.get("wifi")),
            can_take_calls=bool(request.form.get("calls")),
            seats=request.form.get("seats"),
            coffee_price=request.form.get("coffee_price"),
        )
        if new_cafe:
            db.session.add(new_cafe)
            db.session.commit()
            return jsonify(response={"success": "Successfully added the new cafe."})

# A PATCH request route in main.py to handle PATCH requests to our API.

@app.route("/update-price/<int:cafe_id>", methods=["PATCH"])
def patch_new_price(cafe_id):
    new_price = request.args.get("new_price")
    cafe = db.session.query(Cafe).get(cafe_id) #finding a sector in db with id as primary key
    if cafe:
        cafe.coffee_price = new_price
        db.session.commit()
        # Add the code after the jsonify method. 200 = Ok
        return jsonify(response={"success": "Successfully updated the price."}), 200
    else:
        #404 = Resource not found
        return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database."}), 404

# DELETE

@app.route("/report-closed/<int:cafe_id>",methods=["DELETE"])
def delete(cafe_id):
    api_key=request.args.get("api-key")
    if api_key=="TopSecretAPIKey":
        cafe_to_delete = Cafe.query.get(cafe_id)
        if cafe_to_delete:
            db.session.delete(cafe_to_delete)
            return jsonify(response={"success": f"Successfully deleted the cafe with id:{cafe_id} ."}), 200
        else:
            return jsonify(error={"Not Found": "Sorry .A cafe with that cafe id was not found in the database"}), 404
    else:
        return jsonify(error={"Forbidden": "Sorry that's not allowed.Make sure you have the right Api Key"}), 403









if __name__ == '__main__':
    app.run(debug=True)
