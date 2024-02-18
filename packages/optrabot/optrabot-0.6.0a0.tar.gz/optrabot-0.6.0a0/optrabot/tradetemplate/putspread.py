from optrabot.tradetemplate.template import *

class PutSpread(Template):
	def __init__(self, name: str) -> None:
		super().__init__(name=name)
		self._type = TemplateType.PutSpread