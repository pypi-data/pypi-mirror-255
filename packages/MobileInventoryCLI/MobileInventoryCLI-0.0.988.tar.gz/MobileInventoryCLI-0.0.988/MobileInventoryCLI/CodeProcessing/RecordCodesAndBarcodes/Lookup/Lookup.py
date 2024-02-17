from MobileInventoryCLI.CodeProcessing.RecordCodesAndBarcodes.DB.db import *
from colored import Style,Fore,Back

class Lookup:
	def __init__(self,engine,tbl):
		self.engine=engine
		self.tbl=tbl
		self.cmds={
		'1':{
			'cmds':['q','quit'],
			'exec':lambda self=self:exit("user quit!"),
			'desc':'Quit the program!'
		},
		'2':{
			'cmds':['b','back'],
			'exec':None,
			'desc':'Go Back a Menu!'
		},
		'3':{
			'cmds':['3','lu','s'],
			'exec':self.search,
			'desc':'Lookup Codes',
		}

		}
		while True:
			for k in self.cmds:
				print(f"{self.cmds[k]['cmds']} -{self.cmds[k]['desc']}")
			cmd=input("Do What: ")
			for i in self.cmds:
				if cmd.lower() in self.cmds[i]['cmds']:
					if cmd.lower() in self.cmds['2']['cmds']:
						return
					else:
						self.cmds[i]['exec']()
						break



	def search(self):
		while True:
			try:
				code=input("Code to Search [q/b]: ")
				print(f"{Fore.green}{Style.underline}Lookup Initialized...{Style.reset}")
				if code.lower() in self.cmds['1']['cmds']:
					self.cmds['1']['exec']()
				elif code.lower() in self.cmds['2']['cmds']:
					break
				else:
					with Session(self.engine) as session:	
						query=session.query(Entry).filter(or_(Entry.Barcode==code,Entry.Code==code))
						results=query.all()
						for num,r in enumerate(results):
							print(f'{Fore.red}{num}{Style.reset}/{Fore.green}{len(results)}{Style.reset} -> {r}')
						print(f"{Fore.cyan}There were {Fore.green}{Style.bold}{len(results)}{Style.reset} {Fore.cyan}results.{Style.reset}")
			except Exception as e:
				print(e)