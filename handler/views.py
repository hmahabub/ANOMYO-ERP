from django.shortcuts import render, redirect
from django.core.paginator import Paginator, EmptyPage
from django.contrib import messages
from django.contrib.auth.models import auth, User
from .models import *
from .form import *
from django.http import HttpResponse, JsonResponse
import datetime
from pathlib import Path
import json
import pytz
tmz = pytz.timezone('Asia/Dhaka')
BASE_DIR = Path(__file__).resolve().parent.parent

def db_name(user_id):
    user = User.objects.get(id=user_id)
    database = user_info.objects.using('default').get(user_id=user_id)
    return database.db
def logs_item(page_num,item,db):
    items = activity_log.objects.order_by('-id').using(db)
    p = Paginator(items, item)
    try:
        data = p.page(page_num)
    except EmptyPage:
        data = p.page(1)
    return data

def get_currency_rate(db,year,usd_currency):

    def c_r(year, y_list, r_list):
        if year in y_list:
            return r_list[y_list.index(year)]
        else:
            comparison_list =[]
            year_list = []
            for a in y_list:
                comparison_list.append(abs(int(a)-int(year)))
                year_list.append(a)
            return r_list[y_list.index(y_list[comparison_list.index(min(comparison_list))])]

    u_c = currency.objects.using(db).get(id = usd_currency)
    y_list = [a.year for a in u_c.currency_rate_set.all()]
    r_list = [a.rate for a in u_c.currency_rate_set.all()]
    usd_rate = c_r(year,y_list,r_list)

    
    p_c = currency.objects.using(db).get(is_primary = True)
    y_list = [a.year for a in p_c.currency_rate_set.all()]
    r_list = [a.rate for a in p_c.currency_rate_set.all()]
    prime_rate = c_r(year,y_list,r_list)

    return prime_rate / usd_rate


def forward_cash(db,mnth):
    dataset = mnth.cash_book_set.all().order_by("id")
    today = datetime.datetime.now(tmz).date()
    if len(dataset) == 0:
        first = today.replace(day=1)
        lastMonth = first - datetime.timedelta(days=1)
        last_month = lastMonth.strftime("%Y-%m")
        forward_balance = 0
        if month.objects.using(db).filter(month=last_month).exists():
            lst_mnth =  month.objects.using(db).get(month=last_month)
            new_dataset = lst_mnth.cash_book_set.all()
            for a in new_dataset:
                if a.method == "C":
                    forward_balance += a.amount
                elif a.method == "D":
                    forward_balance -= a.amount
        c = cash_book(month=mnth,date=today,prtc="Forward balance from previous month", method = "C", amount=forward_balance)
        c.save(using=db)
def forward_bank(db,mnth):
    dataset = mnth.bank_book_set.all().order_by("id")
    today = datetime.datetime.now(tmz).date()
    if len(dataset) == 0:
        first = today.replace(day=1)
        lastMonth = first - datetime.timedelta(days=1)
        last_month = lastMonth.strftime("%Y-%m")
        forward_balance = 0
        if month.objects.using(db).filter(month=last_month).exists():
            lst_mnth =  month.objects.using(db).get(month=last_month)
            new_dataset = lst_mnth.bank_book_set.all()
            for a in new_dataset:
                if a.method == "C":
                    forward_balance += a.amount
                elif a.method == "D":
                    forward_balance -= a.amount
        b = bank_book(month=mnth,date=today,prtc="Forward balance from previous month", method = "C",chq_date=today, amount=forward_balance)
        b.save(using=db)
def create_payroll_full(db,a,last_month):
    # checking if employee have any entry on that particular month
    if not payroll_full.objects.using(db).filter(employee = a, month= last_month).exists():
        # Calculating Second last month from last month
        mnths = ['12','01','02','03','04','05','06','07','08','09','10','11','12']
        if int(last_month.month[5:]) == 1:
            s_l_month = str(int(last_month.month[:4]) - 1) +"-12"
        else:
            s_l_month = last_month.month[:5] + mnths[int(last_month.month[5:]) - 1]

        if payroll_full.objects.using(db).filter(employee = a, month__month= s_l_month).exists():
            s_entry = payroll_full.objects.using(db).get(employee = a, month__month= s_l_month)
            f = payroll_full(employee = a, month= last_month,attendance = s_entry.attendance, basic = s_entry.basic,medical = s_entry.medical,home = s_entry.home,conveyance = s_entry.conveyance, transport = s_entry.transport,others = s_entry.others,deduction = s_entry.deduction)
            f.save(using=db)
        else:
            f = payroll_full(employee = a, month= last_month,attendance = 0, basic = 0,medical = 0,home = 0,conveyance = 0, transport = 0,others = 0,deduction = 0)
            f.save(using=db)
def create_payroll_part(db,i,last_month):
    if not payroll_part.objects.using(db).filter(employee = int(i), month= last_month).exists():
        a = employee_info.objects.using(db).get(id=int(i))
        mnths = ['12','01','02','03','04','05','06','07','08','09','10','11','12']
        if int(last_month.month[5:]) == 1:
            s_l_month = str(int(last_month.month[:4]) - 1) +"-12"
        else:
            s_l_month = last_month.month[:5] + mnths[int(last_month.month[5:]) - 1]
        
        if payroll_part.objects.using(db).filter(employee = a, month__month= s_l_month).exists():
            s_entry = payroll_part.objects.using(db).get(employee = a, month__month= s_l_month)
            f = payroll_part(employee = a, month= last_month,work_hours = s_entry.work_hours, hours_rate = s_entry.hours_rate, others = s_entry.others)
            f.save(using=db)
        else:
            f = payroll_part(employee = a, month= last_month,work_hours = 0, hours_rate = 0, others = 0)
            f.save(using=db)
def create_templates(db):
    inv_tmp_list = tmp.objects.filter(isfor="I")
    pr_reg_list = tmp.objects.filter(isfor="PR")
    pr_csl_list = tmp.objects.filter(isfor="PC")
    bank_book_list = tmp.objects.filter(isfor="BB")
    cash_book_list = tmp.objects.filter(isfor="CB")
    if not tmp.objects.using(db).filter(isfor="I").exists():
        f = tmp(isfor="I",src_code=inv_tmp_list.first().src_code)
        f.save(using=db)
    if not tmp.objects.using(db).filter(isfor="PR").exists():
        f = tmp(isfor="PR",src_code=pr_reg_list.first().src_code)
        f.save(using=db)
    if not tmp.objects.using(db).filter(isfor="PC").exists():
        f = tmp(isfor="PC",src_code=pr_csl_list.first().src_code)
        f.save(using=db)
    if not tmp.objects.using(db).filter(isfor="BB").exists():
        f = tmp(isfor="BB",src_code=bank_book_list.first().src_code)
        f.save(using=db)
    if not tmp.objects.using(db).filter(isfor="CB").exists():
        f = tmp(isfor="CB",src_code=cash_book_list.first().src_code)
        f.save(using=db)
    

def render_to_pdf(template_src, context_dict={}):
    from io import BytesIO
    from django.template import Context, Template
    from xhtml2pdf import pisa
    template = Template(template_src)
    context = Context(context_dict)
    html = template.render(context)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None

    

def get_summary(db,year):
    sale = 0
    sale = '{0:.2f}'.format(sum([a.recieved * get_currency_rate(db,year,a.currency.id) for a in sales.objects.using(db).filter(invoice_date__contains=year)]))
    expense = 0
    expense = sum([a.amount for a in cash_book.objects.using(db).filter(month__month__contains=year,method="D")]) + sum([a.amount for a in bank_book.objects.using(db).filter(month__month__contains=year,method="D")]) 
    revenue = float(sale) - float(expense)
    sales_data = sales.objects.using(db).filter(invoice_date__contains = year)
    invoice_no = len(sales_data)
    clients = []
    sum_of_sales =[]
    for a in sales_data:
        if a.client not in clients:
            sum_of_sales.append(sum([y.total*get_currency_rate(db,year,y.currency.id) for y in sales_data.filter(client = a.client)]))
            clients.append(a.client)
    best_client = ""
    best_client_sales = 0
    if sales_data:
        best_client = clients[sum_of_sales.index(max(sum_of_sales))].name
        best_client_sales = '{0:.2f}'.format(max(sum_of_sales))

    return sale,expense,revenue,invoice_no,best_client,best_client_sales






def home(request):
    if request.user.is_authenticated:
        user_id = request.user.id
        db = db_name(user_id)
        year = datetime.datetime.now(tmz).date().year
        sale,expense,revenue,invoice_no,best_client,best_client_sales = get_summary(db,year)
        logs = logs_item(1,7,db)
        if not company.objects.all().using(db).first():
            c = company(name="My Company",address="My Address")
            c.save(using=db)
        if currency.objects.using(db).filter(is_primary=True).exists():
            crncy = currency.objects.using(db).filter(is_primary=True).first().code
        else:
            crncy = 'set a primary <a href="/dsp/crncy">currency</a>'

        instance =company.objects.all().using(db).first()
        company_form = CompanyForm(instance=instance)
        context = {
        "sales": sale,
        "expense": expense,
        "revenue":revenue,
        "invoice_no":invoice_no,
        "emp_no" : len(employee_info.objects.all().using(db)),
        "mod_no" : len(user_info.objects.filter(db=db)),
        "best_client":best_client,
        "best_client_sales":best_client_sales,
        "currency": crncy,
        "year":year,
        "logs":logs,
        "company_form":company_form,
        'company': instance,
        }
        return render(request,"home.html", context)
    else:
        if request.method=='POST':
            username = request.POST["username"]
            password = request.POST["password"]
            from django.contrib.auth import authenticate
            user = auth.authenticate(username = username, password=password)
            if user is not None:
                auth.login(request,user)
                return redirect("/")
            messages.info(request, "Access Denied. Try With Correct Info.")
            return render(request, "log_in.html")
        else:
            return render(request, "log_in.html")

def logout(request):
    auth.logout(request)
    return render(request, "log_in.html")



def view(request, pk):
    if request.user.is_authenticated:
        user_id = request.user.id
        db = db_name(user_id)
        if pk=="emp" and (request.user.user_info.is_admin or request.user.user_info.is_hr):
            dataset1 = employee_info.objects.all().using(db).order_by("-id")
            form = EmployeeForm(auto_id=False)
            dept_list = department.objects.all().using(db)
            dept_form = DeptForm(auto_id=False)
            dataset = []
            regular = 0
            casual = 0
            total = len(dataset1)
            for a in dataset1:
                if a.is_regular:
                    regular += 1
                else:
                    casual += 1
                dept = department.objects.using(db).get(id=a.department)
                data ={
                'instance': a,
                'form': EmployeeForm(instance=a,auto_id=False),
                'dept': dept,
                }
                dataset.append(data)
            return render(request, 'anomyo_employee.html',{"dataset1":dataset,"form":form,'dept_list':dept_list,'dept_form': dept_form, "casual": casual,"regular":regular,"total":total})
        elif pk == "pr_rgl" and (request.user.user_info.is_admin or request.user.user_info.is_hr):
            if request.method=="POST":
                month_year = request.POST["month"]
            else:
                today = datetime.datetime.now(tmz).date()
                first = today.replace(day=1)
                lastMonth = first - datetime.timedelta(days=1)
                month_year = lastMonth.strftime("%Y-%m")

            # checking month exist or not .if not create one
            if month.objects.using(db).filter(month=month_year).exists():
                last_month = month.objects.using(db).get(month=month_year)
            else:
                f = month(month=month_year)
                f.save(using=db)
                last_month = f
            dataset1 = employee_info.objects.using(db).filter(is_regular=True)
            dataset=[]

            for a in dataset1:
                # This will create payroll if not exist
                create_payroll_full(db,a,last_month)
                data = payroll_full.objects.using(db).get(employee = a, month= last_month)
                frm = PrFullForm(instance=data)
                dta = {
                'data': data,
                'form' : frm
                }
                dataset.append(dta)

            sum_total_payable = 0
            sum_net_payable = 0
            for x in payroll_full.objects.using(db).filter(month = last_month):
                sum_total_payable += x.total_payable
                sum_net_payable += x.net_payable
   
            return render(request, 'anomyo_payroll_regular.html',{'dataset':dataset,'month_year':month_year,'sum_total_payable':sum_total_payable,'sum_net_payable':sum_net_payable})
        elif pk == "advance" and (request.user.user_info.is_admin or request.user.user_info.is_accountant):

            today = datetime.datetime.now(tmz).date()
            mnth = today.strftime("%Y-%m")
            day = today.strftime("%d")
            employees = employee_info.objects.all().using(db)
            
            context = {
            'employees':employees,
            "month_now":mnth,
            'page':request.GET["page"],
            "day": day,
            }
            return render(request, 'anomyo_advance_payment.html',context)
        elif (pk == "pr_csl" or pk=="pr_csl_rd") and (request.user.user_info.is_admin or request.user.user_info.is_hr):
            if request.method=="POST":
                month_year = request.POST["month"]
            elif pk == "pr_csl_rd":
                month_year = request.GET["month_year"]
            else:
                today = datetime.datetime.now(tmz).date()
                first = today.replace(day=1)
                lastMonth = first - datetime.timedelta(days=1)
                month_year = lastMonth.strftime("%Y-%m")
            if month.objects.using(db).filter(month=month_year).exists():
                last_month = month.objects.using(db).get(month=month_year)
            else:
                f = month(month=month_year)
                f.save(using=db)
                last_month = f
            dataset1 = employee_info.objects.using(db).filter(is_regular=False)
            dataset=[]
            dataset_new=[]
            for a in dataset1:
                if payroll_part.objects.using(db).filter(employee = a, month= last_month).exists():
                    data = payroll_part.objects.using(db).get(employee = a, month= last_month)
                    frm = PrPartForm(instance=data)
                    dta = {
                    'data': data,
                    'form' : frm
                    }
                    dataset.append(dta)
                else:
                    dta = {
                    'employee' : a,
                    'department': department.objects.using(db).get(id=a.department)
                    }
                    dataset_new.append(dta)
            sum_total_payable = 0
            sum_net_payable = 0
            for x in payroll_part.objects.using(db).filter(month = last_month):
                sum_total_payable += x.total_payable
                sum_net_payable += x.net_payable

            return render(request, 'anomyo_payroll_casual.html', {'month_year':month_year,"dataset":dataset,"dataset_new":dataset_new,'sum_total_payable':sum_total_payable,'sum_net_payable':sum_net_payable})
        elif pk == "client" and (request.user.user_info.is_admin or request.user.user_info.is_marchent):
            dataset1 = client_info.objects.all().using(db).order_by("-id")
            form = ClientForm()
            emp_list = employee_info.objects.all().using(db)
            dataset = []
            for a in dataset1:
                try:
                    emp = employee_info.objects.using(db).get(id=a.lead)
                except:
                    emp=""
                data ={
                'instance': a,
                'form': ClientForm(instance=a),
                'emp': emp,
                }
                dataset.append(data)
            return render(request, 'anomyo_client.html',{"dataset1":dataset,"form":form,'emp_list':emp_list})
        elif pk == "sales" and (request.user.user_info.is_admin or request.user.user_info.is_marchent):
            clients = client_info.objects.all().using(db)
            currencies = currency.objects.all().using(db)
            today = datetime.datetime.now(tmz).date()
            tday = today.strftime("%Y-%m-%d")

            sales_list = [int(s.invoice_no[9:]) for s in sales.objects.using(db).filter(invoice_no__contains = today.year) if s.invoice_no[4:8] == str(today.year)]

            if sales_list:
                s_no = max(sales_list) + 1
                new_invoice_no = "INV/" + str(today.year)+"/" + "{0:05d}".format(s_no)
                report_no = "R/" + str(today.year)+"/" + "{0:05d}".format(s_no)
            else:
                new_invoice_no = "INV/" + str(today.year)+"/" + "00001"
                report_no = "R/" + str(today.year)+"/" + "00001"
            context = {
            'clients' : clients,
            'currencies' : currencies,
            'today' : tday,
            'new_invoice_no': new_invoice_no,
            'report_no' : report_no
            }
            return render(request, 'anomyo_sales_new.html',context)
        elif pk == "invoices" and (request.user.user_info.is_admin or request.user.user_info.is_marchent or request.user.user_info.is_accountant):
            if request.method =="POST":
                year = request.POST["year"]
            else:
                today = datetime.datetime.now(tmz).date()
                year = today.year
            sales_list = sales.objects.using(db).filter(invoice_date__contains = year ).order_by("-id")
            return render(request, "anomyo_all_sales.html",{"sales":sales_list,"year":year})

        elif pk =="crncy":
            year = datetime.datetime.now(tmz).date().year
            currencies = [{"id": a.id,"name": a.name } for a in currency.objects.all().order_by('name') if not currency.objects.using(db).filter(name=a.name).exists()]
            p_currencies = []
            for a in currency.objects.using(db).all():
                for y in range(int(year),2020,-1):
                    if currency_rate.objects.using(db).filter(currency = a, year = str(y)).exists():
                        instance = currency_rate.objects.using(db).get(currency = a, year =str(y))
                        dta = {
                        "data":a,
                        "rate": instance.rate,
                        "year": instance.year
                        }
                        p_currencies.append(dta)
            return render(request, "anomyo_currency.html",{"p_currencies":p_currencies,"currencies":currencies})
        elif pk == "trns" and (request.user.user_info.is_admin or request.user.user_info.is_accountant):
            today = datetime.datetime.now(tmz).date()
            m =today.strftime("%Y-%m")
            if not month.objects.using(db).filter(month=m).exists():
                f = month(month=m)
                f.save(using=db)
            mnth = month.objects.using(db).get(month=m)
            forward_cash(db,mnth)
            forward_bank(db,mnth)
            pr_reg = payroll_full.objects.using(db).filter(editable=True)
            pr_csl = payroll_part.objects.using(db).filter(editable = True)
            return render(request, "anomyo_transaction.html",{"month": mnth,"day":today.strftime("%d"),"today":today.strftime("%Y-%m-%d"),"pr_reg":pr_reg,"pr_csl":pr_csl})

        elif pk == "cash_book" and (request.user.user_info.is_admin or request.user.user_info.is_accountant):
            today = datetime.datetime.now(tmz).date()
            m =today.strftime("%Y-%m")
            if not month.objects.using(db).filter(month=m).exists():
                f = month(month=m)
                f.save(using=db)
            mnth = month.objects.using(db).get(month=m)
            pr_reg = payroll_full.objects.using(db).filter(editable=True)
            pr_csl = payroll_part.objects.using(db).filter(editable = True)
            #this will forward cash if no entry on that month
            forward_cash(db,mnth)
            if request.method =="POST":
                month_year = request.POST["month_year"]
                data = cash_book.objects.using(db).filter(month__month=month_year).order_by("id")
            else:
                month_year = m
                data = mnth.cash_book_set.all().order_by("id")
            balance = 0
            datas =[]
            for i in range(0,len(data)):
                if data[i].method == "C":
                    balance += data[i].amount
                elif data[i].method == "D":
                    balance -= data[i].amount
                dta = {
                "data": data[i],
                "balance" : balance
                }
                datas.append(dta)
            return render(request, "anomyo_cash_book.html",{"month": mnth,"day":today.strftime("%d"),"today":today.strftime("%Y-%m-%d"),"pr_reg":pr_reg,"pr_csl":pr_csl,"dataset":datas,"month_year":month_year})

        elif pk == "bank_book" and (request.user.user_info.is_admin or request.user.user_info.is_accountant):
            today = datetime.datetime.now(tmz).date()
            m =today.strftime("%Y-%m")
            if not month.objects.using(db).filter(month=m).exists():
                f = month(month=m)
                f.save(using=db)
            mnth = month.objects.using(db).get(month=m)
            forward_bank(db,mnth)
            if request.method =="POST":
                month_year = request.POST["month_year"]
                data = bank_book.objects.using(db).filter(month__month=month_year).order_by("id")
            else:
                month_year = m
                data = mnth.bank_book_set.all().order_by("id")
            balance = 0
            datas =[]
            for i in range(0,len(data)):
                if data[i].method == "C":
                    balance += data[i].amount
                elif data[i].method == "D":
                    balance -= data[i].amount
                dta = {
                "data": data[i],
                "balance" : balance
                }
                datas.append(dta)
            pr_reg = payroll_full.objects.using(db).filter(editable=True)
            pr_csl = payroll_part.objects.using(db).filter(editable = True)
            return render(request, "anomyo_bank_book.html",{"month": mnth,"day":today.strftime("%d"),"today":today.strftime("%Y-%m-%d"),"pr_reg":pr_reg,"pr_csl":pr_csl,"dataset":datas,"month_year":month_year})
        
        elif pk == "templates":    
            create_templates(db)
            inv_tmp = tmp.objects.using(db).filter(isfor="I").first()
            pr_reg = tmp.objects.using(db).filter(isfor="PR").first()
            pr_csl = tmp.objects.using(db).filter(isfor="PC").first()
            bank_book = tmp.objects.using(db).filter(isfor="BB").first()
            cash_book = tmp.objects.using(db).filter(isfor="CB").first()
            context = {
            "inv_tmp": inv_tmp,
            "pr_reg" : pr_reg,
            "pr_csl" : pr_csl,
            "bank_book" : bank_book,
            "cash_book" : cash_book,
            }
            return render(request, "anomyo_templates.html",context)
        elif pk == "users":
            try:
                message = request.GET["message"]
            except:
                message =""
            user = request.user
            if request.user.user_info.is_admin:
                dataset = user_info.objects.filter(db=db,is_admin=False)
            else:
                dataset = None
            return render(request,"anomyo_users.html",{"message":message,"user":user,"dataset":dataset})
        elif pk == "summary":
            year = request.GET.__getitem__("year")
            sale,expense,revenue,invoice_no,best_client,best_client_sales = get_summary(db,year)
            return JsonResponse({"sale":sale,"expense":expense,"revenue":revenue,"invoice_no":invoice_no,"best_client":best_client,"best_client_sales":best_client_sales})
        else:
            return HttpResponse("<h1>This is classified</h1>")
    else:
        return redirect("/")
















def view_2(request,pk1,pk2):
    if request.user.is_authenticated:
        user_id = request.user.id
        db = db_name(user_id)
        if pk1 == "crncy":
            year = datetime.datetime.now(tmz).date().year
            currencies = [{"id": a.id,"name": a.name } for a in currency.objects.all() if not currency.objects.using(db).filter(name=a.name).exists()]
            p_currencies = []
            for a in currency.objects.using(db).all():
                for y in range(int(year),2020,-1):
                    if currency_rate.objects.using(db).filter(currency = a, year = str(y)).exists():
                        instance = currency_rate.objects.using(db).get(currency = a, year =str(y))
                        dta = {
                        "data":a,
                        "rate": instance.rate,
                        "year": instance.year
                        }
                        p_currencies.append(dta)

            instance = currency.objects.using(db).get(id=int(pk2))
            # comment_set_all will get all instances related to particular instance
            currency_rates =instance.currency_rate_set.using(db).all()
            year_choices = [y for y in range(int(year),2010,-1) if not currency_rate.objects.using(db).filter(year=y,currency=instance).exists()]
            context ={
            "currency_info":instance,
            "currency_rates":currency_rates,
            "currencies":currencies,
            "p_currencies":p_currencies,
            "year_choices":year_choices
            }
            return render(request, "anomyo_currency.html", context)
        elif pk1 == "advance"  and (request.user.user_info.is_admin or request.user.user_info.is_accountant):
            if request.is_ajax():
                mnth = request.GET.__getitem__("month")
                emp = employee_info.objects.using(db).get(id=pk2)

                # create month if not exist
                if month.objects.using(db).filter(month=mnth).exists():
                    f = month.objects.using(db).get(month=mnth)
                else:
                    f = month(month=mnth)
                    f.save(using=db)

                if emp.is_regular:
                    create_payroll_full(db,emp,f)
                    pr = emp.payroll_full_set.get(month__month=mnth)
                    data = {
                    "pr_id": "full-"+str(pr.id),
                    "emp" : pr.employee.name,
                    "is_regular":pr.employee.is_regular,
                    "month" : mnth,
                    "advance": pr.advance,
                    "is_editable": pr.editable,
                    }
                    
                elif not emp.is_regular:
                    create_payroll_part(db,emp.id,f)
                    pr = emp.payroll_part_set.get(month__month=mnth)
                    data = {
                    "pr_id": "part-"+str(pr.id),
                    "emp" : pr.employee.name,
                    "is_regular":pr.employee.is_regular,
                    "month" : mnth,
                    "advance": pr.advance,
                    "is_editable": pr.editable,
                    }
                return JsonResponse(data)
                        
        elif pk1 == "sales"  and (request.user.user_info.is_admin or request.user.user_info.is_marchent or request.user.user_info.is_accountant):
            f = sales.objects.using(db).get(id=pk2)
            criterias = f.sales_criteria_set.all().using(db)
            clients = client_info.objects.all().using(db)
            currencies = currency.objects.all().using(db)
            today = datetime.datetime.now(tmz).date()
            m =today.strftime("%Y-%m")
            if not month.objects.using(db).filter(month=m).exists():
                y = month(month=m)
                y.save(using=db)
            mnth = month.objects.using(db).get(month=m)
            relative_rate = get_currency_rate(db, today.year, f.currency.id)
            context = {
            'clients' : clients,
            'currencies' : currencies,
            'day' : today.strftime("%d"),
            'month' : mnth.month,
            'month_id': mnth.id,
            'today' : today.strftime("%Y-%m-%d"),
            'invoice_no': f.invoice_no,
            'invoice_date': f.invoice_date.strftime("%Y-%m-%d"),
            'report_no' : f.report_no,
            'report_date' : f.report_date.strftime("%Y-%m-%d"),
            'criterias' : criterias,
            'f' : f,
            'prime_currency' : currency.objects.using(db).get(is_primary=True).code,
            'relative_rate' : "{:.5f}".format(relative_rate)
            }
            return render(request,"anomyo_sales.html",context)
        elif pk1 == "logs" and request.user.user_info.is_admin:
            
            items = activity_log.objects.order_by('-id').using(db)
            p = Paginator(items, 13)
            current_page_num = int(pk2)

            last_page_num = p.num_pages - int(pk2)
            l_page_num = p.num_pages
            if last_page_num > 5:
                last_page_num = 5
            first_page_num = int(pk2) - 1
            if first_page_num >5:
                first_page_num = 5
            try:
                logs = p.page(pk2)
            except EmptyPage:
                logs = p.page(1)
            return render(request, "anomyo_logs.html",{"logs":logs,"current_page_num":current_page_num,"last_page_num":last_page_num,"first_page_num":first_page_num,"l_page_num":l_page_num})
        else:
            return HttpResponse("<h1> This is classified</h1>")
    else:
        return redirect("/")














def save_new(request, pk):
    if request.user.is_authenticated:
        user_id = request.user.id
        db = db_name(user_id)
        if pk=='emp' and (request.user.user_info.is_admin or request.user.user_info.is_hr):
            form = EmployeeForm(request.POST)
            if form.is_valid():
                f = form.save(commit=False)
                f.department = department.objects.using(db).get(id=request.POST["dept_l"]).id
                f.save(using=db)
                log = activity_log(user= user_id, username=User.objects.get(id=user_id).username, description = f'added new employee(Name:{f.name}) information', method='C')
                log.save(using=db)
                return redirect('/dsp/emp')
        elif pk=='client' and (request.user.user_info.is_admin or request.user.user_info.is_marchent):
            form = ClientForm(request.POST)
            if form.is_valid():
                f = form.save(commit=False)
                f.lead = employee_info.objects.using(db).get(id=request.POST["emp_l"]).id
                f.save(using=db)
                log = activity_log(user= user_id, username=User.objects.get(id=user_id).username, description = f'Added new client((Name:{f.name})) information', method='C')
                log.save(using=db)
                return redirect('/dsp/client')

        elif pk=="crncy" and (request.user.user_info.is_admin or request.user.user_info.is_marchent):
            if request.is_ajax():
                id_no = request.GET.__getitem__('id_no')
                # Getting Currency Info from default db
                instance = currency.objects.get(id=int(id_no))
                c_rate = currency_rate.objects.get(currency=instance)
                # Checking If Currency info exist in personal db
                if currency.objects.filter(name= instance.name).using(db).exists():
                    message = f"{instance.name} already added in your Currencies"
                else:
                    # Saving Currency Info to personal db
                    new = currency(name=instance.name, code=instance.code)
                    new.save(using=db)
                    new2 = currency_rate(currency=new, year = c_rate.year, rate = c_rate.rate)
                    new2.save(using=db)
                    if not currency.objects.using(db).filter(is_primary = True).exists():
                        new.is_primary = True
                        new.save()
                    message = f"Success! {instance.name} added in your Currencies"
                    log = activity_log(user= user_id, username=User.objects.get(id=user_id).username, description = f'Added new currency((Code:{new.code}))', method='C')
                    log.save(using=db)
                return JsonResponse({"message":message})
        elif pk =="dept" and (request.user.user_info.is_admin or request.user.user_info.is_hr):
            form = DeptForm(request.POST)
            if form.is_valid():
                f = form.save(commit=False)
                f.save(using=db)
            return redirect("/dsp/emp")
        elif (pk == "advance_cash" or pk == "advance_bank") and (request.user.user_info.is_admin or request.user.user_info.is_accountant):
            ins_list = request.POST.__getitem__("ins_list")
            method = "D"
            today = datetime.datetime.now(tmz).date()
            m =today.strftime("%Y-%m")
            mnth = month.objects.using(db).get(month=m)
            date = m + "-" + "{0:02d}".format(int(request.POST.__getitem__("day")))
            prtc = request.POST.__getitem__("prtc")
            from decimal import Decimal
            amount = Decimal(request.POST.__getitem__("amount"))
            for a in ins_list.split(","):
                if a.split("-")[0] == "full":
                    pr = payroll_full.objects.using(db).get(id=a.split("-")[1])
                elif a.split("-")[0] == "part":
                    pr = payroll_part.objects.using(db).get(id=a.split("-")[1])
                pr.advance = Decimal(a.split("-")[2])
                pr.save()
            if pk == "advance_cash":
                forward_cash(db,mnth)
                f = cash_book(month=mnth, date=date,prtc=prtc,method=method,amount=amount)
                f.save(using=db)
                log = activity_log(user= user_id, username=User.objects.get(id=user_id).username, description = f'advance to employee added in Cash Book (Ref No.:{f.id})', method='C')
                log.save(using=db)
                return JsonResponse({"message":"success","url":"/dsp/cash_book"})
            elif pk =="advance_bank":
                forward_bank(db,mnth)
                bank = request.POST.__getitem__("bank")
                chq_no = request.POST.__getitem__("chq_no")
                chq_date = request.POST.__getitem__("chq_date")
                print(bank,chq_no,chq_date)
                f = bank_book(month=mnth, date=date,prtc=prtc,method=method,bank=bank,chq_no=chq_no,chq_date=chq_date, amount=amount)
                f.save(using=db)
                log = activity_log(user= user_id, username=User.objects.get(id=user_id).username, description = f'advance to employee added in Bank Book (Ref No.:{f.id})', method='C')
                log.save(using=db)
                return JsonResponse({"message":"success","url":"/dsp/bank_book"})

        elif pk =="pr_csl" and (request.user.user_info.is_admin or request.user.user_info.is_hr):
            id_list = request.POST.getlist('id_list[]')
            month_year = request.POST.__getitem__('month_year')
            last_month = month.objects.using(db).get(month=month_year)
            for i in id_list:
                create_payroll_part(db,i,last_month) 
            return JsonResponse({"message":f"/dsp/pr_csl_rd?month_year={month_year}"})
        elif pk =="sales" and (request.user.user_info.is_admin or request.user.user_info.is_marchent):
            if request.is_ajax():
                invoice_date = request.POST.__getitem__("invoice_date")
                report_no = request.POST.__getitem__("report_no")
                report_date = request.POST.__getitem__("report_date")
                client_id = request.POST.__getitem__("client_id")
                client = client_info.objects.using(db).get(id=int(client_id))
                currency_id = request.POST.__getitem__("currency_id")
                crncy = currency.objects.using(db).get(id=int(currency_id))
                discount = request.POST.__getitem__("discount")
                count = int(request.POST.__getitem__('criteria_no'))
                today = datetime.datetime.now(tmz).date()
                sales_list = [int(s.invoice_no[9:]) for s in sales.objects.using(db).filter(invoice_no__contains = today.year) if s.invoice_no[4:8] == str(today.year)]

                if sales_list:
                    s_no = max(sales_list) + 1
                    new_invoice_no = "INV/" + str(today.year)+"/" + "{0:05d}".format(s_no)
                    report_no = "R/" + str(today.year)+"/" + "{0:05d}".format(s_no)
                else:
                    new_invoice_no = "INV/" + str(today.year)+"/" + "00001"
                    report_no = "R/" + str(today.year)+"/" + "00001"
                f = sales(invoice_no = new_invoice_no, invoice_date = invoice_date,report_no=report_no,report_date=report_date,client = client, currency = crncy, discount = discount)
                f.save(using=db)

                for i in range(0,count):
                    desc = request.POST.__getitem__(f"criterias[{i}][desc]")
                    qtn = request.POST.__getitem__(f"criterias[{i}][qtn]")
                    amount = request.POST.__getitem__(f"criterias[{i}][amount]")

                    sc = sales_criteria(sales=f,desc=desc,qtn = qtn,amount=amount)
                    sc.save(using=db)
                log = activity_log(user= user_id, username=User.objects.get(id=user_id).username, description = f'Created an invoice (INVOICE NO:{new_invoice_no})', method='C')
                log.save(using=db)
                
                context = {
                'invoice_no': new_invoice_no,
                "id": f.id,
                'message': f"{f.invoice_no} is Saved and Ready to Print"
                }
                return JsonResponse(context)
        elif (pk == "cash_entry" or pk=="cash_entry_pr_reg" or pk=="cash_entry_pr_csl" or pk=="cash_entry_sales") and (request.user.user_info.is_admin or request.user.user_info.is_accountant):
            
            if pk == "cash_entry_pr_reg":
                id_list = request.POST.getlist("id_list")
                for a in id_list:
                    f = payroll_full.objects.using(db).get(id = a)
                    f.editable = False
                    f.save()

            elif pk == "cash_entry_pr_csl":
                id_list = request.POST.getlist("id_list")
                for a in id_list:
                    f = payroll_part.objects.using(db).get(id = a)
                    f.editable = False
                    f.save()
            elif pk == "cash_entry_sales":
                sales_id = request.POST["sales_id"]
                is_full_paid = request.POST.getlist("full_paid")
                f = sales.objects.using(db).get(id = sales_id)
                from decimal import Decimal
                f.recieved = f.recieved + Decimal(request.POST["used_amount"])
                f.discount = Decimal(request.POST["discount"])
                f.save()
                if is_full_paid or f.due == 0:
                    f.editable = False
                    f.save()
                
            mnth = month.objects.using(db).get(id=request.POST["month_id"])
            forward_cash(db,mnth)
            date = mnth.month + "-" + "{0:02d}".format(int(request.POST["day"]))
            prtc = request.POST["prtc"]
            method = request.POST["method"]
            amount = request.POST["amount"]
            f = cash_book(month=mnth, date=date,prtc=prtc,method=method,amount=amount)
            f.save(using=db)
            log = activity_log(user= user_id, username=User.objects.get(id=user_id).username, description = f'Made a entry in Cash Book (Ref No.:{f.id})', method='C')
            log.save(using=db)
            return redirect("/dsp/cash_book")
        elif (pk == "bank_entry" or pk=="bank_entry_pr_reg" or pk=="bank_entry_pr_csl" or pk=="bank_entry_sales") and (request.user.user_info.is_admin or request.user.user_info.is_accountant):
            if pk == "bank_entry_pr_reg":
                id_list = request.POST.getlist("id_list")
                for a in id_list:
                    f = payroll_full.objects.using(db).get(id = a)
                    f.editable = False
                    f.save()
            elif pk == "bank_entry_pr_csl":
                id_list = request.POST.getlist("id_list")
                for a in id_list:
                    f = payroll_part.objects.using(db).get(id = a)
                    f.editable = False
                    f.save()
            elif pk == "bank_entry_sales":
                sales_id = request.POST["sales_id"]
                is_full_paid = request.POST.getlist("full_paid")
                f = sales.objects.using(db).get(id = sales_id)
                from decimal import Decimal
                f.recieved = f.recieved + Decimal(request.POST["used_amount"])
                f.discount = Decimal(request.POST["discount"])
                f.save()
                if is_full_paid or f.due == 0:
                    f.editable = False
                    f.save()
            mnth = month.objects.using(db).get(id=request.POST["month_id"])
            forward_bank(db,mnth)
            date = mnth.month + "-" + "{0:02d}".format(int(request.POST["day"]))
            prtc = request.POST["prtc"]
            method = request.POST["method"]
            bank = request.POST["bank"]
            chq_no = request.POST["chq_no"]
            chq_date = request.POST["chq_date"]
            amount = request.POST["amount"]
            f = bank_book(month=mnth, date=date,prtc=prtc,method=method,bank=bank,chq_no=chq_no,chq_date=chq_date, amount=amount)
            f.save(using=db)
            log = activity_log(user= user_id, username=User.objects.get(id=user_id).username, description = f'Made a entry in Bank Book (Ref No.:{f.id})', method='C')
            log.save(using=db)
            return redirect("/dsp/bank_book")
        elif pk=="user" and request.user.user_info.is_admin:
            username = request.user.username + "_" + request.POST["username"]
            new_password = request.POST["new_password"]
            admin_password = request.POST["admin_password"]
            try:
                face = request.FILES["face"]
            except:
                face = ""
            
            is_hr = False
            is_accountant = False
            is_marchent = False
            try:
                role = request.POST.getlist("role")
                if "hr" in role:
                    is_hr = True
                if "accountant" in role:
                    is_accountant = True
                if "marchent" in role:
                    is_marchent = True
            except:
                pass
            
            permission = request.user.check_password(admin_password) and request.user.user_info.is_admin
            total_user = user_info.objects.filter(db=db)
            if permission and len(total_user) < 10:
                if User.objects.filter(username=username).exists():
                    message ="Username is too Common" 
                else:
                    U = User.objects.create_user(username=username,password=new_password)
                    if face == "":
                        UI = user_info(user=U,db=db,is_accountant=is_accountant,is_hr=is_hr,is_marchent=is_marchent)
                    else:
                        UI = user_info(user=U,face=face,db=db,is_accountant=is_accountant,is_hr=is_hr,is_marchent=is_marchent)
                    UI.save()
                    message ="Moderator created successfully"
                return redirect(f"/dsp/users?message={message}")
            elif permission:
                message = "You reached highest number of user"
            else:
                message = "admin passsowrd didn't match"
            return redirect(f"/dsp/users?message={message}")
        else:
            return HttpResponse("<h1> This is classified</h1>")
    else:
        return redirect("/")












def add_new(request, pk1, pk2):
    if request.user.is_authenticated:
        user_id = request.user.id
        db = db_name(user_id)
        if pk1=="crncy" and (request.user.user_info.is_admin or request.user.user_info.is_marchent):
            # Getting Currency Info from default db
            instance = currency.objects.get(id=int(pk2))
            c_rate = currency_rate.objects.get(currency=instance)
            # Checking If Currency info exist in personal db
            if currency.objects.filter(name= instance.name).using(db).exists():
                message = f"{instance.name} already added in your Currencies"
            else:
                # Saving Currency Info to personal db
                new = currency(name=instance.name, code=instance.code)
                new.save(using=db)
                # if len(currency.objects.all().using(db)) == 1:
                #     new.is_primary = True
                #     new.save()
                new2 = currency_rate(currency=new, year = c_rate.year, rate = c_rate.rate)
                new2.save(using=db)
                log = activity_log(user= user_id, username=User.objects.get(id=user_id).username, description = f'Added currency (Currency:{new.code})', method='C')
                log.save(using=db)
                message = f"Success! {instance.name} added in your Currencies"
            return redirect('/dsp/crncy')
        elif pk1=="crncy_rate" and (request.user.user_info.is_admin or request.user.user_info.is_marchent):
            get_year = request.GET["year"]
            get_rate = request.GET["rate"]
            instance = currency.objects.using(db).get(id=int(pk2))
            c_rate = currency_rate(currency=instance,year=get_year,rate=get_rate)
            c_rate.save(using=db)
            log = activity_log(user= user_id, username=User.objects.get(id=user_id).username, description = f'Added currency rate for currency:-{instance.code} in year-{c_rate.year} ', method='C')
            log.save(using=db)
            return redirect(f'/view/crncy/{pk2}')
        else:
            return HttpResponse("<h1>This is classified</h1>")
    else:
        return redirect("/")













def update(request,pk1,pk2):
    if request.user.is_authenticated:
        user_id = request.user.id
        db = db_name(user_id)
        if pk1=='emp' and (request.user.user_info.is_admin or request.user.user_info.is_hr):
            instance = employee_info.objects.using(db).get(id=pk2)
            form = EmployeeForm(request.POST, instance=instance)
            f = form.save(commit=False)
            f.department = department.objects.using(db).get(id=request.POST["dept_l"]).id
            f.save(using=db)
            log = activity_log(user= user_id, username=User.objects.get(id=user_id).username, description = f'Updated an employee(ID:{f.id},Name:{f.name}) information', method='U')
            log.save(using=db)
            return redirect('/dsp/emp')
        elif pk1=='client' and (request.user.user_info.is_admin or request.user.user_info.is_marchent):
            instance = client_info.objects.using(db).get(id=pk2)
            form = ClientForm(request.POST, instance=instance)
            f = form.save(commit=False)
            f.lead = employee_info.objects.using(db).get(id=request.POST["emp_l"]).id
            f.save(using=db)
            log = activity_log(user= user_id, username=User.objects.get(id=user_id).username, description = f'Updated a Client(ID:{f.id},Name:{f.name}) information', method='U')
            log.save(using=db)
            return redirect('/dsp/client')
        elif pk1 == "pr_rgl" and (request.user.user_info.is_admin or request.user.user_info.is_hr):
            instance = payroll_full.objects.using(db).get(id=pk2)
            form = PrFullForm(request.POST, instance = instance)
            if form.is_valid() and instance.editable==True:
                f = form.save(commit=False)
                f.save(using=db)
                sum_total_payable = 0
                sum_net_payable = 0
                for x in payroll_full.objects.using(db).filter(month = f.month):
                    sum_total_payable += x.total_payable
                    sum_net_payable += x.net_payable
                message = {
                'id' : f.id,
                'total_payable' : f.total_payable,
                'net_payable' : f.net_payable,
                'sum_total_payable' : sum_total_payable,
                'sum_net_payable': sum_net_payable
                }
                log = activity_log(user= user_id, username=User.objects.get(id=user_id).username, description = f'Updated Payroll of a full-time Employee (Name:{instance.employee.name}) of Month-{f.month.month}', method='U')
                log.save(using=db)
            else:
                message = "false"
            return JsonResponse({"message":message})
        elif pk1 == "pr_csl" and (request.user.user_info.is_admin or request.user.user_info.is_hr):
            instance = payroll_part.objects.using(db).get(id=pk2)
            form = PrPartForm(request.POST, instance = instance)
            if form.is_valid() and instance.editable==True:
                f = form.save(commit=False)
                f.save(using=db)
                sum_total_payable = 0
                sum_net_payable = 0
                for x in payroll_part.objects.using(db).filter(month = f.month):
                    sum_total_payable += x.total_payable
                    sum_net_payable += x.net_payable
                message = {
                'id' : f.id,
                'overtime' : f.overtime,
                'total_payable' : f.total_payable,
                'net_payable' : f.net_payable,
                'sum_total_payable' : sum_total_payable,
                'sum_net_payable': sum_net_payable
                }
                log = activity_log(user= user_id, username=User.objects.get(id=user_id).username, description = f'Updated Payroll of a part-time Employee(Name:{instance.employee.name}) of Month-{f.month.month}', method='U')
                log.save(using=db)
            else:
                message = "false"
            return JsonResponse({"message":message})
        elif pk1 == "crncy" and (request.user.user_info.is_admin or request.user.user_info.is_accountant):
            instance = currency.objects.using(db).get(id=pk2)
            if not instance.is_primary:
                for a in currency.objects.using(db).all():
                    a.is_primary = False
                    a.save()
                instance.is_primary =True
                instance.save()
                log = activity_log(user= user_id, username=User.objects.get(id=user_id).username, description = f'Made a Currency as Primary(currency:{instance.code})', method='U')
                log.save(using=db)
            return redirect(f"/view/crncy/{pk2}")
        elif pk1 == "crncy_rate" and (request.user.user_info.is_admin or request.user.user_info.is_marchent):
            instance = currency_rate.objects.using(db).get(id=int(pk2))
            instance.rate = request.GET["rate"]
            instance.save()
            log = activity_log(user= user_id, username=User.objects.get(id=user_id).username, description = f'Updated currency rate of {instance.currency.code} of year-{instance.year}', method='U')
            log.save(using=db)
            return redirect(f"/view/crncy/{instance.currency.id}")
        elif pk1 == "cmpny":
            instance = company.objects.all().using(db).first()
            form = CompanyForm( request.POST,request.FILES, instance=instance)
            if form.is_valid():
                f = form.save(commit=False)
                f.save(using=db)
                log = activity_log(user= user_id, username=User.objects.get(id=user_id).username, description = f'Updated your company info', method='U')
                log.save(using=db)
            return redirect("/")
        elif pk1 == "sales" and (request.user.user_info.is_admin or request.user.user_info.is_marchent):  
            f = sales.objects.using(db).get(id=pk2)
            f.invoice_date = request.POST.__getitem__("invoice_date")
            f.report_no = request.POST.__getitem__("report_no")
            f.report_date = request.POST.__getitem__("report_date")
            client_id = request.POST.__getitem__("client_id")
            f.client = client_info.objects.using(db).get(id=int(client_id))
            currency_id = request.POST.__getitem__("currency_id")
            f.currency = currency.objects.using(db).get(id=int(currency_id))
            f.discount = request.POST.__getitem__("discount")
            f.save()
            count = int(request.POST.__getitem__('criteria_no'))

            criterias = f.sales_criteria_set.all().using(db)

            if count == len(criterias):
                for i in range(0,count):
                    sc = criterias[i]
                    sc.desc = request.POST.__getitem__(f"criterias[{i}][desc]")
                    sc.qtn = request.POST.__getitem__(f"criterias[{i}][qtn]")
                    sc.amount = request.POST.__getitem__(f"criterias[{i}][amount]")
                    sc.save()
            elif count < len(criterias):
                for i in range(0,len(criterias)):
                    sc = criterias[i]
                    if i < count:
                        sc.desc = request.POST.__getitem__(f"criterias[{i}][desc]")
                        sc.qtn = request.POST.__getitem__(f"criterias[{i}][qtn]")
                        sc.amount = request.POST.__getitem__(f"criterias[{i}][amount]")
                        sc.save()
                    else:
                        sc.delete()
            elif count > len(criterias):
                for i in range(0,count):
                    if i < len(criterias):
                        sc = criterias[i]
                        sc.desc = request.POST.__getitem__(f"criterias[{i}][desc]")
                        sc.qtn = request.POST.__getitem__(f"criterias[{i}][qtn]")
                        sc.amount = request.POST.__getitem__(f"criterias[{i}][amount]")
                        sc.save()
                    else:
                        desc = request.POST.__getitem__(f"criterias[{i}][desc]")
                        qtn = request.POST.__getitem__(f"criterias[{i}][qtn]")
                        amount = request.POST.__getitem__(f"criterias[{i}][amount]")

                        sc = sales_criteria(sales=f,desc=desc,qtn = qtn,amount=amount)
                        sc.save(using=db)

            log = activity_log(user= user_id, username=User.objects.get(id=user_id).username, description = f'Updated an Invoice(Invoice No.:{f.invoice_no})', method='U')
            log.save(using=db)
            message = f"{f.invoice_no} is Updated and Ready to Print"
            return JsonResponse({'message':message})
        elif pk1 == "templates":
            f = tmp.objects.filter(isfor=pk2).using(db).first()
            f.src_code = request.POST["src_code"]
            f.save()
            return redirect("/dsp/templates")
        elif pk1 == "user_password" or pk1=="moderator" or pk1=="moderator_password":
            if pk1 == "user_password":
                new_password = request.POST["new_password"]
                retype_password = request.POST["retype_password"]
                old_password = request.POST["old_password"]
                if new_password != retype_password:
                    message = "New password and Retype password didn't match. Type carefully"
                elif request.user.check_password(old_password) and len(new_password)>=6:
                    U = request.user
                    U.set_password(new_password)
                    U.save()
                    message ="Password changed successfully"
                else:
                    message = "Old Password didn't match."
            elif pk1 == "moderator":
                admin_password = request.POST["admin_password"]
                try:
                    face = request.FILES["face"]
                except:
                    face = ""
                is_hr = False
                is_accountant = False
                is_marchent = False
                try:
                    role = request.POST.getlist("role")
                    if "hr" in role:
                        is_hr = True
                    if "accountant" in role:
                        is_accountant = True
                    if "marchent" in role:
                        is_marchent = True
                except:
                    pass
                U = user_info.objects.get(user=pk2)
                permission = request.user.check_password(admin_password) and request.user.user_info.is_admin and U.db == request.user.user_info.db
                
                if permission:
                    if face == "":
                        U.is_marchent = is_marchent
                        U.is_hr = is_hr
                        U.is_accountant = is_accountant
                    else:
                        U.face = face
                        U.is_marchent = is_marchent
                        U.is_hr = is_hr
                        U.is_accountant = is_accountant
                    U.save()
                    message ="Moderator successfully updated"
                else:
                    message = "Admin passsowrd didn't match"
            elif pk1 == "moderator_password":
                admin_password = request.POST["admin_password"]
                new_password = request.POST["new_password"]
                U = User.objects.get(id=pk2)
                permission = request.user.check_password(admin_password) and request.user.user_info.is_admin and U.user_info.db == request.user.user_info.db

                if permission and len(new_password)>=6:
                    
                    U.set_password(new_password)
                    U.save()
                    message ="Moderator password successfully changed"
                else:
                    message = "Admin passsowrd didn't match"
            return redirect(f"/dsp/users?message={message}")
        else:
            return HttpResponse("<h1> This is classified</h1>")
    else:
        return redirect("/")
















def delete(request,pk1,pk2):
    if request.user.is_authenticated:
        user_id = request.user.id
        db = db_name(user_id)
        if pk1=='emp' and (request.user.user_info.is_admin or request.user.user_info.is_hr):
            instance = employee_info.objects.using(db).get(id=pk2)
            name = instance.name
            instance.delete()
            log = activity_log(user= user_id, username=User.objects.get(id=user_id).username, description = f'Deleted an employee(Name:{name}) information', method='D')
            log.save(using=db)
            return redirect('/dsp/emp')
        elif pk1=='client' and (request.user.user_info.is_admin or request.user.user_info.is_marchent):
            instance = client_info.objects.using(db).get(id=pk2)
            name = instance.name
            instance.delete()
            log = activity_log(user= user_id, username=User.objects.get(id=user_id).username, description = f'Deleted a Client(Name:{name}) information', method='D')
            log.save(using=db)
            return redirect('/dsp/client')
        return HttpResponse('Wrong Way')
    else:
        return redirect("/")












def gen_pdf(request,pk1,pk2):
    if request.user.is_authenticated:
        user_id = request.user.id
        db = db_name(user_id)
        try:
            primary_currency = currency.objects.using(db).get(is_primary=True).code
        except:
            return HttpResponse("<h4>Set A Primary <a href='/dsp/crncy'>Currency</a> First</h4>")
        create_templates(db)
        cmpny = company.objects.all().using(db).first()
        if pk1 == "invoice" and (request.user.user_info.is_admin or request.user.user_info.is_marchent):
            
            data = sales.objects.using(db).get(id=pk2)
            sales_c = data.sales_criteria_set.all() 
            inv_tmp = tmp.objects.using(db).filter(isfor="I").first()
            context = {"info":data,"company":cmpny,"sales_criteria":sales_c,"inv_tmp":inv_tmp}
            pdf = render_to_pdf(inv_tmp.src_code, context)
            pdf['Content-Disposition'] = f'filename="{data.invoice_no}.pdf"'
            return pdf
        elif pk1 == "pr_rgl" and (request.user.user_info.is_admin or request.user.user_info.is_hr):
            
            d = month.objects.using(db).get(month=pk2)
            data = d.payroll_full_set.all()
            pr_rgl = tmp.objects.using(db).filter(isfor="PR").first()
            sum_total_payable = 0
            sum_net_payable = 0
            for x in data:
                sum_total_payable += x.total_payable
                sum_net_payable += x.net_payable
            context = {"company":cmpny,"inv_tmp":pr_rgl,"pr_rgl_list":data,"month_year":datetime.datetime.strptime(pk2,"%Y-%m").strftime("%b-%Y"),"sum_total_payable":sum_total_payable,"sum_net_payable":sum_net_payable,"primary_currency":primary_currency}
            pdf = render_to_pdf(pr_rgl.src_code, context)
            pdf['Content-Disposition'] = f'filename="Payroll Regular {pk2}.pdf"'
            return pdf
        elif pk1 == "pr_csl" and (request.user.user_info.is_admin or request.user.user_info.is_hr):
            
            d = month.objects.using(db).get(month=pk2)
            data = d.payroll_part_set.all()
            pr_csl = tmp.objects.using(db).filter(isfor="PC").first()
            sum_total_payable = 0
            sum_net_payable = 0
            for x in data:
                sum_total_payable += x.total_payable
                sum_net_payable += x.net_payable
            context = {"company":cmpny,"inv_tmp":pr_csl,"pr_csl_list":data,"month_year":datetime.datetime.strptime(pk2,"%Y-%m").strftime("%b-%Y"),"sum_total_payable":sum_total_payable,"sum_net_payable":sum_net_payable,"primary_currency":primary_currency}
            pdf = render_to_pdf(pr_csl.src_code, context)
            pdf['Content-Disposition'] = f'filename="Payroll Casual {pk2}.pdf"'
            return pdf
        elif pk1 == "cash_book" and (request.user.user_info.is_admin or request.user.user_info.is_accountant):
            d = month.objects.using(db).get(month=pk2)
            data = d.cash_book_set.all().order_by("id")
            balance = 0
            datas =[]
            for i in range(0,len(data)):
                if data[i].method == "C":
                    balance += data[i].amount
                elif data[i].method == "D":
                    balance -= data[i].amount
                dta = {
                "data": data[i],
                "balance" : balance
                }
                datas.append(dta)
            cash_book_tmp = tmp.objects.using(db).filter(isfor="CB").first()
            context = {"company":cmpny,"inv_tmp":cash_book_tmp,"page":"cash","book_list":datas,"month_year":datetime.datetime.strptime(pk2,"%Y-%m").strftime("%b-%Y"),"primary_currency":primary_currency}
            pdf = render_to_pdf(cash_book_tmp.src_code, context)
            pdf['Content-Disposition'] = f'filename="Cash Book {pk2}.pdf"'
            return pdf
        elif pk1 == "bank_book" and (request.user.user_info.is_admin or request.user.user_info.is_accountant):
            d = month.objects.using(db).get(month=pk2)
            data = d.bank_book_set.all().order_by("id")
            balance = 0
            datas =[]
            for i in range(0,len(data)):
                if data[i].method == "C":
                    balance += data[i].amount
                elif data[i].method == "D":
                    balance -= data[i].amount
                dta = {
                "data": data[i],
                "balance" : balance
                }
                datas.append(dta)
            bank_book_tmp = tmp.objects.using(db).filter(isfor="BB").first()
            context = {"company":cmpny,"inv_tmp":bank_book_tmp,"page":"bank","book_list":datas,"month_year":datetime.datetime.strptime(pk2,"%Y-%m").strftime("%b-%Y"),"primary_currency":primary_currency}
            pdf = render_to_pdf(bank_book_tmp.src_code, context)
            pdf['Content-Disposition'] = f'filename="Bank Book {pk2}.pdf"'
            return pdf
        else:
            return HttpResponse("<h1>This is classified</h1>")
    else:
        return redirect("/")





def gen_csv(request,pk1,pk2):
    if request.user.is_authenticated:
        user_id = request.user.id
        db = db_name(user_id)
        try:
            primary_currency = currency.objects.using(db).get(is_primary=True).code
        except:
            return HttpResponse("<h4>Set A Primary <a href='/dsp/crncy'>Currency</a> First</h4>")
        create_templates(db)
        cmpny = company.objects.all().using(db).first()
        import csv
        if pk1 == "pr_rgl" and (request.user.user_info.is_admin or request.user.user_info.is_hr):     
            d = month.objects.using(db).get(month=pk2)
            data = d.payroll_full_set.all()
            # Create the HttpResponse object with the appropriate CSV header.
            response = HttpResponse(
                content_type='text/csv'
            )

            response['Content-Disposition'] = f'filename="payroll of full time employee - {pk2}.csv"'

            writer = csv.writer(response)
            writer.writerow(['Name', 'Desig.', 'att.', 'Basic','Medical A.','Home A.','Conveyance A.','Transport A.','Others','Deduction','Total Payable','Advance','Net Payable'])
            
            for x in data:
                writer.writerow([x.employee.name, x.employee.designation, x.attendance, x.basic, x.medical,x.home,x.conveyance,x.transport,x.others, x.deduction, x.total_payable, x.advance, x.net_payable])
            return response
        elif pk1 == "pr_csl" and (request.user.user_info.is_admin or request.user.user_info.is_hr):
            d = month.objects.using(db).get(month=pk2)
            data = d.payroll_part_set.all()
            # Create the HttpResponse object with the appropriate CSV header.
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = f'filename="payroll of part time employee - {pk2}.csv"'
            writer = csv.writer(response)
            writer.writerow(['Name', 'Desig.', 'work_hours', 'hours_rate',f'Overtime({primary_currency})',f'Allownce({primary_currency})',f'Total Payable({primary_currency})',f'Advance({primary_currency})',f'Net Payable({primary_currency})'])
            
            for x in data:
                writer.writerow([x.employee.name, x.employee.designation, x.work_hours, x.hours_rate, x.overtime, x.others, x.total_payable, x.advance, x.net_payable])
            return response
        elif pk1 == "cash_book" and (request.user.user_info.is_admin or request.user.user_info.is_accountant):
            d = month.objects.using(db).get(month=pk2)
            data = d.cash_book_set.all().order_by("id")
            # Create the HttpResponse object with the appropriate CSV header.
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = f'filename="cash book - {pk2}.csv"'
            writer = csv.writer(response)
            writer.writerow(['Ref. No.', 'Date', 'Particulars', 'Credit','Debit','Balance'])
            balance = 0
            for i in data:
                if i.method == "C":
                    balance += i.amount
                    writer.writerow([i.id, i.date, i.prtc, i.amount, '',balance])
                elif i.method == "D":
                    balance -= i.amount
                    writer.writerow([i.id, i.date, i.prtc, '', i.amount, balance])
            return response
        elif pk1 == "bank_book" and (request.user.user_info.is_admin or request.user.user_info.is_accountant):
            d = month.objects.using(db).get(month=pk2)
            data = d.bank_book_set.all().order_by("id")
            # Create the HttpResponse object with the appropriate CSV header.
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = f'filename="bank book - {pk2}.csv'
            writer = csv.writer(response)
            writer.writerow(['Ref. No.', 'Date', 'Particulars','Bank Name','Chq. No.', 'Chq. Date', 'Credit','Debit','Balance'])
            balance = 0
            for i in data:
                if i.method == "C":
                    balance += i.amount
                    writer.writerow([i.id, i.date, i.prtc, i.bank, i.chq_no, i.chq_date, i.amount, '',balance])
                elif i.method == "D":
                    balance -= i.amount
                    writer.writerow([i.id, i.date, i.prtc, i.bank, i.chq_no, i.chq_date, '', i.amount, balance])
            return response