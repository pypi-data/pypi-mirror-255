import tempfile
from pathlib import Path
import shutil
from copy import deepcopy
import json,os,base64,time
from datetime import datetime
from sqlalchemy.ext.automap import automap_base
import sqlalchemy
from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *
import zipfile
from colored import Fore,Back,Style

from MobileInventoryCLI.CodeProcessing.RecordCodesAndBarcodes.DB.db import *



class ExtractPkg:
	def __str__(self):
		return "ExtractPkg and Update Config"

	def __init__(self,tbl,error_log,engine):
		self.tbl=tbl
		self.error_log=error_log
		self.engine=engine

		while True:
			try:
				path2bck=input("MobileInventoryCLI-BCK Path[filepath+filename/q/b]: ")
				if path2bck in ['q','quit']:
					exit("user quit!")
				elif path2bck in ['b','back']:
					return
				else:
					path2bck=Path(path2bck)
					if path2bck.exists():
						with zipfile.ZipFile(path2bck,"r") as zip:
							#tmpdir=Path(tempfile.mkdtemp())
							for file in zip.namelist():
								if Path(file).suffix == ".db3":
									x=zip.extract(file,path=str(Path("./system.db").absolute()))
									print(x)
									#update db
									print("opening db for updates")
									with Session(engine) as session:
										while True:
											clear_db=input("Clear DB before adding from file[Y/n/q/b]: ")
											if clear_db.lower() in ['y','yes','ye']:
												session.query(Entry).delete()
												session.commit()
												break
											elif clear_db.lower() in ['q','quit','qui','qu','exit']:
												exit("user quit!")
												break
											elif clear_db.lower() in ['b','ba','bac','back']:
												return
											else:
												break

										l_base=automap_base()
										f=f'sqlite:///{Path(x).absolute()}'
										print(f)
										l_engine=create_engine(f)
										l_base.prepare(autoload_with=l_engine)
										ltbl=l_base.classes

										with Session(l_engine) as ses:
											results=ses.query(ltbl.Item).all()
											print(dir(ltbl))
											for num,item in enumerate(results):
												n=str(item.ImagePath)
												if n != 'None':
													n=str(Path("Images")/Path(Path(n).name))

												entry=Entry(Name=item.Name,Barcode=item.Barcode,Code=item.Code,Price=item.Price,Image=n)
												session.add(entry)
												if num % 100 == 0:
													session.commit()
												print(f'{num+1}/{len(results)}')
											session.commit()
									print("done importing")
								else:
									zip.extract(file,path=str(Path("./system.db").absolute()))
								print("Extracting {s1}{v}{e} to {s2}{vv}{e}".format(v=file,vv=str(Path("./system.db").absolute()),e=Style.reset,s1=Fore.light_green,s2=Fore.red))

					if Path("Images").exists():
						shutil.rmtree("./Images")

					shutil.move("./system.db/Images","./Images")
			except Exception as e:
				print(e)