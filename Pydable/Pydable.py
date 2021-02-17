import tkinter
import pyttsx3
import pymsgbox
import requests
import threading
import os
import mysql.connector
from playsound import playsound
from tkinter import ttk
from tkinter import filedialog 
from bs4 import BeautifulSoup 
from PyPDF2 import 	PdfFileReader,PdfFileWriter

#https://www.vocabulary.com/dictionary/word

class DefineObj():
	def __init__ (self):
		self.word_to_define = None

	def search_result(self):
		try:
			div = self.Soup.find("div",class_="section blurb").text #the definition div  in vocabulary.com html
			return div
		except:
			return -1

		
	def display_results(self):
		root = tkinter.Tk()
		root.configure(bg = '#222121')
		results = self.search_result()
		root.title(string = "Results")
		if results != -1: # if a result is found from vocabulary.com.
			header = tkinter.Label(root , 
				text = f"Definition for : {self.word_to_define}", 
				fg ='#3776ab',
				bg = '#222121' ).pack()
			definition = tkinter.Message(root, text = str(results), 
				bg = '#222121',
				fg = "#ffffff").pack()
		else:
			header = tkinter.Label(root , text = f"No results for : {self.word_to_define} " ,
			 fg = '#3776ab' ,
			 bg = '#222121').pack()
		root.mainloop()

	def create_search_parameters(self):
		self.word_to_define = self.user_input.get()
		self.root.destroy()
		link = f"https://www.vocabulary.com/dictionary/{self.word_to_define}"
		source = requests.get(link).text
		self.Soup = BeautifulSoup(source,"lxml")
		self.display_results()


	def display_word_entry(self):#prompting user for a word.
		self.root = tkinter.Tk()
		self.root.configure(bg = '#222121')
		self.root.title(string = "Define A word")
		user_prompt= tkinter.Label(self.root,
			text = "Enter the word of your choice!",
			fg = "#ffffff", 
			bg = '#222121').pack()

		self.user_input = ttk.Entry(self.root)
		self.user_input.pack()
		submit_button = tkinter.Button(self.root, 
			text = "Define",
			bg ='#3776ab',
			command = self.create_search_parameters).pack()

		self.root.mainloop()#block and wait on word to search for.
		




class SqlFunctionality():
	def __init__(self):
		self.database = mysql.connector.connect(host = "localhost" , 
			user= "test" , 
			password = "test", 
			database = "test")
		self.cursor = self.database.cursor()

	def insert_book_name(self,name,error_status):
		if error_status == False:
			self.cursor.execute("INSERT INTO books (bookpath) VALUES (%s)", (name,))	
			self.database.commit()
			playsound("soundeff.mp3")
			pymsgbox.alert(text = "Restart the window to update your books!!" , button = "ok" , title = "Restart the program!")
		else:
			pymsgbox.alert(text = "Issue formatting the book completetly!!", title ="error" , button= "ok")

	def remove_book(self,name):
		self.cursor.execute("DELETE FROM books WHERE bookpath =%s" , (name,))
		self.database.commit()
		os.remove(f"{name}.txt")
		playsound("soundeff.mp3")


	def all_books(self):
		self.cursor.execute("SELECT * FROM books")
		books = []
		for book in self.cursor.fetchall():
			books.append(book[0])
		return books

class MainGuiAndInterface():
	def __init__(self,master):
		#reading functionality
		self.def_obj = DefineObj()
		self.parse_obj = PdfParserAndWriter()
		self.book_creation_error = None
		self.reading = False
		self.placeholder = 0
		self.last_line = None
		self.engine_speed = 125
		self.engine = pyttsx3.init()
		self.books = self.parse_obj.sql_obj.all_books() #this will be a list of all books 
		self.books.insert(0, "Choose a book!!")


		#window
		self.master = master
		master.resizable(width = False , height = False)
		master.grid_rowconfigure(0,weight=1)
		master.grid_rowconfigure(1,weight=1)
		master.grid_rowconfigure(3,weight=1)
		master.grid_columnconfigure(0,weight=1)
		master.grid_columnconfigure(5,weight=1)
		master.geometry("400x500") 
		master.title(string ="Pydable 1.0")
		master.configure(bg = '#222121')

		#real time words
		self.text_content = tkinter.Message(master,
			text="words being read will be here",
			bg ='#222121',
			fg = "#ffffff")

		self.text_content.grid(row = 1 ,columnspan = 6, column = 0,sticky = 'we',padx =10)

		self.line_percentage = tkinter.Label(master,
			text = "Completion: 0%",
			bg ='#222121',
			fg = "#ffffff")
		self.line_percentage.grid(row = 0 ,column =0,columnspan = 3)

		#buttons
		self.play_button = tkinter.Button(master, 
			text="Play",
			bg ='#3776ab' ,
			command = self.begin_reading,
			borderwidth = 0)

		self.define_word_button = tkinter.Button(master  ,
			text = "Define",
			bg ='#3776ab',
			command = self.def_obj.display_word_entry ,
			borderwidth = 0)

		self.add_book_button = tkinter.Button(master,
		 text = "Add Book",
		 bg ='#3776ab',
		 command = self.parse_obj.display_book_name_entry,
		 borderwidth = 0 )

		self.remove_book_button = tkinter.Button(master ,
		 text = "Remove Book",
		 bg = '#8b0000', 
		 fg = "#ffffff",
		 command= self.display_delete_window,
		 borderwidth = 0)

		self.play_button.grid(row =2 , column = 3, padx = 10)
		self.define_word_button.grid(row =2, column=2 )
		self.add_book_button.grid(row = 2, column = 4)
		self.remove_book_button.grid(row = 3 , column = 2, columnspan = 3)
		

		#options
		self.searchvar = tkinter.StringVar()
		self.searchvar.set(self.books[0])

		self.menu = tkinter.OptionMenu(master,self.searchvar, *self.books)
		self.menu.grid(row = 0 ,column =4,columnspan = 2)
		self.menu.configure(background = '#222121',border = 0 , fg = "#00FF00")
		self.menu["menu"].config(bg ='#222121',fg = "#00FF00")
		self.menu["highlightthickness"] = 0

	def display_delete_window(self):
		root = tkinter.Toplevel()
		root.configure(background = '#222121')
		book_to_remove = tkinter.StringVar()
		book_to_remove.set("Choose a book to remove!!")
		menu = tkinter.OptionMenu(root,book_to_remove , *self.books)
		menu.configure(background = '#222121',border = 0 , fg = "#00FF00" )
		menu.pack()
		menu["highlightthickness"] = 0

		remove_button = tkinter.Button(root ,command = lambda: self.parse_obj.sql_obj.remove_book(book_to_remove.get()),
		 text = "Confirm Book Delete" , 
		 bg = '#8b0000' ,
		  border = 0).pack()
		root.mainloop()

	def skip_back(self):
			self.placeholder = self.placeholder - 10

	def skip_forward(self):
			self.placeholder += 10

	def stop_reading(self):
		self.reading = False
		self.engine.stop()
		self.line_percentage.configure(text = "Completion : 0%")
		self.configure_read_buttons(False)
	
	def update_real_time_labels(self,line,lines_len):
		self.text_content.configure(text = line)
		percentage = self.placeholder / lines_len
		self.line_percentage.configure(text = f"Completion: {str(percentage)[0:4]}%")

	def read_thread(self,lines): 
		self.engine.setProperty('rate',self.engine_speed) 

		while self.reading == True:
			try:
				line = lines[self.placeholder]
				lines_len = len(lines)
				self.update_real_time_labels(line ,lines_len)
				self.engine.say(line)
				self.engine.runAndWait()
				self.placeholder += 1
				
			except Exception as e: #out of bounds exception(book finished.)
				self.reading = False
				self.placeholder = 0
				self.line_percentage.configure(text = "Completion : 0%")
				self.engine.say("finished this book")
				self.engine.runAndWait()

	def configure_read_buttons(self , reading_status):
		if reading_status == True:
			self.play_button.configure(text = "Stop", command = self.stop_reading)
			self.define_word_button.configure(text = "<<" ,command = self.skip_back)
			self.add_book_button.configure(text = ">>",command = self.skip_forward)
		else:
			self.play_button.configure(text = "Play", command = self.begin_reading)
			self.define_word_button.configure(text = "Define" ,command = self.def_obj.display_word_entry)
			self.add_book_button.configure(text = "Add Book",command = self.parse_obj.display_book_name_entry)

	def begin_reading(self):
		self.reading = True
		book_name = self.searchvar.get()
		file_name = f"{book_name}.txt"

		try:
	
			with open(file_name , "r") as file:
				lines = file.readlines()
				self.configure_read_buttons(True)
				thread = threading.Thread(target = self.read_thread, args = (lines,))
				thread.start()
		except:
			self.reading = False
			pymsgbox.alert(text = f"Issue reading: {book_name}" , title = "error", button = "ok")

class PdfParserAndWriter():
	def __init__(self):
		self.sql_obj = SqlFunctionality()

	def display_book_name_entry(self):
		self.root = tkinter.Toplevel()
		self.root.configure(background = '#222121')
		user_prompt = tkinter.Label(
			self.root,
			text = 'What is your new book name?',
			bg = '#222121',
			fg = "#ffffff").pack()
		submit_button = tkinter.Button(self.root,
		 text = "Define",
		 bg ='#3776ab',
		 command= self.prompt_and_create_book_file).pack() 
		self.user_input = ttk.Entry(self.root)
		self.user_input.pack()
		self.root.mainloop()

	def write_or_throw(self,current_page,file,error_status,page_num):
		try:
			text = current_page.extractText()
			fixed_page_num = int(page_num) +1
			file.write(f"page {fixed_page_num}")
			file.write(text)
		except :
			error_status = True


	def write_book_contents(self):
		self.root.destroy()
		formatted_bookname = f"{self.book_name}.txt"
		try:
			pdf = PdfFileReader(self.file_path)
			error_status = False
			#start
			with open (formatted_bookname,'w') as file:
				for  page_num in range(pdf.numPages): #for every page
					current_page = pdf.getPage(page_num)
					self.write_or_throw(current_page,file,error_status,page_num)
			self.sql_obj.insert_book_name(self.book_name,error_status)
		except:
			pymsgbox.alert(
				text = "Make Sure you select a pdf file , and make sure it isn't encrypted",
			 	title = "Error" ,
			 	button = "ok")


	def prompt_and_create_book_file(self):
		self.book_name = self.user_input.get()
		self.root.destroy
		self.file_path = filedialog.askopenfilename( 
		initialdir= "/",
		title='Please select a file')
		self.write_book_contents()

root = tkinter.Tk()
MainGuiAndInterface(root)
root.mainloop()