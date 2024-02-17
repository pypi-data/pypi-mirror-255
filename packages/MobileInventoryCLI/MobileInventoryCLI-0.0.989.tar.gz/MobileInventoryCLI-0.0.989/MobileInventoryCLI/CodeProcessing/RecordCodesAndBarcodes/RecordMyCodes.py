import pandas as pd
import csv
from datetime import datetime
from pathlib import Path
from colored import Fore,Style,Back
from barcode import Code39,UPCA,EAN8,EAN13
import barcode,qrcode,os,sys,argparse
from datetime import datetime,timedelta
import zipfile,tarfile
import base64,json
from ast import literal_eval
import sqlalchemy
from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.ext.declarative import declarative_base as dbase
from sqlalchemy.ext.automap import automap_base
from pathlib import Path
import upcean

print("fores")
from MobileInventoryCLI.CodeProcessing.RecordCodesAndBarcodes.ExtractPkg.ExtractPkg2 import *
from MobileInventoryCLI.CodeProcessing.RecordCodesAndBarcodes.Lookup.Lookup import *
from MobileInventoryCLI.CodeProcessing.RecordCodesAndBarcodes.DayLog.DayLogger import *
from MobileInventoryCLI.CodeProcessing.RecordCodesAndBarcodes.DB.db import *
from MobileInventoryCLI.CodeProcessing.RecordCodesAndBarcodes.ConvertCode.ConvertCode import *
from MobileInventoryCLI.CodeProcessing.RecordCodesAndBarcodes.setCode.setCode import *
from MobileInventoryCLI.CodeProcessing.RecordCodesAndBarcodes.Locator.Locator import *
print("fores")

class Main:
	def __init__(self,engine,tables,error_log):
		self.ExtractPkg=ExtractPkg
		self.DayLogger=DayLogger
		self.Lookup=Lookup
		self.engine=engine
		self.tables=tables
		self.error_log=error_log
		self.modes={
		'1':{
		'cmds':['collect','1','item'],
		'exec':self.startCollectItemMode,
		'desc':'use to collect item data rapidly'
		},
		'2':{
		'cmds':['list','2','+/-','cnt','count'],
		'exec':self.startListMode,
		'desc':"use as a list maker",
		},
		'3':{
		'cmds':['quit','q','3','e'],
		'exec':lambda self=self:exit("User Quit!"),
		'desc':"exit program"
		},
		'4':{
		'cmds':['import','system_import','si','4'],
		'exec':lambda self=self:self.ExtractPkg(tbl=self.tables,engine=self.engine,error_log=self.error_log),
		'desc':"Import Codes from MobileInventory Pro Backup File with *.bck"
		},
		'5':{
		'cmds':['lu','5','lookup','search'],
		'exec':lambda self=self:self.Lookup(engine=engine,tbl=self.tables),
		
		'desc':"Lookup product info!",
			},
		'6':{
		'cmds':['dl','6','daylog',],
		'exec':lambda self=self:self.DayLogger(engine=engine),
		
		'desc':"create a product tracking log for the current date!",
			},
		'7':{
		'cmds':['convert','7','cnvt',],
		'exec':lambda self=self:ConvertCode(),
		
		'desc':"convert codes upce2upca also creates a saved img!",
			},
		'8':{
		'cmds':['setCode','8','setcd',],
		'exec':lambda self=self:SetCode(engine=engine),
		
		'desc':"convert codes upce2upca also creates a saved img!",
			},
			'9':{
		'cmds':['shelf_locator','9','shelf_locator','shf_lct'],
		'exec':lambda self=self:Locator(engine=engine),
		
		'desc':"locate shelf location using barcode to shelf tag code",
			}		
		}
		#
		self.modeString=''.join([f"{Fore.cyan}{self.modes[i]['cmds']} - {self.modes[i]['desc']}{Style.reset}\n" for i in self.modes])
		while True:
			self.currentMode=input(f"which mode do you want to use \n{self.modeString}: ").lower()
			for k in self.modes:
				if self.currentMode in self.modes[k]['cmds']:
					self.modes[k]['exec']()

	def Unified(self,line):
		try:
			return self.unified(line)
		except Exception as e:
			print(e)
			return False


	def unified(self,line):
		args=line.split(",")
		#print(args)
		if len(args) > 1:
			if args[0].lower() in ["remove","rm",'del','delete']:
				try:
					with Session(self.engine) as session:
						result=session.query(Entry).filter(Entry.EntryId==int(args[1])).delete()
						print(result)
						session.commit()
						session.flush()
				except Exeption as e:
					print(e)
				return True
			elif args[0].lower() in ["search","s",'sch']:
				print("Search Mod")
				with Session(self.engine) as session:
					#session.query(Entries).filter
					for field in Entry.__table__.columns:
						if field.name.lower() == args[1].lower():
							print(field)
							if str(field.type) in ['FLOAT','INTEGER']:
								term=0
								if str(field.type) == 'FLOAT':
									term=float(args[2])
								elif str(field.type) == 'INTEGER':
									term=int(args[2])
								operators=['==','!=','<','<=','>','>=','q','b']
								print(f"""
{Fore.yellow}=={Style.reset} -> equal to
{Fore.yellow}=!{Style.reset} -> not equal to
{Fore.yellow}<{Style.reset} -> less than
{Fore.yellow}<={Style.reset} -> less than, or equal to
{Fore.yellow}>{Style.reset} -> greater than
{Fore.yellow}>={Style.reset} -> greater than, or equal to
{Fore.red}q{Style.reset} -> quit
{Fore.red}b{Style.reset} -> back
									""")
								while True:
									operator=input(f"operator {operators}:").lower()
									if operator not in operators:
										continue
									if operator == 'q':
										exit('user quit')
									elif operator == 'b':
										break
									elif operator == '==':
										query=session.query(Entry).filter(field==term)
										save_results(query)
										results=query.all()
										for num,e in enumerate(results):
											print(f"{Fore.red}{Style.bold}{Style.underline}{num}{Style.reset}->{e}")
										print(f"Number of Results: {len(results)}")
										break
									elif operator == '!=':
										query=session.query(Entry).filter(field!=term)
										save_results(query)
										results=query.all()
										for num,e in enumerate(results):
											print(f"{Fore.red}{Style.bold}{Style.underline}{num}{Style.reset}->{e}")
										print(f"Number of Results: {len(results)}")
										break
									elif operator == '<':
										query=session.query(Entry).filter(field<term)
										save_results(query)
										results=query.all()
										for num,e in enumerate(results):
											print(f"{Fore.red}{Style.bold}{Style.underline}{num}{Style.reset}->{e}")
										print(f"Number of Results: {len(results)}")
										break
									elif operator == '<=':
										query=session.query(Entry).filter(field<=term)
										save_results(query)
										results=query.all()
										for num,e in enumerate(results):
											print(f"{Fore.red}{Style.bold}{Style.underline}{num}{Style.reset}->{e}")
										print(f"Number of Results: {len(results)}")
										break
									elif operator == '>':
										query=session.query(Entry).filter(field>term)
										save_results(query)
										results=query.all()
										for num,e in enumerate(results):
											print(f"{Fore.red}{Style.bold}{Style.underline}{num}{Style.reset}->{e}")
										print(f"Number of Results: {len(results)}")
										break
									elif operator == '>=':
										query=session.query(Entry).filter(field>=term)
										save_results(query)
										results=query.all()
										for num,e in enumerate(results):
											print(f"{Fore.red}{Style.bold}{Style.underline}{num}{Style.reset}->{e}")
										print(f"Number of Results: {len(results)}")
										break
								break
							elif str(field.type) == 'VARCHAR':
								operators=['=','%','q','b','!%','!=']
								print(f"""
 {Fore.yellow}={Style.reset} -> entry in Field is exactly
 {Fore.yellow}!={Style.reset} -> entry is not equal to
 {Fore.yellow}%{Style.reset} -> entry is contained within field but is NOT exact to the total of the field
 {Fore.yellow}!%{Style.reset} -> entry is not contained within field but is NOT exact to the total of the field
 {Fore.red}q{Style.reset} -> quit
 {Fore.red}b{Style.reset} -> back
									""")
								while True:
									operator=input(f"operator {operators}:").lower()
									if operator not in operators:
										continue
									if operator == 'q':
										exit('user quit')
									elif operator == 'b':
										break
									elif operator == '=':
										query=session.query(Entry).filter(field==args[2])
										save_results(query)
										results=query.all()
										for num,e in enumerate(results):
											print(f"{Fore.red}{Style.bold}{Style.underline}{num}{Style.reset}->{e}")
										print(f"Number of Results: {len(results)}")
										break
									elif operator == '!=':
										query=session.query(Entry).filter(field!=args[2])
										save_results(query)
										results=query.all()
										for num,e in enumerate(results):
											print(f"{Fore.red}{Style.bold}{Style.underline}{num}{Style.reset}->{e}")
										print(f"Number of Results: {len(results)}")
										break
									elif operator == '%':
										query=session.query(Entry).filter(field.icontains(args[2]))
										save_results(query)
										results=query.all()
										for num,e in enumerate(results):
											print(f"{Fore.red}{Style.bold}{Style.underline}{num}{Style.reset}->{e}")
										print(f"Number of Results: {len(results)}")
										break
									elif operator == '!%':
										query=session.query(Entry).filter(field.icontains(args[2])==False)
										save_results(query)
										results=query.all()
										for num,e in enumerate(results):
											print(f"{Fore.red}{Style.bold}{Style.underline}{num}{Style.reset}->{e}")
										print(f"Number of Results: {len(results)}")
										break

								break
							else:
								print(field.type)

				'''args[1] == fieldname'''
				'''args[2] == value to search for'''
				return True
			elif args[0].lower() in ['name','nm']:
				if len(args) == 2:
					with Session(self.engine) as session:
							result=session.query(Entry).filter(Entry.EntryId==int(args[1])).first()
							if result:
								print(result.Name)
							else:
								print(f"{Fore.yellow}{Style.blink}{Style.bold}Nothing by that EntryId{Style.reset}")	
				elif len(args) == 3:
					with Session(self.engine) as session:
						result=session.query(Entry).filter(Entry.EntryId==int(args[1])).first()
						setattr(result,'Name',str(args[2]))
						session.commit()
						session.flush()
						session.refresh(result)
						print(result.Name)
				return True
			elif args[0].lower() in ['code','cd']:
				if len(args) == 2:
					with Session(self.engine) as session:
							result=session.query(Entry).filter(Entry.EntryId==int(args[1])).first()
							if result:
								print(result.Code)
							else:
								print(f"{Fore.yellow}{Style.blink}{Style.bold}Nothing by that EntryId{Style.reset}")
				elif len(args) == 3:
					with Session(self.engine) as session:
						result=session.query(Entry).filter(Entry.EntryId==int(args[1])).first()
						setattr(result,'Code',str(args[2]))
						
						session.commit()
						session.flush()
						session.refresh(result)
						print(result.Code)
				return True
			elif args[0].lower() in ['barcode','bcd','bd']:
				if len(args) == 2:
					with Session(self.engine) as session:
							result=session.query(Entry).filter(Entry.EntryId==int(args[1])).first()
							if result:
								print(result.Barcode)
							else:
								print(f"{Fore.yellow}{Style.blink}{Style.bold}Nothing by that EntryId{Style.reset}")
				elif len(args) == 3:
					with Session(self.engine) as session:
						result=session.query(Entry).filter(Entry.EntryId==int(args[1])).first()
						setattr(result,'Barcode',str(args[2]))
						
						session.commit()
						session.flush()
						session.refresh(result)
						print(result.Barcode)
				return True
			elif args[0].lower() in ['note','nt']:
				if len(args) == 2:
					with Session(self.engine) as session:
							result=session.query(Entry).filter(Entry.EntryId==int(args[1])).first()
							if result:
								print(result.Note)
							else:
								print(f"{Fore.yellow}{Style.blink}{Style.bold}Nothing by that EntryId{Style.reset}")
				elif len(args) == 3:
					with Session(self.engine) as session:
						result=session.query(Entry).filter(Entry.EntryId==int(args[1])).first()
						setattr(result,'Note',str(args[2]))
						
						session.commit()
						session.flush()
						session.refresh(result)
						print(result.Note)
				return True
			elif args[0].lower() in ['price','pc','prc']:
				if len(args) == 2:

					with Session(self.engine) as session:
							result=session.query(Entry).filter(Entry.EntryId==int(args[1])).first()
							if result:
								print(result.Price)
							else:
								print(f"{Fore.yellow}{Style.blink}{Style.bold}Nothing by that EntryId{Style.reset}")
				elif len(args) == 3:
					with Session(self.engine) as session:
						result=session.query(Entry).filter(Entry.EntryId==int(args[1])).first()
						setattr(result,'Price',float(args[2]))
						
						session.commit()
						session.flush()
						session.refresh(result)
						print(result.Price)
				return True
			elif args[0].lower() in ['img','im','Image']:
				if len(args) == 2:

					with Session(self.engine) as session:
							result=session.query(Entry).filter(Entry.EntryId==int(args[1])).first()
							if result:
								print(result.Image)
							else:
								print(f"{Fore.yellow}{Style.blink}{Style.bold}Nothing by that EntryId{Style.reset}")
				elif len(args) == 3:
					with Session(self.engine) as session:
						result=session.query(Entry).filter(Entry.EntryId==int(args[1])).first()
						try:
							imtext=str(args[2])
							f=importImage(image_dir=img_dir,src_path=imtext,nname=f'{result.EntryId}.png',ow=True)
							setattr(result,'Image',f)
							
							session.commit()
							session.flush()
							session.refresh(result)
							print(result.Image)
						except Exception as e:
							print("No Such EntryId!")
				return True
			elif args[0].lower() in ['rm_img','rm_im','del_img']:
				try:
					with Session(self.engine) as session:
						result=session.query(Entry).filter(Entry.EntryId==int(args[1])).first()
						try:
							imtext=result.Image
							removeImage(image_dir=img_dir,img_name=imtext)
							setattr(result,'Image','')
							
							session.commit()
							session.flush()
							session.refresh(result)
							print(result.Image)
						except Exception as e:
							print(e)
							print("No Such EntryId!")
				except Exception as e:
					print(e)
				return True
			elif args[0].lower() in ['size','sz','sze']:
				if len(args) == 2:
					with Session(self.engine) as session:
							result=session.query(Entry).filter(Entry.EntryId==int(args[1])).first()
							if result:
								print(result.Size)
							else:
								print(f"{Fore.yellow}{Style.blink}{Style.bold}Nothing by that EntryId{Style.reset}")
				elif len(args) == 3:
					with Session(self.engine) as session:
						result=session.query(Entry).filter(Entry.EntryId==int(args[1])).first()
						setattr(result,'Size',str(args[2]))
						
						session.commit()
						session.flush()
						session.refresh(result)
						print(result.Size)
				return True
			elif args[0].lower() in ['shelf','slf','shf','shlf']:
				if len(args) == 2:
					with Session(self.engine) as session:
							result=session.query(Entry).filter(Entry.EntryId==int(args[1])).first()
							if result:
								print(result.Shelf)
							else:
								print(f"{Fore.yellow}{Style.blink}{Style.bold}Nothing by that EntryId{Style.reset}")
				elif len(args) == 3:
					with Session(self.engine) as session:
						result=session.query(Entry).filter(Entry.EntryId==int(args[1])).first()
						setattr(result,'Shelf',int(args[2]))
						
						session.commit()
						session.flush()
						session.refresh(result)
						print(result.Shelf)
				return True
			elif args[0].lower() == ['backroom','bkrm','br']:
				if len(args) == 2:
					with Session(self.engine) as session:
							result=session.query(Entry).filter(Entry.EntryId==int(args[1])).first()
							if result:
								print(result.BackRoom)
							else:
								print(f"{Fore.yellow}{Style.blink}{Style.bold}Nothing by that EntryId{Style.reset}")
				elif len(args) == 3:
					with Session(self.engine) as session:
						result=session.query(Entry).filter(Entry.EntryId==int(args[1])).first()
						setattr(result,'BackRoom',int(args[2]))
						
						session.commit()
						session.flush()
						session.refresh(result)
						print(result.BackRoom)		
				return True
			elif args[0].lower() in ['inlist','il']:
				if len(args) == 2:
					with Session(self.engine) as session:
							result=session.query(Entry).filter(Entry.EntryId==int(args[1])).first()
							if result:
								print(result.InList)
							else:
								print(f"{Fore.yellow}{Style.blink}{Style.bold}Nothing by that EntryId{Style.reset}")
				elif len(args) == 3:
					with Session(self.engine) as session:
						result=session.query(Entry).filter(Entry.EntryId==int(args[1])).first()
						setattr(result,'InList',bool(int(args[2])))
						
						session.commit()
						session.flush()
						session.refresh(result)
						print(result.InList)		
				return True
			elif args[0].lower() in ['display_1','d1']:
				if len(args) == 2:
					with Session(self.engine) as session:
							result=session.query(Entry).filter(Entry.EntryId==int(args[1])).first()
							if result:
								print(result.Display_1)
							else:
								print(f"{Fore.yellow}{Style.blink}{Style.bold}Nothing by that EntryId{Style.reset}")
				elif len(args) == 3:
					with Session(self.engine) as session:
						result=session.query(Entry).filter(Entry.EntryId==int(args[1])).first()
						setattr(result,'Display_1',int(args[2]))
						
						session.commit()
						session.flush()
						session.refresh(result)
						print(result.Display_1)		
				return True
			elif args[0].lower() in ['display_2','d2']:
				if len(args) == 2:
					with Session(self.engine) as session:
							result=session.query(Entry).filter(Entry.EntryId==int(args[1])).first()
							if result:
								print(result.Display_2)
							else:
								print(f"{Fore.yellow}{Style.blink}{Style.bold}Nothing by that EntryId{Style.reset}")
				elif len(args) == 3:
					with Session(self.engine) as session:
						result=session.query(Entry).filter(Entry.EntryId==int(args[1])).first()
						setattr(result,'Display_2',int(args[2]))
						
						session.commit()
						session.flush()
						session.refresh(result)
						print(result.Display_2)		
				return True
			elif args[0].lower() in ['display_3','d3']:
				if len(args) == 2:
					with Session(self.engine) as session:
							result=session.query(Entry).filter(Entry.EntryId==int(args[1])).first()
							if result:
								print(result.Display_3)
							else:
								print(f"{Fore.yellow}{Style.blink}{Style.bold}Nothing by that EntryId{Style.reset}")
				elif len(args) == 3:
					with Session(self.engine) as session:
						result=session.query(Entry).filter(Entry.EntryId==int(args[1])).first()
						setattr(result,'Display_3',int(args[2]))
						
						session.commit()
						session.flush()
						session.refresh(result)
						print(result.Display_3)	
				return True
			elif args[0].lower() in ['display_4','d4']:
				if len(args) == 2:
					with Session(self.engine) as session:
							result=session.query(Entry).filter(Entry.EntryId==int(args[1])).first()
							if result:
								print(result.Display_4)
							else:
								print(f"{Fore.yellow}{Style.blink}{Style.bold}Nothing by that EntryId{Style.reset}")
				elif len(args) == 3:
					with Session(self.engine) as session:
						result=session.query(Entry).filter(Entry.EntryId==int(args[1])).first()
						setattr(result,'Display_4',int(args[2]))
						
						session.commit()
						session.flush()
						session.refresh(result)
						print(result.Display_4)		
				return True
			elif args[0].lower() in ['display_5','d5']:
				if len(args) == 2:
					with Session(self.engine) as session:
							result=session.query(Entry).filter(Entry.EntryId==int(args[1])).first()
							if result:
								print(result.Display_5)
							else:
								print(f"{Fore.yellow}{Style.blink}{Style.bold}Nothing by that EntryId{Style.reset}")
				elif len(args) == 3:
					with Session(self.engine) as session:
						result=session.query(Entry).filter(Entry.EntryId==int(args[1])).first()
						setattr(result,'Display_5',int(args[2]))
						
						session.commit()
						session.flush()
						session.refresh(result)
						print(result.Display_5)		
				return True
			elif args[0].lower() in ['display_6','d6']:
				if len(args) == 2:
					with Session(self.engine) as session:
							result=session.query(Entry).filter(Entry.EntryId==int(args[1])).first()
							if result:
								print(result.Display_6)
							else:
								print(f"{Fore.yellow}{Style.blink}{Style.bold}Nothing by that EntryId{Style.reset}")
				elif len(args) == 3:
					with Session(self.engine) as session:
						result=session.query(Entry).filter(Entry.EntryId==int(args[1])).first()
						setattr(result,'Display_6',int(args[2]))
						
						session.commit()
						session.flush()
						session.refresh(result)
						print(result.Display_6)			
				return True
			elif args[0].lower() in ['inlist','il']:
				if len(args) == 2:
					with Session(self.engine) as session:
							result=session.query(Entry).filter(Entry.EntryId==int(args[1])).first()
							if result:
								print(result.InList)
							else:
								print(f"{Fore.yellow}{Style.blink}{Style.bold}Nothing by that EntryId{Style.reset}")
				elif len(args) == 3:
					with Session(self.engine) as session:
						result=session.query(Entry).filter(Entry.EntryId==int(args[1])).first()
						setattr(result,'InList',bool(int(args[2])))
						
						session.commit()
						session.flush()
						session.refresh(result)
						print(result.InList)	
				return True
			elif args[0].lower() in ['qty','listQty','lq','lstqty']:
				if len(args) == 2:
					with Session(self.engine) as session:
							result=session.query(Entry).filter(Entry.EntryId==int(args[1])).first()
							if result:
								print(result.ListQty)
							else:
								print(f"{Fore.yellow}{Style.blink}{Style.bold}Nothing by that EntryId{Style.reset}")
				elif len(args) == 3:
					with Session(self.engine) as session:
						result=session.query(Entry).filter(Entry.EntryId==int(args[1])).first()
						setattr(result,'ListQty',float(args[2]))
						
						session.commit()
						session.flush()
						session.refresh(result)
						print(result.ListQty)
				return True
				#newbuild	
			elif args[0].lower() in ['location','geo','lctn','ln','l']:
				if len(args) == 2:
					with Session(self.engine) as session:
							result=session.query(Entry).filter(Entry.EntryId==int(args[1])).first()
							if result:
								print(result.Location)
							else:
								print(f"{Fore.yellow}{Style.blink}{Style.bold}Nothing by that EntryId{Style.reset}")
				elif len(args) == 3:
					with Session(self.engine) as session:
						result=session.query(Entry).filter(Entry.EntryId==int(args[1])).first()
						setattr(result,'Location',args[2])
						
						session.commit()
						session.flush()
						session.refresh(result)
						print(result.Location)
				return True
			elif args[0].lower() in ['upce2upca','u2u','e2a']:
				if len(args) == 2:
					with Session(self.engine) as session:
							result=session.query(Entry).filter(Entry.EntryId==int(args[1])).first()
							if result:
								print(result.upce2upca)
							else:
								print(f"{Fore.yellow}{Style.blink}{Style.bold}Nothing by that EntryId{Style.reset}")
				elif len(args) == 3:
					with Session(self.engine) as session:
						result=session.query(Entry).filter(Entry.EntryId==int(args[1])).first()
						setattr(result,'upce2upca',args[2])
						
						session.commit()
						session.flush()
						session.refresh(result)
						print(result.upce2upca)		
				return True
			elif args[0].lower() in ['+','-','=']:
				if len(args) == 3:
					with Session(self.engine) as session:
						result=session.query(Entry).filter(or_(Entry.Barcode==args[2],Entry.Code==args[2])).first()
						if result:
							if args[0] == '-':
								result.ListQty=result.ListQty-float(args[1])
							elif args[0] == '+':
								result.ListQty=result.ListQty+float(args[1])
							elif args[0] == '=':
								result.ListQty=float(args[1])
							result.InList=True
							session.commit()
							session.flush()
							session.refresh(result)
							print(result)		
						else:
							print(f"{Fore.yellow}{Style.blink}{Style.bold}Nothing by that EntryId{Style.reset}")
				else:
					print(f"{Fore.red}[+,-,=]{Style.reset},{Fore.yellow}QTY{Style.reset},{Fore.green}Code/Barcode{Style.reset}")
				return True
			elif args[0].lower() in ["stock_total","st"]:
				with Session(self.engine) as session:
					item=session.query(Entry).filter(Entry.EntryId==int(args[1])).first()
					keys=[f'Display_{i}' for i in range(1,7)]
					keys.append('Shelf')
					keys.append('BackRoom')
					print(keys)
					t=0
					for k in keys:
						curr=getattr(item,k)
						if curr:
							t+=curr
						else:
							setattr(item,k,0)
					setattr(item,'Stock_Total',t)
					
					session.commit()
					session.flush()
					session.refresh(item)
					print(item.Stock_Total)
				return True	
			elif args[0].lower() == "show":
				with Session(self.engine) as session:
						result=session.query(Entry).filter(Entry.EntryId==int(args[1])).all()
						for num,e in enumerate(result):
							print(num,e)
				return True
		elif args[0].lower() in ["list_all","la"]:
			print("-"*10)
			with Session(self.engine) as session:
					result=session.query(Entry).all()
					for num,e in enumerate(result):
						print(num,e)
			print("-"*10)
			return True
		elif args[0].lower() in ["show_list","sl",]:
			print("-"*10)
			with Session(self.engine) as session:
					result=session.query(Entry).filter(Entry.InList==True).all()
					for num,e in enumerate(result):
						print(num,e)
			print("-"*10)
			return True
		elif args[0].lower() in ["clear_list","cl","clrl"]:
			print("-"*10)
			with Session(self.engine) as session:
					result=session.query(Entry).filter(Entry.InList==True).update({'InList':False,'ListQty':0})
					session.commit()
					session.flush()
					print(result)
			print("-"*10)
			return True
		elif args[0].lower() in ["clear_all","ca","clrall"]:
			print("-"*10)
			with Session(self.engine) as session:
					result=session.query(Entry).update(
						{'InList':False,
						'ListQty':0,
						'Shelf':0,
						'Note':'',
						'BackRoom':0
						,'Display_1':0,
						'Display_2':0,
						'Display_3':0,
						'Display_4':0,
						'Display_5':0,
						'Display_6':0,
						'Stock_Total':0,
						})
					session.commit()
					session.flush()
					print(result)
			print("-"*10)
			return True
		elif args[0].lower() in ["clear_all_img","cam","clrallimg"]:
			print("-"*10)
			with Session(self.engine) as session:
					result=session.query(Entry).all()
					for num,item in enumerate(result):
						print(f"{Fore.red}{num} - clearing img field -> {item}")
						if Path(item.Image).exists():
							try:
								if Path(item.Image).is_file():
									Path(item.Image).unlink()
									item.ImagePath=''
									session.commit()
									#session.flush()
									#session.refresh(item)
							except Exception as e:
								item.Image=''
								session.commit()
								#session.flush()
								#session.refresh(item)
						else:
							item.Image=''
							session.commit()
							#session.flush()
							#session.refresh(item)
					session.commit()
					session.flush()
					print(result)
			print("-"*10)
			return True
		elif args[0].lower() in ["save_csv","save","sv"]:
			df=pd.read_sql_table('Entry',self.engine)
			while True:
				try:
					sfile=input(f"{Style.bold}Save Where:{Style.reset} ")
					if sfile == "":
						sfile="./db.csv"
						print(f'{Fore.orange_3}{Path(sfile).absolute()}{Style.reset}')
					if sfile.lower() == 'q':
						exit("user quit!")
					elif sfile.lower() == 'b':
						break
					else:
						df.to_csv(sfile,index=False)
					break
				except Exception as e:
					print(e)
					
			return True
		elif args[0].lower() in ["save_bar","sb","svbr"]:
			df=pd.read_sql_table('Entry',self.engine)
			while True:
				try:
					sfile=input(f"{Style.bold}Save Where:{Style.reset} ")
					if sfile == "":
						sfile="./barcode.csv"
						print(f'{Fore.orange_3}{Path(sfile).absolute()}{Style.reset}')
					if sfile.lower() == 'q':
						exit("user quit!")
					elif sfile.lower() == 'b':
						break
					else:
						df=df['Barcode']
						df.to_csv(sfile,index=False)
					break
				except Exception as e:
					print(e)
					
			return True
		elif args[0].lower() in ["save_bar_cd","sbc","svbrcd"]:
			df=pd.read_sql_table('Entry',self.engine)
			while True:
				try:
					sfile=input(f"{Style.bold}Save Where:{Style.reset} ")
					if sfile == "":
						sfile="./barcode.csv"
						print(f'{Fore.orange_3}{Path(sfile).absolute()}{Style.reset}')
					if sfile.lower() == 'q':
						exit("user quit!")
					elif sfile.lower() == 'b':
						break
					else:
						df=df[['Barcode','Code']]
						df.to_csv(sfile,index=False)
					break
				except Exception as e:
					print(e)
					
			return True
		elif args[0].lower() in ["factory_reset"]:
			#just delete db file and re-generate much simpler
			reInit()
			'''with Session(self.engine) as session:
				done=session.query(Entry).delete()
				session.commit()
				session.flush()
				print(done)'''
			return True
		elif args[0].lower() in ["fields","f","flds"]:
			print("fields in table!")
			for column in Entry.__table__.columns:
				print(column.name)
			return True
		elif args[0].lower() in ['tlm']:
			self.listMode=not self.listMode
			print(f"ListMode is now: {Fore.red}{self.listMode}{Style.reset}")
			return True
		elif args[0].lower() in ['slm']:
			print(f"ListMode is: {Fore.red}{self.listMode}{Style.reset}")
			return True
		elif args[0].lower() in ['sum_list','smzl']:
			with Session(self.engine) as session:
				results=session.query(Entry).filter(Entry.InList==True).all()
				for result in results:
					result.listdisplay()
			
			return True

		return False
	upc_other_cmds=False
	code_other_cmds=False
	def startCollectItemMode(self):
		code=''
		barcode=''
		options=['q - quit - 1','2 - b - back','skip','?']
		while True:
			self.upc_other_cmds=False
			self.code_other_cmds=False
			while True:
				fail=False
				upce=''
				barcode=input(f"{Fore.green_yellow}Barcode{Style.reset}{options}{Style.bold}\n: ")
				print(f"{Style.reset}")
				if barcode.lower() in ['q','quit','1']:
					exit('user quit!')
				elif barcode in ['2','b','back']:
					return
				elif barcode.lower() in ['skip','sk','skp']:
					#barcode='1'*11
					break
				elif barcode.lower() in ['?']:
					self.help()
					self.upc_other_cmds=True
				elif self.Unified(barcode):
					self.upc_other_cmds=True
				elif barcode == '':
					#barcode='0'*11
					break
				else:	
					if len(barcode) == 8:
						try:
							upce=upcean.convert.convert_barcode(intype="upce",outtype="upca",upc=barcode)
						except Exception as e:
							print(e)				
					for num,test in enumerate([UPCA,EAN8,EAN13]):
						try:
							if test == UPCA:
								if len(barcode) >= 11:
									t=test(barcode)	
								elif len(barcode) == 8:
									t=test(upce)
							else:
								t=test(barcode)
								print(t)
							break
						except Exception as e:
							print(e)
							if num >= 3:
								fail=True
				#print("break",fail)
				if fail:
					barcode='0'*11
					break
				else:
					break

			while True:
				fail=False
				code=input(f"{Style.reset}{Fore.green}Code{Style.reset}{options}{Style.bold}\n: ")
				print(f"{Style.reset}")
				if code.lower() in ['q','quit','1']:
					exit('user quit!')
				elif code in ['2','b','back']:
					return
				elif code.lower() in ['skip','sk','skp']:
					#code='1'*8
					break
				elif code.lower() in ['?']:
					self.help()
					self.code_other_cmds=True
				elif self.Unified(code):
					self.code_other_cmds=True
				elif code == '':
					#code='0'*8
					break
				elif code == 'tlm':
					self.listMode=not self.listMode
					print(f"ListMode is now: {Fore.red}{self.listMode}{Style.reset}")
					break
				elif code == 'slm':
					print(f"ListMode is: {Fore.red}{self.listMode}{Style.reset}")
					break
				else:
					fail=False
					for num,test in enumerate([Code39,]):
						try:
							t=test(code,add_checksum=False)
							break
						except Exception as e:
							print(e)
							if num >= 1:
								fail=True
				if fail:
					code='0'*8
					break
				else:
					break
			
			if self.code_other_cmds == False and self.upc_other_cmds == False:
				with Session(self.engine) as session:
					if len(barcode) == 8:
						if code == '#skip':
							try:
								query=session.query(self.tables['Entry']).filter(self.tables['Entry'].barcode.icontains(barcode))
							except Exception as e:
								query=session.query(self.tables['Entry']).filter(self.tables['Entry'].barcode.icontains(upce))
						elif barcode == '#skip':
							query=session.query(self.tables['Entry']).filter(self.tables['Entry'].Code.icontains(upce))
						else:	
							query=session.query(self.tables['Entry']).filter(or_(self.tables['Entry'].Barcode.icontains(barcode),self.tables['Entry'].Code.icontains(code)))

					else:
						print(code,barcode)
						if code in ['#skip','']:
							query=session.query(self.tables['Entry']).filter(self.tables['Entry'].Barcode.icontains(barcode))
						elif barcode == ['#skip','']:
							query=session.query(self.tables['Entry']).filter(self.tables['Entry'].Code.icontains(code))

						else:
							query=session.query(self.tables['Entry']).filter(or_(self.tables['Entry'].Barcode.icontains(barcode),self.tables['Entry'].Code.icontains(code)))
					results=query.all()
					if len(results) < 1:
						print(code)
						print(barcode)
						if (code != '0'*8 and barcode != '0'*11):
							if upce != '':
								entry=self.tables['Entry'](Barcode=upce,Code=barcode,upce2upca=barcode)
							else:
								entry=self.tables['Entry'](Barcode=barcode,Code=code)
							session.add(entry)
							session.commit()
							session.flush()
							session.refresh(entry)
							print(entry)
					else:
						for num,e in enumerate(results):
							print(f"{Fore.light_red}{num}{Style.reset}->{e}")
						while True:
							msg=input(f"Do you want to edit one? if so enter its {Fore.light_red}entry number{Style.reset}(or {Fore.yellow}-1|q|quit{Style.reset} to {Fore.yellow}quit{Style.reset},{Fore.cyan}-2|b|back{Style.reset} to {Fore.cyan}go back{Style.reset}{Fore.green}[or Hit <Enter>]{Style.reset}): ")
							try:								
								if msg == '':
									if self.listMode and len(results) >=1:
										qty=input("How Much to add? ")
										if qty == '':
											qty=1
										qty=float(qty)
										setattr(results[0],'InList',True)
										setattr(results[0],'ListQty',getattr(results[0],'ListQty')+qty)
										session.commit()
										session.flush()
										session.refresh(results[0])
									break
								if msg.lower() in ['-1','q','quit']:
									exit("user quit!")
								elif msg.lower() in ['-2','b','back']:
									break
								else:
									num=int(msg)
									if num < 0:
										raise Exception("Invalid Id:Hidden CMD!")
									else:
										if self.listMode:
											while True:
												qty=input("How Much to add? ")
												print(qty)
												if qty == '':
													qty=1
												qty=float(qty)
												setattr(results[num],'InList',True)
												setattr(results[num],'ListQty',getattr(results[num],'ListQty')+qty)
												session.commit()
												session.flush()
												session.refresh(results[num])
												break
										else:
											print(results[num])
											self.editEntry(session,results[num])
										break
							except Exception as e:
								print(e)
							#use first result as found as entry and display it while incrementing it
							

	listMode=False
	def editEntry(self,session,item):
		print(session,item)
		for column in item.__table__.columns:
			while True:
				try:
					if column.name not in ['Timestamp','EntryId','Image']:
						new_value=input(f"{column.name}->{getattr(item,column.name)}('n','s','d','q'): ")
						if new_value in ['s','n','']:
							break
						elif new_value in ['#clear_field']:
							if isinstance(column.type,Float):
								new_value=float(0)
							elif isinstance(column.type,Integer):
								new_value=int(0)
							elif str(column.type) == "VARCHAR":
								new_value=''
							elif isinstance(column.type,Boolean):
								setattr(item,column.name,0)
						elif new_value in ['d']:
							session.query(self.tables['Entry']).filter(self.tables['Entry'].EntryId==item.EntryId).delete()
							print(item,"Was Deleted!")
							return
						elif new_value in ['b']:
							return	
						elif new_value in ['q']:
							exit("user quit!")

						if isinstance(column.type,Float):
							new_value=float(new_value)
						elif isinstance(column.type,Integer):
							new_value=int(new_value)
						elif str(column.type) == "VARCHAR":
							pass
						elif isinstance(column.type,Boolean):
							if new_value.lower() in ['true','yes','1','y',]:
								setattr(item,column.name,1)
							else:
								setattr(item,column.name,0)
						if str(column.type) not in ['BOOLEAN',]:
							#exit(str((column.name,column.type,isinstance(column.type,Boolean))))
							setattr(item,column.name,new_value)
							
						session.commit()
					break
				except Exception as e:
					print(e)




	def startListMode(self):
		print(f"{Fore.yellow}List Mode{Style.reset}")
		self.listMode=True
		self.startCollectItemMode()

	def help(self):
		with open(Path(__file__).parent/Path("helpMsg.txt"),"r") as msgr:
			msg=f"""{msgr.read().format(Style=Style,Fore=Fore,Back=Back)}"""
			print(msg)
			return msg

def quikRn():
	Main(engine=ENGINE,tables=tables,error_log=Path("error_log.log"))

if __name__ == "__main__":
	Main(engine=ENGINE,tables=tables,error_log=Path("error_log.log"))