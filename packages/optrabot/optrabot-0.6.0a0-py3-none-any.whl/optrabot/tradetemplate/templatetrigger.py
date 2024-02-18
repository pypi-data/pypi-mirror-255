from typing import OrderedDict

class TriggerType:
	External: str = 'external'
	Time: str = 'time'

class TemplateTrigger:
	def __init__(self, triggerdata: OrderedDict) -> None:
		type = triggerdata['type']
		assert type in [TriggerType.External, TriggerType.Time]
		self.type = type
		self.value = triggerdata['value']
		assert self.value != '' and self.value != None