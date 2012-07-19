class ParseInfo:
	def __init__(self):
		self.texts = []
		self.command = None
		pass
	def __getitem__(self, index):
		return self.texts[index]

	def get_all(self):
		return self.texts

	def get_command(self):
		return self.command

	def addItem(self, text):
		if self.command == None:
			if  self.is_start_with_address == True and self.texts.__len__() == 1:
				self.command = text
				return
			elif self.is_start_with_address == False and self.texts.__len__() == 0:
				self.command = text
				return

		self.texts.append(text)

	def __len__(self):
		return self.texts.__len__()

class Parser:
	def __init__(self):
		pass
	def parser(self, text):
		parse_info = None
		parse_info = ParseInfo()
		parse_info.is_start_with_address = False
		if text[0] == ':':
			parse_info.is_start_with_address = True
			text = text[1:]

		while True:
			if text[0] == ':':
				parse_info.addItem(text)
				break

			nextpos = text.find(' ')
			if nextpos == -1:
				parse_info.addItem(text)
				break
			parse_info.addItem(text[:nextpos])
			text = text[nextpos+1:]
		return parse_info

parser = Parser()

if __name__ == '__main__':
	parseinfo= parser.parser(':zi-test.nexon.com 002 magellan :Your host is zi-test.nexon.com, running version ngircd-18 (x86_64/pc/linux-gnu)')
	getattr(TestHandler, 'on_' + parseinfo.get_command())(testhandler,*parseinfo.get_all())
