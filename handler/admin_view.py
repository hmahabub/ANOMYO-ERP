from django.shortcuts import render, redirect
from .models import messageforus
import datetime
from django.http import HttpResponse
def save_in_admin(request,pk):
    if pk=="message":
        name = request.POST["name"]
        email = request.POST["email"]
        message = request.POST["message"]

        f = messageforus(name=name,email=email,message=message)
        f.save(using="default")
        return redirect("/")

def show_message(request):
    if request.user.is_superuser:
        try:
            action = request.GET["action"]
            if action =="markasread":
                for a in messageforus.objects.filter(is_seen=False):
                    a.is_seen = True
                    a.save()
        except:
            pass

        html = "<a href='/show_message?action=markasread'>Mark all as Read</a><table style='width:60%;margin:auto;text-align:center'><tr><th>Name</th><th>Email</th><th>Message</th><th>recieved_at</th></tr>"
        for a in messageforus.objects.all().order_by("-recieved_at"):
            if a.is_seen:
                html += f"<tr style='border:2px solid black'><td>{a.name}</td><td>{a.email}</td><td>{a.message}</td><td>{a.recieved_at}</td></tr>"
            else:
                html += f"<tr style='border:2px solid black;background:mediumseagreen;color:white'><td>{a.name}</td><td>{a.email}</td><td>{a.message}</td><td>{a.recieved_at}</td></tr>"
            
        html += "</table>"

        return HttpResponse(html)
    return redirect("/")


