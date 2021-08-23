from flask import Flask,request
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource,Api
from flask_migrate import Migrate
import os

app=Flask(__name__)

app.config['SECRET_KEY'] = 'mysecretkey'
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
Migrate(app,db)
#jwt = JWT(app, authenticate, identity)
api = Api(app)

class MassDetails(db.Model):
    mass_no=db.Column(db.Integer,primary_key=True)
    total_seat=db.Column(db.Integer)
    remainig_seat=db.Column(db.Integer)
    def __init__(self,mass_no,total_seat,remainig_seat):
        self.total_seat=total_seat
        self.mass_no=mass_no
        self.remainig_seat=remainig_seat

    def json(self):
        return {'mass_number':self.mass_no,
                'total_seat':self.total_seat,
                'remainig_seat':self.remainig_seat}

class Massbook(db.Model):
    book_id=db.Column(db.Integer,primary_key=True)
    date=db.Column(db.String(55))
    time=db.Column(db.String(55))
    name=db.Column(db.String(60))
    h_name=db.Column(db.String(80))
    mobile=db.Column(db.Integer)
    mass_no=db.Column(db.Integer)

    def __init__(self,book_id,date,time,name,h_name,mobile,mass_no):
        self.book_id=book_id
        self.date=date
        self.time=time
        self.name=name
        self.h_name=h_name
        self.mobile=mobile
        self.mass_no=mass_no

    def json(self):
        l=self.name
        j=l.split(',')
        j.pop()
        return {'book_id':self.book_id,
                'date':self.date,
                'time':self.time,
                'name':j,
                'h_name':self.h_name,
                'mobile':self.mobile,
                'mass_number':self.mass_no}


########################################################################################
########################################################################################

class MassDeAdd(Resource):
    def post(self):
        mass_no=request.json['mass_no']
        total_seat=request.json['total_seat']
        md=MassDetails(mass_no=mass_no,total_seat=total_seat,remainig_seat=total_seat)
        db.session.add(md)
        db.session.commit()
        return md.json()
class MassDeAdd1(Resource):
    def get(self,mass_no):
        masd=MassDetails.query.filter_by(mass_no=mass_no).first()
        if masd:
            return masd.json()
        else:
            return {'mass_number':'nout found'},404
class Searchmas(Resource):
    def get(self):
        date=request.json["date"]
        getmas=Massbook.query.filter_by(date=date).all()
        if getmas:
            return [masob.json() for masob in getmas]
        else:
            return {'name':'not found'}, 404

#############################################################################

#############################################################################

class MassBookAdd(Resource):
    def post(self):
        book_id=request.json['book_id']
        date=request.json['date']
        time=request.json['time']
        name1=request.json['name']
        h_name=request.json['h_name']
        mobile=request.json['mobile']
        mass_no=request.json['mass_no']
        seat_n=len(name1)
        temp=''
        for i in name1 :
            temp+=i+','
        name=temp
        seat=MassDetails.query.filter_by(mass_no=mass_no).first()
        if seat.remainig_seat>0:
            seat.remainig_seat=seat.remainig_seat-seat_n
            db.session.add(seat)
            db.session.commit()
            mb=Massbook(book_id=book_id,date=date,time=time,name=name,h_name=h_name,mobile=mobile,mass_no=mass_no)
            db.session.add(mb)
            db.session.commit()
            return mb.json()
        else:
            ermsg='Sorry no seat available for Mass number {}'.format(mass_no)
            return {'msg':ermsg},404
    def stringgen(self,nameg):
        temp=''
        for i in nameg :
            temp+=i+','
        return temp
    
class MassBookView(Resource):
    def get(self,book_id):
        pup = Massbook.query.filter_by(book_id=book_id).first()
        if pup:
            return pup.json()
        else:
            return {'name':'not found'}, 404

class AllBookings(Resource):
    #@jwt_required()
    def get(self):
        # return all the puppies 
        puppies = Massbook.query.all()
        # return json of (puppies)
        return [pup.json() for pup in puppies]

class CancelMass(Resource):
    def delete(self):
        book_id=request.json['book_id']
        pup = Massbook.query.filter_by(book_id=book_id).first()

        if pup:
            mn=pup.mass_no
            seat=MassDetails.query.filter_by(mass_no=mn).first()
            l=pup.name
            j=l.split(',')
            j.pop()
            cn=len(j)
            seat.remainig_seat=seat.remainig_seat+cn
            db.session.add(seat)
            db.session.commit()
            db.session.delete(pup)
            db.session.commit()
            return {'msg':"deleted successfuly"}
        else:
            return {'name':'not found'}, 404
@app.route('/')
def info():
    return '<h1>Its works</h1>'

api.add_resource(MassBookAdd,'/Book')
api.add_resource(MassBookView,'/Book/<book_id>')
api.add_resource(AllBookings,'/bookings')
api.add_resource(MassDeAdd,'/admas')
api.add_resource(MassDeAdd1,'/getmas/<mass_no>')
api.add_resource(Searchmas,'/search')
api.add_resource(CancelMass,'/cancel')

if __name__=='__main__':
    app.run(debug=False)