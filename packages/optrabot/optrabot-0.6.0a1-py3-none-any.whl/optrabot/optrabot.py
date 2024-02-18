from collections import OrderedDict
import asyncio
import datetime as dt
from fastapi import FastAPI
from ib_insync import *
from loguru import logger
from sqlalchemy.orm import Session
from optrabot import schemas
from optrabot.marketdatatype import MarketDataType
from optrabot.optionhelper import OptionHelper
from optrabot.config import Config
from .tradinghubclient import TradinghubClient
import pkg_resources
from .database import *
from . import crud

class OptraBot():
	def __init__(self, app: FastAPI):
		self.app = app
		self.thc : TradinghubClient = None
		self._tradingEnabled = False
		self._marketDataType : MarketDataType = None
		self.Version = pkg_resources.get_distribution('optrabot').version

	def __setitem__(self, key, value):
		setattr(self, key, value)

	def __getitem__(self, key):
		return getattr(self, key)
	
	async def startup(self):
		logger.info('OptraBot {version}', version=self.Version)
		# Read Config
		conf = Config("config.yaml")
		self['config'] = conf
		conf.logConfigurationData()
		conf.readTemplates()
		updateDatabase()
		await self.connect_ib()
		self.thc = TradinghubClient(self)
		await self.thc.start_polling()
		task = asyncio.create_task(self._statusInfoDelayed())
		task.add_done_callback(self.handleTaskDone)

	async def shutdown(self):
		logger.debug('OptraBot shutdown()')
		await self.thc.shutdown()
		ib: IB = self['ib']
		if ib.isConnected():
			logger.info('Disconnect from IB')
			ib.disconnectedEvent -= self.onDisconnected
			ib.disconnect()

	async def _statusInfoDelayed(self):
		await asyncio.sleep(60*5)
		asyncio.create_task(self._statusInfo())

	async def _statusInfo(self):
		siTradingEnabled = 'Yes' if self._tradingEnabled == True else 'No' 
		siPosition = 'Yes' if self.thc._position == True else 'No'
		siHubConnection = 'OK' if self.thc.isHubConnectionOK() == True else 'Problem!'
		logger.info("Status Info: Hub Connection: {} Trading Enabled: {} Open Position: {}", siHubConnection, siTradingEnabled, siPosition)
		asyncio.create_task(self._statusInfoDelayed())

	async def connect_ib(self):
		logger.debug('Trying to connect with IB ...')
		delaySecs = 30
		ib = IB()
		self['ib'] = ib
		asyncio.create_task(self._connect_ib_task(0, delaySecs))
	
	async def _connect_ib_task(self, attempt: int, delaySecs: int):
		config: Config = self['config']
		twshost = config.get('tws.host')
		if twshost == '':
			twshost = 'localhost'
		try:
			twsport = int(config.get('tws.port'))
		except KeyError as keyErr:
			twsport = 7496
		try:
			twsclient = int(config.get('tws.clientid'))
		except KeyError as keyErr:
			twsclient = 21

		try:
			ib: IB = self['ib']
			ib.errorEvent += self.onErrorEvent
			await ib.connectAsync(twshost, twsport, clientId=twsclient)
			logger.debug("Connected to IB")
			ib.disconnectedEvent += self.onDisconnected
			ib.execDetailsEvent += self.thc.onExecDetailsEvent
			with Session(get_db_engine()) as session:
				for managedAccount in ib.managedAccounts():
					logger.debug('Managed Account: {}', managedAccount)
					known_account = crud.get_account(session, managedAccount)
					if known_account == None:
						logger.debug('Account is new. Adding it to the Database')
						new_account = schemas.AccountCreate( id = managedAccount, name = managedAccount, broker = 'IBKR', pdt=False)
						crud.create_account(session, new_account)
						logger.debug('Account {} created in database.', managedAccount)
			asyncio.create_task(self._checkMarketData())

		except Exception as excp:
			logger.error("Error connecting IB: {}", excp)
			attempt += 1
			logger.error('Connect failed. Retrying {}. attempt in {} seconds', attempt, delaySecs)
			await asyncio.sleep(delaySecs)
			asyncio.create_task(self._connect_ib_task(attempt, delaySecs))

	async def _reconnect_ib_task(self):
		await asyncio.sleep(30)
		await self.connect_ib()

	async def onDisconnected(self):
		logger.warning('Disconnected from TWS, attempting to reconnect in 30 seconds ...')
		self._tradingEnabled = False
		asyncio.create_task(self._reconnect_ib_task())

	async def onErrorEvent(self, reqId: int, errorCode: int, errorString: str, contract: Contract):
		if errorCode in { 202, 399, 2103, 2104, 2105, 2106, 2108, 2109, 2158}:
			# 202: Order wurde storniert z.B. TP order bei OCO, wenn SL Order ausgeführt wurde
			# 399: Warnung das die Order nur während der regulären Handelszeiten ausgeführt wird
			# 2103, 2104, 2105, 2106, 2108, 2158: Marktdatenverbindung ignorieren
			# 2109: Warnhinweis zu einem Orderereignis außerhalb der regulären Handelszeiten
			return
		errorData = {'action': 'errorEvent','reqId':reqId, 'errorCode':errorCode, 'errorString':errorString, 'contract': contract}
		logger.error('IB raised following error: {}', errorData)

	def getMarketDataType(self) -> MarketDataType:
		""" Return the configured Market Data Type
		"""
		if self._marketDataType is None:
			config: Config = self['config']
			try:
				confMarketData = config.get('tws.marketdata')
			except KeyError as keyError:
				confMarketData = 'Delayed'
			self._marketDataType = MarketDataType()
			self._marketDataType.byString(confMarketData)
		return self._marketDataType
	
	async def _checkMarketData(self):
		""" Checks if the Market Data Subscription is as configured.
			It requests SPX Options Market Data and checks if the returned Market Data Type
			is Live Market data. If not, trading is prevented.
		"""
		self._tradingEnabled = False
		ib: IB = self['ib']
		if not ib.isConnected():
			return

		marketDataType = self.getMarketDataType()
		logger.debug("Requesting '{}' data from Interactive Brokers", marketDataType.toString())
		ib.reqMarketDataType(marketDataType.Value)

		spx = Index('SPX', 'CBOE')
		qualifiedContracts = await ib.qualifyContractsAsync(spx)
		[ticker] = await ib.reqTickersAsync(spx)
		ibMarketDataType = MarketDataType(ticker.marketDataType)
		if ibMarketDataType.Value != marketDataType.Value:
			logger.error("IB returned '{}' data for SPX! Trading is deactivated!", ibMarketDataType.toString())
			return
		else:
			logger.info("Received '{}' market data for SPX as expected.", ibMarketDataType.toString())

		spxPrice = ticker.close
		if util.isNan(spxPrice):
			logger.error("IB returned no SPX price but just NaN value for last price. Trading is deactivated!")
			return

		chains = await ib.reqSecDefOptParamsAsync(spx.symbol, '', spx.secType, spx.conId)
		chain = next(c for c in chains if c.tradingClass == 'SPXW' and c.exchange == 'SMART')
		if chain == None:
			logger.error("No Option Chain for SPXW and SMARE found! Not able to trade SPX options!")
			return
		
		current_date = dt.date.today()
		expiration = current_date.strftime('%Y%m%d')
		strikePrice = OptionHelper.roundToStrikePrice(spxPrice)
		logger.info("Requesting Short Put price of strike {}", strikePrice)
		shortPutContract = Option(spx.symbol, expiration, strikePrice, 'P', 'SMART', tradingClass = 'SPXW')
		await ib.qualifyContractsAsync(shortPutContract)
		if not OptionHelper.checkContractIsQualified(shortPutContract):
			return
		ticker = None
		[ticker] = await ib.reqTickersAsync(shortPutContract)
		ibMarketDataType = MarketDataType(ticker.marketDataType)
		if ibMarketDataType.Value != marketDataType.Value:
			logger.error("IB returned '{}' data for SPX Option! Trading is deactivated!", ibMarketDataType.toString())
			return
		else:
			logger.info("Received '{}' market data for SPX Option as expected.", ibMarketDataType.toString())
		
		optionPrice = ticker.close
		if util.isNan(optionPrice):
			logger.error("IB returned no price for the SPX option but just a NaN value. Trading is deactivated!")
			return

		logger.info("Market Data subscription checks passed successfully. Options Trading is enabled.")
		self._tradingEnabled = True

	def isTradingEnabled(self) -> bool:
		""" Returns true if trading is enabled after market data subscription checks have passed.
		"""
		return self._tradingEnabled
	
	@logger.catch
	def handleTaskDone(self, task: asyncio.Task):
		if not task.cancelled():
			taskException = task.exception()
			if taskException != None:
				logger.error('Task Exception occured!')
				raise taskException