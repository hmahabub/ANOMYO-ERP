from django.db import models
from django.contrib.auth.models import User

#this class is on main database.
class user_info(models.Model):
	user = models.OneToOneField(User, on_delete = models.CASCADE, primary_key = True)
	face = models.ImageField(upload_to="user",default = "default/avatar.png")
	db = models.CharField(max_length=20)
	is_admin = models.BooleanField(default=False)
	is_accountant = models.BooleanField(default=False)
	is_hr = models.BooleanField(default=False)
	is_marchent =models.BooleanField(default=False)

	def __str__(self):
		return self.user.username
	
class messageforus(models.Model):
	name = models.CharField(max_length=80)
	email = models.EmailField()
	message = models.TextField()
	recieved_at = models.DateTimeField(auto_now_add=True)
	is_seen = models.BooleanField(default=False)
#following models will be in personal database

class tmp(models.Model):
	method_choice = [('I','Invoice'),('PR','Payroll_Regular'),('PC','Payroll_Casual'),('CB','Cash_Book'),('BB','Bank_Book')]
	isfor = models.CharField(max_length=40,choices=method_choice)
	src_code = models.TextField()

	def __str__(self):
		return self.isfor



class company(models.Model):
	name = models.CharField(max_length=40, default="Your Company")
	logo = models.ImageField(upload_to="logo",default = "deafult/logo.jpg")
	address = models.TextField()
	account_number = models.CharField(max_length = 20,blank=True)
	contact_1 = models.CharField(max_length = 20,blank=True)
	email = models.EmailField(blank=True)
	website = models.CharField(max_length = 30,blank=True)

class activity_log(models.Model):
	method_choice = [('C','Create'),('U','Update'),('D','Delete')]
	user = models.IntegerField()
	username = models.CharField(max_length=20, default="Unknown")
	description = models.CharField(max_length=100)
	datetime = models.DateTimeField(auto_now_add=True)
	method = models.CharField(max_length = 2, choices= method_choice)

class currency(models.Model):
	name = models.CharField(max_length = 50)
	code = models.CharField(max_length = 6)
	symbol = models.CharField(max_length= 6)
	is_primary = models.BooleanField(default=False)
	def __str__(self):
		return self.name

class currency_rate(models.Model):
	import datetime
	import pytz
	tmz = pytz.timezone('Asia/Dhaka')
	year_choices = [(str(r),str(r)) for r in range(datetime.datetime.now(tmz).date().year,2005,-1)]
	currency = models.ForeignKey( currency, on_delete = models.CASCADE)
	year = models.CharField(max_length = 5, choices=year_choices)
	rate = models.DecimalField(max_digits=13,decimal_places=5)
	def __str__(self):
		return self.currency.name+ "-" + str(self.year)

class department(models.Model):
	name = models.CharField(max_length = 20)

class employee_info(models.Model):
	method_choice = [('S','Single'),('M','Married'),('D','Divorced')]
	name = models.CharField(max_length = 40)
	is_regular = models.BooleanField(default=True)
	department = models.IntegerField(blank=True)
	designation = models.CharField(max_length = 20, blank=True)
	email = models.EmailField( blank=True)
	contact_1 = models.CharField(max_length = 20)
	contact_2 = models.CharField(max_length = 20, blank=True)
	bank = models.CharField(max_length = 40, blank=True)
	account_number = models.CharField(max_length = 20, blank=True)
	is_married = models.CharField(max_length = 10, choices=method_choice)
	present_address = models.TextField( blank=True)
	permanent_address = models.TextField( blank=True)
	emergency_name = models.CharField(max_length = 20, blank=True)
	emergency_relation = models.CharField(max_length = 10, blank=True)
	emergency_contact_1 = models.CharField(max_length = 20, blank=True)
	emergency_contact_2 = models.CharField(max_length = 20, blank=True)
	
		

class client_info(models.Model):
	name = models.CharField(max_length = 40)
	lead = models.IntegerField(blank=True)
	email = models.EmailField(blank=True)
	contact_1 = models.CharField(max_length = 20,blank=True)
	contact_2 = models.CharField(max_length = 20,blank=True)
	website = models.CharField(max_length = 30,blank=True)
	address = models.TextField(blank=True)

class month(models.Model):
	month = models.CharField(max_length = 8, unique=True)
	working_days = models.IntegerField(default = 26)

	@property
	def cash_balance(self):
		total = 0
		for a in self.cash_book_set.all():
			if a.method =="C":
				total += a.amount
			elif a.method == "D":
				total -= a.amount
		return total
	@property
	def bank_balance(self):
		total = 0
		for a in self.bank_book_set.all():
			if a.method =="C":
				total += a.amount
			elif a.method == "D":
				total -= a.amount
		return total

class payroll_full(models.Model):
	employee = models.ForeignKey( employee_info, on_delete = models.CASCADE)
	month = models.ForeignKey(month, on_delete= models.CASCADE)
	attendance = models.IntegerField(default = 0)
	basic = models.DecimalField(max_digits = 9, decimal_places = 2,default = 0)
	medical = models.DecimalField(max_digits = 9, decimal_places = 2,default = 0)
	home = models.DecimalField(max_digits = 9, decimal_places = 2,default = 0)
	conveyance = models.DecimalField(max_digits = 9, decimal_places = 2,default = 0)
	transport = models.DecimalField(max_digits = 9, decimal_places = 2,default = 0)
	others = models.DecimalField(max_digits = 9, decimal_places = 2,default = 0)
	deduction = models.DecimalField(max_digits = 9, decimal_places = 2,default = 0)
	advance = models.DecimalField(max_digits = 9, decimal_places = 2,default = 0)
	editable = models.BooleanField(default=True)

	@property
	def total_payable(self):
		return self.basic + self.medical + self.home + self.conveyance + self.transport + self.others  - self.deduction
	@property
	def net_payable(self):
		return self.total_payable - self.advance

class payroll_part(models.Model):
	employee = models.ForeignKey( employee_info, on_delete = models.CASCADE)
	month = models.ForeignKey(month, on_delete= models.CASCADE)
	work_hours = models.IntegerField(default = 0)
	hours_rate = models.DecimalField(max_digits= 9, decimal_places = 3)
	others = models.DecimalField(max_digits = 9, decimal_places = 2,default = 0)
	advance = models.DecimalField(max_digits = 9, decimal_places = 2,default = 0)
	editable = models.BooleanField(default=True)

	@property
	def overtime(self):
		return self.work_hours * self.hours_rate
	@property
	def total_payable(self):
		return self.overtime + self. others
	@property
	def net_payable(self):
		return self.total_payable - self.advance


class sales(models.Model):
	client = models.ForeignKey( client_info, on_delete = models.CASCADE)
	currency = models.ForeignKey(currency, on_delete=models.SET_NULL, null=True)
	report_no = models.CharField(max_length = 15)
	report_date = models.DateField(default="0000-00-00")
	invoice_no = models.CharField(max_length = 15)
	invoice_date = models.DateField(default="0000-00-00")
	discount = models.DecimalField(max_digits = 9, decimal_places = 2,default = 0)
	recieved = models.DecimalField(max_digits = 9, decimal_places = 2,default = 0)
	editable = models.BooleanField(default=True)
	@property
	def total(self):
		totals = 0
		for s in self.sales_criteria_set.all():
			totals += s.amount
		return totals
	@property
	def net_total(self):
		return self.total - self.discount
	@property
	def due(self):
		return self.total - self.recieved - self.discount
	@property
	def is_paid(self):
		if self.due == 0:
			return True
		return False

 
class sales_criteria(models.Model):
 	sales = models.ForeignKey(sales, on_delete = models.CASCADE)
 	desc = models.CharField(max_length = 80)
 	qtn = models.CharField(max_length = 20)
 	amount = models.DecimalField(max_digits = 9, decimal_places=2,default=0)

class cash_book(models.Model):
 	month = models.ForeignKey(month, on_delete=models.CASCADE)
 	date = models.DateField()
 	prtc = models.CharField(max_length= 300)
 	method = models.CharField(max_length = 1)
 	comment = models.CharField( max_length = 100)
 	amount = models.DecimalField(max_digits=9,decimal_places=2,default=0)

class bank_book(models.Model):
	month = models.ForeignKey(month, on_delete=models.CASCADE)
	date = models.DateField()
	prtc = models.CharField(max_length=300)
	method = models.CharField(max_length = 1)
	amount = models.DecimalField(max_digits=9,decimal_places=2,default=0)
	chq_no = models.CharField(max_length=25,blank=True)
	chq_date = models.DateField(blank=True)
	bank = models.CharField(max_length=80,blank=True)
