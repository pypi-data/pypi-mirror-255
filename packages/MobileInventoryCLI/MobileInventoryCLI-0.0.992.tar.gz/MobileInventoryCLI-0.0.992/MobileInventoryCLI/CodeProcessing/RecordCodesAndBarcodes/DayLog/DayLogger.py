from MobileInventoryCLI.CodeProcessing.RecordCodesAndBarcodes.DB.db import *
from datetime import date

class DayLogger:
	def __init__(self,engine):
		self.engine=engine

		self.cmds={
		'1':{
			'cmds':['q','quit','1'],
			'exec':lambda self=self:exit("user quit!"),
			'desc':"quit program!"
			},
		'2':{
			'cmds':['b','back','2'],
			'exec':None,
			'desc':"Go back a menu!"
		},
		'3':{
			'cmds':['lt','list_today'],
			'exec':self.list_today,
			'desc':f"list entries made today {Fore.yellow}{Style.underline}only.{Style.reset}"
		},
		'4':{
			'cmds':['a','add','acc','accumulate',],
			'exec':lambda self=self:self.modify(mode="accumulate"),
			'desc':f"add entries to DayLog for today and if entry is already id'd by barcode with the date, perform a +=Amount"
		},
		}
		#needs
		##list all entries
		##list all entries for scanned code
		##delete all entries
		##delete entry
		
		while True:
			for i in self.cmds:
				print(f"{self.cmds[i]['cmds']} - {self.cmds[i]['desc']}")
			doWhat=input("Do What: ")
			for num,i in enumerate(self.cmds):
				if doWhat in self.cmds[i]['cmds']:
					if not self.cmds[i]['exec']:
						return
					else:
						self.cmds[i]['exec']()
						break
				else:
					if num >= len(self.cmds):
						print("Not a Valid Cmd!")

	def list_today(self):
		with Session(self.engine) as session:
			query=session.query(DayLog).filter(DayLog.date==date.today())
			results=query.all()
			for i in results:
				print(i)


	def modify(self,mode):
		while True:
			code=input("Code[q/b]: ")
			if code.lower() in self.cmds['1']['cmds']:
				exit("user quit")
			elif code.lower() in self.cmds['2']['cmds']:
				break
			else:
				qty=1
				if mode != 'clear':
					while True:
						qtyS=input("Qty: ")
						if qtyS.lower() in self.cmds['1']['cmds'] and qtyS != '1':
							exit("user quit")
						elif qtyS.lower() in self.cmds['2']['cmds'] and qtyS != '2':
							return
						else:
							try:
								if qtyS != '':
									qty=int(qtyS)
								else:
									pass
									#leave qty as 1
								break
							except Exception as e:
								print(e)

				with Session(self.engine) as session:
					query=session.query(DayLog).filter(DayLog.date==date.today(),DayLog.ScannedCode==code)
					results=query.all()
					if len(results) < 1:
						entries_query=session.query(Entry).filter(or_(Entry.Barcode==code,Entry.Code==code))
						r=entries_query.all()
						if len(r) < 1:
							ndl=DayLog(ScannedCode=code,EntryId=-1,date=datetime.now(),Qty=qty)
							session.add(ndl)
							session.commit()
							session.flush()
							session.refresh(ndl)
							print(ndl)
						elif len(r) == 1:
							ndl=DayLog(ScannedCode=code,EntryId=r[0].EntryId,date=datetime.now(),Qty=qty)
							session.add(ndl)
							session.commit()
							session.flush()
							session.refresh(ndl)
							print(ndl)
						else:
							whichEntry=0
							for num,e in enumerate(r):
								print(f"{Fore.red}{Style.bold}{num}{Style.reset} -> {e}")
							while True:
								try:
									whichEntry=input(f"There {len(r)} Entries for that code. Select one: ")
									whichEntry=int(whichEntry)
									break
								except Exception as e:
									print(e)
							ndl=DayLog(ScannedCode=code,EntryId=r[whichEntry].EntryId,date=datetime.now(),Qty=qty)
							session.add(ndl)
							session.commit()
							session.flush()
							session.refresh(ndl)
							print(ndl)
					elif len(results) >= 1:
						for num,entry in enumerate(results):
							print(f"{Fore.red}{Style.bold}{num}{Style.reset} -> {entry}")
						while True:
							try:
								selection=input(f"Please select an entry to {Fore.yellow}{mode}{Style.reset}: ")
								if selection.lower() in self.cmds['1']['cmds'] and selection != '1':
									exit("user quit!")
								elif selection.lower() in self.cmds['2']['cmds'] and selection != '2':
									return

								selection=int(selection)
								if mode == "accumulate":
									results[selection].addQty(qty)
								elif mode == "deflate":
									results[selection].minusQty(qty)
								elif mode == "clear":
									results[selection].clearQty()
								elif mode == "set":
									results[selection].setQty(qty)
								session.commit()
								session.flush()
								session.refresh(results[selection])
								print(results[selection])
								break
							except Exception as e:
								print(e)

