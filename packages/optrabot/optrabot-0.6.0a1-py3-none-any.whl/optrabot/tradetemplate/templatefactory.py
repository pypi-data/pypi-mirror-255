from typing import OrderedDict
from loguru import logger
from optrabot.tradetemplate.ironfly import *
from optrabot.tradetemplate.putspread import *
from optrabot.tradetemplate.template import *

class TemplateFactory:

	@staticmethod
	def createTemplate(name: str, data) -> Template:
		""" Creates a template object from the given template configuration of config.yaml
		"""
		template = None
		templateType = data['type']
		match templateType:
			case 'Iron Fly':
				logger.debug('Creating Iron Fly template from config')
				template = IronFly(name)
			case 'Put Spread':
				logger.debug('Creating Put Spread template from config')
				template = PutSpread(name)
			case _:
				logger.error('Template type {} is unknown!', templateType)
				return None

		# Strategy
		try:
			strategy = data['strategy']
			template.setStrategy(strategy)
		except KeyError:
			pass

		# Trigger configuration
		try:
			triggerinfo = data['trigger']
			trigger = TemplateTrigger(triggerinfo)
			template.setTrigger(trigger)
		except KeyError:
			pass

		try:
			account = data['account']
			template.setAccount(account)
		except KeyError:
			pass

		try:
			takeProfit = data['takeprofit']
			template.setTakeProfit(takeProfit)
		except KeyError:
			pass

		try:
			stopLoss = data['stoploss']
			template.setStopLoss(stopLoss)
		except KeyError:
			pass

		try:
			amount = data['amount']
			template.setAmount(amount)
		except KeyError:
			pass

		try:
			minPremium = data['minpremium']
			template.setMinPremium(minPremium)
		except KeyError:
			pass

		try:
			adjustmentStep = data['adjustmentstep']
			template.setAdjustmentStep(adjustmentStep)
		except KeyError:
			pass

		# Stop Loss Adjuster
		try:
			stoplossadjustment = OrderedDict(data['adjuststop'])
		except KeyError as keyErr:
			stoplossadjustment = None
			pass

		if stoplossadjustment:
			try:
				trigger = stoplossadjustment['trigger']
				stop = stoplossadjustment['stop']
				offset = float(stoplossadjustment['offset'])
				adjuster = StopLossAdjuster(reverse=True, trigger=trigger, stop=stop, offset=offset)
				template.setStopLossAdjuster(adjuster)
			except KeyError:
				pass

		return template
			
