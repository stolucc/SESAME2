# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.views.generic import TemplateView
from django.shortcuts import render, HttpResponse, redirect
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from django.urls import reverse
from django.views.static import serve
from django.http import JsonResponse
from django.db.models import Q
from .forms import PublishForm
from accounts.models import Call, Center, Proposal, Reviewer ,Funder, Researcher
from accounts.forms import CenterForm, ProposalForm
import MySQLdb as _db
import os
import datetime


host_name = "mysql.netsoc.co"
user_name = "nadehh"
password = "HjOEsz2C483h"
db_name = "nadehh_db_final"
db_info_string="< %s > @ < %s >"%(db_name,host_name)
result = "fail"

class HomeView(TemplateView):
    template_name = 'home/home.html'

    def get(self, request):
        tableData = Call.objects.all()
        context = {'tableData':tableData}
        return render(request, self.template_name, context)

def view_center(request):
    center_obj = Center.objects.filter(members=request.user.id)
    context = {'center_obj':center_obj}
    return render(request, 'home/view_center.html', context)

def create_center(request):
    if request.method == 'POST':
        form = CenterForm(request.POST)
        if form.is_valid():
            form.save(admin=request.user)
            return redirect(reverse('home:view_center'))
    else:
        form = CenterForm()
    return render(request, 'home/create_center.html', {'form': form})

def download_file(request):
    if request.method == "GET":
        filepath = request.GET.get("filename")
        return serve(request, os.path.basename(filepath), os.path.dirname(filepath))

def get_call_view(request):
    files = []
    call_obj = None
    call_id = None
    print("OK RECEIVING SOMETHING")
    if request.method == 'GET':
        call_id = request.GET.get('call_id', '')
        call_obj = Call.objects.get(pk=call_id)
        print("was a get request lol")
        call_id = request.GET.get('call_id', '')
        call_obj = Call.objects.filter(pk=call_id).values()
        context = {'call_obj':call_obj}

        userFileDir = "calls/%s-%s/calls"%(str(request.user).split("@")[0],call_id)


        for file in os.listdir(userFileDir):
            files.append(file)


    else:
        filenames = []

        call_id = request.POST.get('call_id', '').decode('utf-8')

        userFileDir = "calls/%s-%s/calls"%(str(request.user).split("@")[0],call_id)
        if not os.path.isdir(userFileDir):
            os.makedirs(userFileDir)

        for key in request.FILES:
            file = request.FILES[key]
            filenames.append(str(file))
            with open("%s/%s"%(userFileDir,file.name),"wb+") as saveFile:
                for line in file:
                    saveFile.write(line)

        print(filenames)
        filename = ','.join(filenames)

        id = request.user.id
        call_id = int(call_id)

        print(id,call_id,filename)

        db = Proposal(proposal_document=filename,call_id=call_id,user_id=id)
        db.save()

    return render(request, 'home/call_view.html', {'call_obj':call_obj,"link_obj":files,"call_id":call_id})

def delete_proposal(request, proposal_id):
    Proposal.objects.get(pk=int(proposal_id)).delete()
    return redirect(reverse("home:my_calls"))

def delete_call(request, call_id):
    Call.objects.get(pk=int(call_id)).delete()
    return redirect(reverse("home:my_calls"))

def get_my_calls(request):
    user = request.user

    try:
        funder = user.funder
        my_call_table_data = Call.objects.filter(funder_id=user.id).values()
        context = {'my_call_table_data':my_call_table_data}
        return render(request, 'home/my_calls.html', context)
    except Funder.DoesNotExist:
        print("Not funder")

    try:
        researcher = user.researcher
        my_call_table_data = [prop.call for prop in Proposal.objects.select_related('call').filter(user=user)]
        context = {'my_call_table_data':my_call_table_data}
        return render(request, 'home/my_calls.html', context)
    except Researcher.DoesNotExist:
        print("Not researcher")

    try:
        reviewer = user.reviewer
        proposals = Proposal.objects.select_related('call').filter(reviewer_id=user.id)
        my_call_table_data = [prop.call for prop in proposals]
        context = {'my_call_table_data':my_call_table_data, 'proposals':proposals}
        return render(request, 'home/my_calls.html', context)
    except Reviewer.DoesNotExist:
        print("Not reviewer")


def pub (request):
    categories = []
    edit_info = []
    connection = None
    edit_toggle = False
    funds = ["€10,000 - €25,000","€25,000 - €50,000","€50,000 - €100,000","€100,000 - €250,000","€250,000 - €500,000","€500,000 - €1,000,000","€1,000,000 - €2,000,000"]
    editing_mode = False
    now = datetime.datetime.now()
    date_string = "%s-%s-%s"%(now.year,now.month,now.day)

    if request.method == "POST":
       now = datetime.datetime.now()
       date_string = "%s-%s-%s"%(now.year,now.month,now.day)

       print(request.user)
       fname = request.POST.get("fname")
       sname = request.POST.get("sname")
       eligibility = request.POST.get("tag")
       title = request.POST.get("title")
       description = request.POST.get("description")
       deadline = request.POST.get("date")
       grant = request.POST.get("grant")
       funder_id = request.user.id

       value = request.POST.get("editing_mode")

       if value == "True":
           editing_mode = True

       _call_id = request.POST.get("_call_id")


       #print(request.POST.items())
       # for key in request.FILES:
       #     file = request.FILES[key]
       #     with open("/home/users/nadehh/django-uploads/%s"%(file.name),"wb+") as saveFile:
       #         for line in file:
       #             saveFile.write(line)
       #         print("File has been saved")


       filenames = []


       for key in request.FILES:
           file = str(request.FILES[key])
           print(file)
           filenames.append(file)

       print(filenames)

       filename = ', '.join(filenames)

       print("FILE NAMES SENT FROM CONCATENATION --- > ",filename)

       print(request.FILES.values())




       db_query = """

           INSERT INTO calls (target, created, funder_id, title, description, deadline,funds, file_location)
           VALUES ("%s","%s","%s","%s","%s","%s","%s","%s");

       """ %(eligibility,date_string,funder_id,title,description,deadline,grant,filename)

       print("$"*50)

       if editing_mode:
          db_query = """

              UPDATE calls
              SET target="%s",
                  created="%s",
                  funder_id=%d,
                  title="%s",
                  description="%s",
                  deadline="%s",
                  funds="%s"
              WHERE id = %d;

          """ %(eligibility,date_string,int(funder_id),title,description,deadline,grant,int(_call_id))

       try:                        #success page if given to db
           connection = _db.connect(host=host_name,
                            user=user_name,
                            passwd=password,
                            db=db_name)

           result = "success"
           cursor = connection.cursor()

           cursor.execute(db_query)

           #Calling this fucntion below which I set up as the email fucntion
           email_users(request)

           if not editing_mode:
               id = cursor.lastrowid

               user = str(request.user)
               userFileDir = "calls/%s-%s/calls"%(user.split("@")[0],id)

               if not os.path.isdir(userFileDir):
                   os.makedirs(userFileDir)

               for key in request.FILES:
                   file = request.FILES[key]
                   with open("%s/%s"%(userFileDir,file.name),"wb+") as saveFile:
                       for line in file:
                           saveFile.write(line)

           connection.commit()

       except _db.Error as e:
           print("Error connecting to the database.. check credentials!")
           print(e)

       finally:
           connection.close()

    if request.method == 'GET':
        try:
            connection = _db.connect(host=host_name,
                             user=user_name,
                             passwd=password,
                             db=db_name)

            print("#"*64 + "\n")
            print("%-25s %32s" % ("Connected to database:",db_info_string))
            print("%-25s %32s\n" % ("Established cursor:",db_info_string))
            print("#"*64)
            result = "success"
            cursor = connection.cursor()
            cursor.execute("""

                SELECT category FROM categories;

            """)

            for row in cursor.fetchall():
                categories.append(row[0])

            call_id = request.GET.get("call_id")

            if call_id is not None:
                edit_toggle = True

                cursor.execute("""

                    SELECT target,title, description, deadline, funds, file_location From calls WHERE id = %s;

                """%(call_id))

                row = cursor.fetchall()
                if len(row)!=0:
                    for data in row[0]:
                        edit_info.append(data)
                    edit_info[3] = str(edit_info[3])

                fund = edit_info[4].decode('utf-8')

                print("FUNDS -- > ", fund)

                funds.remove(fund)

                categories.remove(str(edit_info[0]))
                edit_info.append(call_id)

        except _db.Error as e:
            print("Error connecting to the database.. check credentials!")
            print(e)

        finally:
            connection.close()

    form = PublishForm()
    return render(request, 'home/publish_call.html',{'form':form,'db':categories, 'edit_info':edit_info, 'edit':edit_toggle, 'funds':funds})

def email_users(request):
    print("Here Ben!")


def autocomplete(request):
    if request.is_ajax():
        search_query = request.GET.get('?search', '')
        centerQuerySet = Center.objects.filter(name__icontains=search_query)[:3]
        researcherQuerySet = Researcher.objects.filter(user__first_name__icontains=search_query) | Researcher.objects.filter(user__last_name__icontains=search_query)[:3]
        queryset = Center.objects.filter(name__contains=request.GET.get('?search', ''))
        list = []
        for i in centerQuerySet:
            list.append(i.name)
            #print(i)
        for i in researcherQuerySet:
            name = ''
            name += i.user.first_name
            name += ' '
            name += i.user.last_name
            list.append(name)
        data = {
            'list': list,
        }
        return JsonResponse(data)

def nav_search(request):
    if request.method == 'GET':
        search_query = request.GET.get('search', '')
        search_query = search_query.split()
        centerQuerySet = Center.objects.all()
        researcherQuerySet = Researcher.objects.all()
        for word in search_query:
            centerQuerySet= centerQuerySet.filter(name__icontains=word)
            researcherQuerySet= researcherQuerySet.filter(Q(user__first_name__icontains=word) | Q(user__last_name__icontains=word))
        context={'centerQuerySet':centerQuerySet, 'researcherQuerySet':researcherQuerySet}
        return render(request, 'home/nav_search.html', context)

def add_to_center(request):
    if request.method == 'GET':
        user_email = request.GET.get('user_email', '')
        center_name = request.GET.get('center', '')
        centerObj = Center.objects.get(name=center_name)
        center_obj = Center.objects.filter(admin_id=request.user.id).values() #for reloading page
        context = {'center_obj':center_obj} #for reloading page
        try:
            userObj = User.objects.get(email=user_email)
            centerObj.members.add(userObj.id)
            centerObj.save()
            context['result'] = 'success'
            return render(request, 'home/view_center.html', context)
        except ObjectDoesNotExist:
            context['result']= 'failure'
            return render(request, 'home/view_center.html', context)

def update_proposal(request):
    if request.method == 'GET':
        proposal_status = request.GET.get('status', '')
        if proposal_status == 'o':
            proposal_status = 'p'
        proposal_id = request.GET.get('id', '')
        proposalObj = Proposal.objects.get(id=proposal_id)
        proposals = Proposal.objects.select_related('call').filter(reviewer_id=request.user.id)
        my_call_table_data = [prop.call for prop in proposals]
        context = {'my_call_table_data':my_call_table_data, 'proposals':proposals}
        try:
            proposalObj.status = proposal_status
            proposalObj.save()
            return render(request, 'home/my_calls.html', context)

        except ObjectDoesNotExist:
            return render(request, 'home/my_calls.html')
