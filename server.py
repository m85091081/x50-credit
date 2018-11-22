from sanic import Sanic
from sanic_motor import BaseModel
from sanic.response import json 

settings = dict(MOTOR_URI='mongodb://localhost:27017/x50',LOGO=None)
app = Sanic()
app.config.update(settings)
BaseModel.init_app(app)

class User(BaseModel):
    __coll__ = 'credit_system'
    __unique_fields__ = ['barcode']

@app.route('/get_credit',methods=["POST"])
async def get_credit(request):
    json_file = request.json
    cardid = json_file["cardid"]
    print(cardid)
    cur = await User.find_one(dict(cardid = str(cardid)))
    point = int(cur.point)
    return json({'point': point })

@app.route('/create_card',methods=["POST"])
async def create_card(request):
    json_file = request.json
    barcode = json_file["barcode"]
    cardid = json_file["cardid"]
    print(cardid)
    is_uniq = await User.is_unique(doc=dict(barcode=barcode))
    if is_uniq in (True, None):
        await User.insert_one(dict(barcode =int(barcode), point=int(0), cardid=str(cardid)))
        return json({'result': 'ok'})
    else:
        return json({'result': 'nok'})

@app.route('/bid_push',methods=["POST"])
async def bid_push(request):
    json_file = request.json
    cardid = json_file["cardid"]
    bid = json_file["bid"]
    bid = int(bid)
    cur = await User.find_one(dict(cardid = str(cardid)))
    if int(cur.point) - int(bid) < 0 :
        return json({"result":"err","message":"money_fuck"})
    else : 
        await User.update_one(dict(cardid = str(cardid)),{'$inc': {"point":-bid}})
        return json({"result":"ok"})

@app.route('/cash_add',methods=["POST"])
async def cash_add(request):
    json_file = request.json
    cardid = json_file["cardid"]
    cash = json_file["cash"]
    cash = int(cash)
    await User.update_one(dict(cardid = str(cardid)),{'$inc': {"point":cash}})
    return json({"result":"ok"})
    

if __name__ == '__main__':
    app.run(host='0.0.0.0', port = 8080)
