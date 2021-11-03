from django.forms import ModelForm
from .models import employee_info, client_info,department, company, payroll_full,payroll_part

class EmployeeForm(ModelForm):
	class Meta:
		model = employee_info
		fields = '__all__'
		labels = {
		'is_regular' : 'Is Full Time',
		'emergency_name' : 'Emergency Contact Person',
		'emergency_relation' : 'Relation',
		'emergency_contact_1' : 'Emergency Contact 1',
		'emergency_contact_2' : 'Emergency Contact 2'
		}
	
	def __init__(self, *args, **kwargs):
		super(EmployeeForm, self).__init__(*args, **kwargs)
		self.fields['name'].widget.attrs.update({'class': 'form-control'})
		self.fields['is_regular'].widget.attrs.update({'class': 'form-check-input mt-0'})
		self.fields['department'].widget.attrs.update({'class': 'form-control','placeholder' :'ex.: Human Resource'})
		self.fields['designation'].widget.attrs.update({'class': 'form-control','placeholder' :'ex.: Senior Officer'})
		self.fields['email'].widget.attrs.update({'class': 'form-control'})
		self.fields['contact_1'].widget.attrs.update({'class': 'form-control'})
		self.fields['contact_2'].widget.attrs.update({'class': 'form-control'})
		self.fields['account_number'].widget.attrs.update({'class': 'form-control'})
		self.fields['bank'].widget.attrs.update({'class': 'form-control'})
		self.fields['is_married'].widget.attrs.update({'class': 'form-control'})
		self.fields['present_address'].widget.attrs.update({'class': 'form-control',"rows":2})
		self.fields['permanent_address'].widget.attrs.update({'class': 'form-control', "rows":2})
		self.fields['emergency_name'].widget.attrs.update({'class': 'form-control'})
		self.fields['emergency_relation'].widget.attrs.update({'class': 'form-control','placeholder' :'ex.: Cousin'})
		self.fields['emergency_contact_1'].widget.attrs.update({'class': 'form-control'})
		self.fields['emergency_contact_2'].widget.attrs.update({'class': 'form-control'})

class ClientForm(ModelForm):
	class Meta:
		model = client_info
		fields = '__all__'
		labels = {
		'name':'Client Name'
		}
	def __init__(self, *args, **kwargs):
		super(ClientForm, self).__init__(*args, **kwargs)
		for field in self.fields.values():
			field.widget.attrs['class'] = 'form-control'
		self.fields['address'].widget.attrs.update({'rows': 3})
class DeptForm(ModelForm):
	class Meta:
		model = department
		fields = "__all__"
		labels = {"name":"Department Name"}
	def __init__(self, *args, **kwargs):
		super(DeptForm, self).__init__(*args, **kwargs)
		self.fields['name'].widget.attrs.update({'class': 'form-control','placeholder' :'ex.: HR'})
class CompanyForm(ModelForm):
	class Meta:
		model = company
		fields = ['name', 'logo','address','account_number','contact_1','email','website']
		labels = {
		'contact_1' : 'Contact',
		}
	def __init__(self, *args, **kwargs):
		super(CompanyForm, self).__init__(*args, **kwargs)
		self.fields['name'].widget.attrs.update({'class': 'form-control'})
		self.fields['logo'].widget.attrs.update({'class': 'form-control'})
		self.fields['address'].widget.attrs.update({'class': 'form-control', 'rows':'2'})
		self.fields['account_number'].widget.attrs.update({'class': 'form-control'})
		self.fields['contact_1'].widget.attrs.update({'class': 'form-control'})
		self.fields['email'].widget.attrs.update({'class': 'form-control'})
		self.fields['website'].widget.attrs.update({'class': 'form-control'})

class PrFullForm(ModelForm):
	class Meta:
		model = payroll_full
		exclude =['employee','month','advance','editable']
		
	def __init__(self, *args, **kwargs):
		super(PrFullForm, self).__init__(*args, **kwargs)
		for field in self.fields.values():
			field.widget.attrs['style'] = 'width: 100px'
			field.widget.attrs['class'] = 'form_input'
class PrPartForm(ModelForm):
	class Meta:
		model = payroll_part
		fields = ["work_hours","hours_rate","others"]
		
	def __init__(self, *args, **kwargs):
		super(PrPartForm, self).__init__(*args, **kwargs)
		for field in self.fields.values():
			field.widget.attrs['style'] = 'width: 100px'
			field.widget.attrs['class'] = 'form_input'

