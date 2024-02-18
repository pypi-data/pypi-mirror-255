from sqlalchemy.orm import Session
from sqlalchemy import select
from . import models, schemas

def create_account(session: Session, account: schemas.AccountCreate) -> models.Account:
	""" Create a new account in the database
	"""
	db_account = models.Account(id=account.id, name=account.name, broker=account.broker, pdt=account.pdt)
	session.add(db_account)
	session.commit()
	return db_account

def get_account(session: Session, id: str) -> models.Account:
	""" Fetches the data of the given account based on the ID.
	"""
	statement = select(models.Account).filter_by(id=id)
	account = session.scalars(statement).first()
	return account

def get_accounts(session: Session, skip: int = 0, limit: int = 100):
	stmnt = select(models.Account)
	accounts = session.scalars(stmnt).all()
	
	return accounts