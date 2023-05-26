from sqlalchemy.orm import declarative_base
import sqlalchemy as sqla

Base = declarative_base()

class itemTab(Base):
    __tablename__ = 'itemTab'
    itemnum = sqla.Column(sqla.VARCHAR(50), primary_key=True)
    name = sqla.Column(sqla.VARCHAR(100))
    searchname = sqla.Column(sqla.VARCHAR(50))
    pdof = sqla.Column(sqla.VARCHAR(50))
    INT = sqla.Column(sqla.VARCHAR(50))

class TransacHis(Base):
    __tablename__ = 'TransacHis'
    machineID = sqla.Column(sqla.VARCHAR(50))
    timestamp = sqla.Column(sqla.DATETIME(), primary_key=True)
    quantity = sqla.Column(sqla.INTEGER())
    INT = sqla.Column(sqla.VARCHAR(50))
    pdof = sqla.Column(sqla.VARCHAR(50))
    prodord = sqla.Column(sqla.VARCHAR(50))

class machineSTT(Base):
    __tablename__ = 'machineSTT'
    machineID = sqla.Column(sqla.VARCHAR(50))
    timestamp = sqla.Column(sqla.DATETIME(), primary_key=True)
    stt = sqla.Column(sqla.VARCHAR(10))

class PO(Base):
    __tablename__ = 'po'
    prodord = sqla.Column(sqla.VARCHAR(50), primary_key=True)
    itemnum = sqla.Column(sqla.VARCHAR(50))
    name = sqla.Column(sqla.VARCHAR(100))
    resources = sqla.Column(sqla.VARCHAR(50))
    lotnumber = sqla.Column(sqla.VARCHAR(50))
    status = sqla.Column(sqla.VARCHAR(50))
    pool = sqla.Column(sqla.VARCHAR(50))
    quantity = sqla.Column(sqla.INTEGER())
    remaining = sqla.Column(sqla.INTEGER())
    goodquantity = sqla.Column(sqla.INTEGER())
    delivery = sqla.Column(sqla.DATE())
    createddateandtime = sqla.Column(sqla.DATETIME())
    createdby = sqla.Column(sqla.VARCHAR(50))
    searchname = sqla.Column(sqla.VARCHAR(50))
    baseproduct = sqla.Column(sqla.VARCHAR(50))
    size = sqla.Column(sqla.VARCHAR(50))

class ProductDatabase(Base):
    __tablename__ = 'ProductDatabase'
    CodeItem = sqla.Column(sqla.VARCHAR(50), primary_key=True)
    IND = sqla.Column(sqla.VARCHAR(50))
    Item = sqla.Column(sqla.VARCHAR(50))
    ProductOf = sqla.Column(sqla.VARCHAR(50))
    Quantity = sqla.Column(sqla.VARCHAR(50))
    Name = sqla.Column(sqla.VARCHAR(100))
    MaSanPham = sqla.Column(sqla.VARCHAR(50))
    CAT = sqla.Column(sqla.VARCHAR(50))
    INT = sqla.Column(sqla.VARCHAR(50))
    Ma0 = sqla.Column(sqla.VARCHAR(50))
    Size = sqla.Column(sqla.VARCHAR(50))
    IND1 = sqla.Column(sqla.VARCHAR(50))
    Type = sqla.Column(sqla.VARCHAR(50))
    MaTemTui = sqla.Column(sqla.VARCHAR(50))
    QuantityTui = sqla.Column(sqla.VARCHAR(50))
    Ma1 = sqla.Column(sqla.VARCHAR(50))
    Ma2 = sqla.Column(sqla.VARCHAR(50))
    Ma3 = sqla.Column(sqla.VARCHAR(50))
    Ma4 = sqla.Column(sqla.VARCHAR(50))
    Mavachthungdau = sqla.Column(sqla.VARCHAR(50))
    Mavachthungduoi = sqla.Column(sqla.VARCHAR(50))
    Mavachtuidau = sqla.Column(sqla.VARCHAR(50))
    Mavachtuicuoi = sqla.Column(sqla.VARCHAR(50))
