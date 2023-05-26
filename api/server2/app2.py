from flask import Flask, request
from flask_restful import Resource, Api
from flask_jsonpify import jsonify
from waitress import serve
import sqlalchemy as sqla, pandas as pd
import datetime, sorcery, pickle, base64
from Table import itemTab, PO, TransacHis, ProductDatabase, machineSTT

app2 = Flask(__name__, static_url_path='/static')
api = Api(app2)

driver = "ODBC Driver 17 for SQL Server"
server = 'sqlserver'
port = 1433
database = "PrintPack"
uid = "ansell"
pwd = "Global5678"
connection_string = f"DRIVER={driver};SERVER={server}, {port};DATABASE={database};UID={uid};pwd={pwd}"
connection_url = sqla.engine.URL.create("mssql+pyodbc", query={"odbc_connect": connection_string})
db_connect = sqla.create_engine(connection_url, poolclass=sqla.pool.NullPool)
Session = sqla.orm.sessionmaker(bind=db_connect)

class POD(Resource):
    def get(self):
        Int = request.args.get('INT')
        pdof = request.args.get('pdof')
        with Session() as session:
            sql1 = session.query(itemTab.searchname).filter(itemTab.INT==Int, itemTab.pdof==pdof).scalar_subquery()
            sql2 = session.query(itemTab.itemnum).filter(itemTab.INT==Int, itemTab.pdof==pdof).scalar_subquery()
            res = pd.read_sql_query(sql=session.query(PO.prodord.label('ProdOrd'), PO.remaining.label('Remaining')).filter(PO.searchname==sql1, PO.itemnum==sql2, PO.remaining!=0).order_by(PO.delivery.asc()).statement,
                                    con=db_connect.connect())
            rm = session.query(sqla.func.sum(TransacHis.quantity).label('Total')).filter(TransacHis.INT==Int, TransacHis.pdof==pdof).first()[0]
        if len(res) > 0:
            if rm is not None:
                for i in range(len(res)):
                    if (abs(rm) >= (res['Remaining'][i])/144):
                        rm = abs(rm) - res['Remaining'][i]/144
                        pon = 'Vượt đơn!'
                    else:
                        rm = res['Remaining'][i]/144 - abs(rm)
                        pon = res['ProdOrd'][i]
                        break
            else:
                rm = res['Remaining'][0]/144
                pon = res['ProdOrd'][0]
        else:
            rm = 0
            pon = 'Không có đơn'
        result = {"remain": rm, "po": pon}
        return jsonify(result)

    def post(self):
        machineID = request.args.get('machineid')
        timestamp = datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S")
        INT = request.args.get('INT')
        prodord = request.args.get('ProdOrd')
        pdof = request.args.get('pdof')
        quantity = -1
        dict_toSql = sorcery.dict_of(machineID, timestamp, INT, pdof, quantity, prodord)
        with Session() as session:
            session.execute(sqla.insert(TransacHis), dict_toSql)
            session.commit()

    def put(self):
        data = request.args.get('data')
        data = pd.DataFrame(pickle.loads(base64.b64decode(data.encode())), dtype=object).reset_index()
        data.columns = ["prodord", "itemnum", "name", "resources", "lotnumber", "status", "pool", "quantity", "remaining", "goodquantity",
                        "delivery", "createddateandtime", "createdby", "searchname", "baseproduct", "size"]
        with Session() as session:
            res = pd.read_sql_query(session.query(PO).statement, con=db_connect.connect())
        res.columns = ["prodord", "itemnum", "name", "resources", "lotnumber", "status", "pool", "quantity", "remaining", "goodquantity",
                        "delivery", "createddateandtime", "createdby", "searchname", "baseproduct", "size"]
        #data = po after -- res = po before
        temp = pd.concat([res, data])
        temp = temp.convert_dtypes()
        temp['delivery'] = pd.to_datetime(temp['delivery'])
        temp['delivery'] = temp['delivery'].dt.strftime("%m/%d/%Y")
        temp['createddateandtime'] = pd.to_datetime(temp['createddateandtime'])
        temp['createddateandtime'] = temp['createddateandtime'].dt.strftime("%m/%d/%Y %H:%M:%S")
        temp = temp.drop_duplicates(subset='prodord', keep='first')
        fin = temp.fillna(' ').to_dict('records')
        with Session() as session:
            session.execute(sqla.delete(PO))
            session.execute(sqla.insert(PO), fin)
            session.commit()

class Database(Resource):
    def get(self):
        if request.args.get('database') == "prod":
            with Session() as session:
                query = pd.read_sql_query(session.query(ProductDatabase).statement, con=db_connect.connect()).to_dict('records')
            result = {"data": query}
            return jsonify(result)
        elif request.args.get('database') == "item":
            with Session() as session:
                query = pd.read_sql_query(session.query(itemTab).statement, con=db_connect.connect()).to_dict('records')
            result = {"data": query}
            return jsonify(result)

    def post(self):
        if request.args.get('database') == "prod":
            data = request.args.get('data')
            data = pd.DataFrame(pickle.loads(base64.b64decode(data.encode())), dtype=object).reset_index()
            data.columns = ["CodeItem", "IND", "Item", "ProductOf", "Quantity", "Name", "MaSanPham",
                "CAT", "INT", "Ma0", "Size", "IND1", "Type", "MaTemTui", "QuantityTui", "Ma1", "Ma2", "Ma3", "Ma4", 
                "Mavachthungdau", "Mavachthungduoi", "Mavachtuidau", "Mavachtuicuoi"]
            data = data.fillna('999999')
            data["CodeItem"] = data["CodeItem"].astype(float).astype("Int64").astype(str)
            data["MaSanPham"] = data["MaSanPham"].astype(float).astype("Int64").astype(str)
            data["MaTemTui"] = data["MaTemTui"].astype(float).astype("Int64").astype(str)
            data = data.replace('999999', ' ').to_dict('records')
            with Session() as session:
                session.execute(sqla.delete(ProductDatabase))
                session.execute(sqla.insert(ProductDatabase), data)
                session.commit()
        elif request.args.get('database') == "item":
            data = request.args.get('data')
            print(data)
            data = pd.DataFrame(pickle.loads(base64.b64decode(data.encode())), dtype=object).reset_index()
            data.columns = ["itemnum", "name", "searchname", "pdof", "INT"]
            data = data.to_dict('records')
            with Session() as session:
                session.execute(sqla.delete(itemTab))
                session.execute(sqla.insert(itemTab), data)
                session.commit()

class machineSTTD(Resource):
    def get(self):
        if request.args.get('type') == "sttnor":
            with Session() as session:
                sub_query = session.query(machineSTT, sqla.func.row_number().over(partition_by=machineSTT.machineID, order_by=machineSTT.timestamp.desc()).label("row_number")).subquery()
                query = pd.read_sql_query(session.query(sub_query).filter(sub_query.c.row_number == 1).statement, con=db_connect.connect()).to_dict('records')
            result = {"data": query}
            return jsonify(result)
        elif request.args.get('type') == "sttall":
            with Session() as session:
                query = pd.read_sql_query(session.query(machineSTT).statement, con=db_connect.connect()).to_dict('records')
            result = {"data": query}
            return jsonify(result)
        elif request.args.get('type') == "proddata":
            lasttime = datetime.datetime.now()
            headtime = lasttime - datetime.timedelta(days=1)
            with Session() as session:
                sub_query = session.query(machineSTT, sqla.func.row_number().over(partition_by=machineSTT.machineID, order_by=machineSTT.timestamp.desc()).label("row_number")).subquery()
                sub_query_machineSTT = session.query(sub_query.c.machineID).filter(sub_query.c.row_number == 1, sub_query.c.stt == "online").subquery()
                sub_query = session.query(TransacHis, sqla.func.row_number().over(partition_by=TransacHis.machineID, order_by=TransacHis.timestamp.desc()).label("row_number")).subquery()
                sub_query_transacHis = session.query(sub_query.c.machineID, sub_query.c.INT, sub_query.c.pdof, sub_query.c.prodord, sub_query.c.quantity).\
                    filter(sub_query.c.row_number == 1, sub_query.c.machineID == sub_query_machineSTT.c.machineID, sub_query.c.timestamp > headtime, sub_query.c.timestamp < lasttime).subquery()
                query_name = session.query(sub_query_transacHis.c.machineID, itemTab.name).\
                    filter(sub_query_transacHis.c.INT == itemTab.INT, sub_query_transacHis.c.pdof == itemTab.pdof).all()
                query_goodquan = session.query(TransacHis.INT, TransacHis.pdof, TransacHis.prodord, sqla.func.sum(TransacHis.quantity).label('goodquan')).\
                    group_by(TransacHis.prodord, TransacHis.INT, TransacHis.pdof).all()
                query_po = session.query(PO.remaining, PO.delivery, sub_query_transacHis.c.machineID, PO.prodord).\
                    filter(PO.prodord == sub_query_transacHis.c.prodord).all()
                query_quan = session.query(TransacHis.prodord, TransacHis.machineID, sqla.func.sum(TransacHis.quantity).label('quan')).group_by(TransacHis.prodord, TransacHis.machineID).\
                    filter(sub_query_transacHis.c.machineID == TransacHis.machineID, sub_query_transacHis.c.prodord == TransacHis.prodord).all()
            data_name = pd.DataFrame(query_name).to_dict('records')
            data_quan = pd.DataFrame(query_quan).to_dict('records')
            data_po = pd.DataFrame(query_po)
            data_goodquan = pd.DataFrame(query_goodquan)
            if not(data_po.empty or data_goodquan.empty):
                datafin = data_po.merge(data_goodquan, how='inner').to_dict('records')
            else:
                datafin = [{}]
            result = {"data": {"data_name": data_name, "data_quan": data_quan, "data_po": datafin}}
            return jsonify(result)
    
    def post(self):
        machineID = request.args.get('machineid')
        timestamp = datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S")
        stt = request.args.get('stt')
        dict_toSql = sorcery.dict_of(machineID, timestamp, stt)
        with Session() as session:
            session.execute(sqla.insert(machineSTT), dict_toSql)
            session.commit()

    def delete(self):
        with Session() as session:
            session.execute(sqla.sql.text('''TRUNCATE TABLE machineSTT'''))
            session.commit()

api.add_resource(POD, '/PO')
api.add_resource(Database, '/Data')
api.add_resource(machineSTTD, '/machineSTT')

@app2.route('/')
def hello_world():
    return "Hello World!2"

if __name__ == '__main__':
    serve(app2, host = "0.0.0.0", port = 5002, url_scheme='http', threads = 17)
#     # app2.run(debug=True)