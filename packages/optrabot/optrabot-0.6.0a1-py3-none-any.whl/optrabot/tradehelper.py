from loguru import logger
from ib_insync import Fill
import re
class TradeHelper:

	@staticmethod
	def getTradeIdFromOrderRef(orderRef: str) -> int:
		""" Extracts the OptraBot Trade Id from the order reference of a fill
		"""
		tradeId = 0
		pattern = r'^OTB\s\((?P<tradeid>[0-9]+)\):[\s0-9A-Za-z]*'
		compiledPattern = re.compile(pattern)
		match = compiledPattern.match(orderRef)
		if match:
			tradeId = int(match.group('tradeid'))
		return tradeId