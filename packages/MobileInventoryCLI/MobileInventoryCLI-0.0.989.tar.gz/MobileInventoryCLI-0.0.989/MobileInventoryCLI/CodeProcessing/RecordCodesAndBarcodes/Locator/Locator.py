from MobileInventoryCLI.CodeProcessing.RecordCodesAndBarcodes.Locator import *



class Locator:
	def __init__(self,engine):
		self.engine=engine	
		product_barcode=input(f"{Fore.cyan}Barcode{Style.reset}: ")	
		if product_barcode.lower() in ['b','back']:
				return
		elif product_barcode.lower() in ['q','quit']:
			exit("user quit!")
		while True:
			shelf_code=input(f"{Fore.magenta}Shelf Code{Fore.red}[or Barcode to exit]{Style.reset}: ")
			if shelf_code == product_barcode:
				return
			elif shelf_code.lower() in ['q','quit']:
				exit("user quit!")
			elif shelf_code.lower() in ['b','back']:
				return
			
			else:
				with Session(engine) as session:
					query_barcode=session.query(Entry).filter(Entry.Barcode==product_barcode).first()
					if query_barcode:
						query_shelf_code=session.query(Entry).filter(Entry.Code==shelf_code).first()
						if query_shelf_code:
							if query_barcode.EntryId == query_shelf_code.EntryId:
								print(f"{Fore.green_yellow}{Style.bold}Match!{Style.reset}"*30)
								return
							else:
								print(f"{Fore.yellow}{Style.bold}Not a Match!{Style.reset}")
						else:
							print(f"{Fore.yellow}{Style.underline}No Such Shelf Code!")
					else:
						print(f"{Fore.yellow}{Style.underline}No Such Barcode found{Style.reset}")
						return

