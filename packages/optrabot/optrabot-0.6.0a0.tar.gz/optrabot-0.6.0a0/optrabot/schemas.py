from pydantic import BaseModel
from datetime import datetime, date

class AccountBase(BaseModel):
	id: str
	name: str
	broker: str
	pdt: bool

class AccountCreate(AccountBase):
	pass

class Account(AccountBase):
	class Config:
		orm_mode = True

class TransactionBase(BaseModel):
	tradeid: int
	id: int
	type: str
	sectype: str
	timestamp: datetime
	expiration: date
	strike: float
	contracts: int
	price: float
	fee: float
	commission: float
	notes: str

class TransactionCreate(TransactionBase):
	pass

class Transaction(TransactionBase):
	class Config:
		orm_mode = True

class TradeBase(BaseModel):
	id: int
	account: str
	symbol: str
	strategy: str



class TradeCreate(TradeBase):
	pass

class Trade(TradeBase):
	status: str
	realizedPNL: float
	
	transactions: list[Transaction] = []

	class Config:
		orm_mode = True