from MobileInventoryCLI.CodeProcessing.RecordCodesAndBarcodes.DB.db import *
from datetime import datetime


class SetCode:
	def setCodeFromBarcode(self):
		print("SetCode")
		if self.engine != None:
			with Session(self.engine) as session:
				self.batchMode=False
				while True:
						batchMode=input("batch mode[y/n]: ")
						if batchMode in ['y','yes']:
							self.batchMode=True
							break
						else:
							self.batchMode=False
							break
				while True:
					try:
						barcode=input("barcode: ")
						if barcode == "#qb":
							break
						#checks needed here
						query=session.query(Entry).filter(Entry.Barcode==barcode)
						results=query.all()
						if len(results) < 1:
							print("No Results")
						else:
							r=None
							if len(results) == 1:
								r=results[0]
							elif len(results) > 1:
								try:
									while True:
										for num,i in enumerate(results):
											print(f"{num} -> {i}")
										select=input("which Entry: ")
										if select == '':
											select=0
											r=results[select]
											break
										if select == "#qb":
											r=None
											break	
										select=int(select)
										r=results[select]
										#print(self.batchMode)
										#if not self.batchMode:
										break
								except Exception as e:
									print(e)
							if r != None:
								ncode=input("New Code #qb = quit batchMode: ")
								if ncode == "#qb":
									break
								r.Code=ncode
								r.user_updated=True
								session.commit()
								session.flush()
								session.refresh(r)
								print(r,self.batchMode)
						if not self.batchMode:
							break
					except Exception as e:
						print(e)

	def __init__(self,engine=None):
		self.engine=engine
		cmds={
		'setCode from Barcode':{
								'cmds':['cfb','1','code<bc'],
								'exec':self.setCodeFromBarcode,
								'desc':"set Code from Barcode"
			},
		'quit':{
				'cmds':["q","quit","2"],
				'exec':lambda self=self:exit("user quit!"),
				'desc':"quit progam"
				},
		'back':{

				'cmds':['b','back','3'],
				'exec':None,
				'desc':"go back a menu if any"
				}
		}

		while True:
			for cmd in cmds:
				print(f"{cmds[cmd]['cmds']} - {cmds[cmd]['desc']}")
			action=input("Do What? : ")
			for cmd in cmds:
				try:
					if action.lower() in cmds[cmd]['cmds'] and cmds[cmd]['exec']!=None:
						cmds[cmd]['exec']()
						break
					elif action.lower() in cmds[cmd]['cmds'] and cmds[cmd]['exec']==None:
						return
					else:
						raise Exception(f"Invalid Command! {action}")
				except Exception as e:
					print(e)

if __name__ == "__main__":
	SetCode()