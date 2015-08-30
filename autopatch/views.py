from django.shortcuts import render, get_object_or_404, render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
#Class Views
from django.views import generic
from django.views.generic import TemplateView
from django.views.generic.edit import FormView

from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.utils import timezone

from django.core.context_processors import csrf
from time import sleep
from django.contrib.auth.backends import RemoteUserBackend
import urllib, bs4, urllib.request, csv
from xmlrpc import client, server
import xmlrpc.client, xmlrpc.server

from .forms import PostForm, EmailForm, ServerForm, HostListForm, LoginForm, ErrataForm
from .models import Server, Hosttotal, Errata, Owner
from autopatch.utils import ModMaint, TaskScripts, encouragement, Satellite

from django.views.decorators.debug import sensitive_variables
from django.views.decorators.debug import sensitive_post_parameters

def CreateCSV(request):
    s = []
    q = []
    context = {}
    #if request.GET:
    if(request.GET.get('devbtn')):
        dev_list = Server.objects.all().filter(env="dev").order_by('server')
        for host in dev_list:
            s.append(host.server)
    elif(request.GET.get('qabtn')):
        qa_list = Server.objects.all().filter(env="qa").order_by('server')
        for host in qa_list:
            s.append(host.server)
    elif(request.GET.get('stagebtn')):
        stage_list = Server.objects.all().filter(env="stage").order_by('server')
        for host in stage_list:
            s.append(host.server)
    elif(request.GET.get('prodbtn')):
        prod_list = Server.objects.all().filter(env="prod").order_by('server')
        for host in prod_list:
            s.append(host.server)
    else:
        pass
    params = ModMaint().genCSV(s)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="patching.csv"'
    writer = csv.writer(response)
    for each in params:
        writer.writerow(each)
    return response

# Funtion used to import hosts from git by cloning the repo
def Git(request):
    unlist = []
    #Checks if a path was give to the git repo
    if(request.GET.get('mybtn')):
        manifests = str(request.GET.get('gitpath'))
    elif(request.GET.get('clear')):
        Server.objects.all().delete()
        manifests = None
    else:
        manifests = None
    # if a path was give this call parseGit which does the
    # importing of FQDNs and syspatch_* parameters to the Server model
    if manifests:
        # Server.objects.all().delete()
        hosts = ModMaint().parseGit(manifests)
    else:
        pass
    # unsassignlist (not in an env) hosts are displayed on the patching-tasks.html template
    unassignlist = Server.objects.all().filter(env="unassigned").order_by('server')
    for each in unassignlist:
        unhost = each.server
        unlist.append(unhost)
    context = {'unlist': unlist, 'encouragement': encouragement()}
    return HttpResponseRedirect(reverse('autopatch:tasks'), context)

# hosts of owners set here will be excluded from patching
def SetOwners(request):
    # owners is a test variable
    owners_list = []
    owner_list = Owner.objects.all().order_by('owner')
    # If the "Set Owners" button is pressed
    if request.GET.get('addowners'):
        owners = str(request.GET.get('owners'))
        owners_list = owners.split(",")
        for each in owners_list:
            cl_owner = each.strip()
            if not Owner.objects.filter(owner=cl_owner).exists():
                owner = Owner(owner=cl_owner)
                owner.owner = cl_owner
                owner.save()
                # owners_list = ['success']
            else:
                # owners_list = ['failure']
                pass
    # If the "Remove Owners" button is pressed
    elif request.GET.get('delowners'):
        Owner.objects.all().delete()
    else:
        pass
    # Creates a list for output to the autopatch/owners.html template
    if Owner.objects.all():
        servers = []
        server_list = []
        owners_list = Owner.objects.all().order_by('owner')
        for item in owners_list:
            exclude = item.owner
            # if Server.objects.filter(owner=exclude).exists():
            #     for host in servers:
            #         s = Server.objects.filter(owner=exclude)
            #         server_list.append(s.server)
            # else:
            #     pass
            Server.objects.filter(owner=exclude).delete()
            # TaskScripts().parseServerForm(server_list,exclude)
    else:
        owners_list = []
    context = {'owner_list': owner_list, 'encouragement': encouragement(), 'owners_list': owners_list}
    return render(request, 'autopatch/owners.html', context)

def UpdateErrata(request):
    # This view used to update the top level errata
    if request.POST:
        # errata = Errata.objects.filter(pk=1)
        form = ErrataForm(request.POST)
        # form = ErrataForm(pk=1)
        if form.is_valid():
            new_erratas = {}
            # TaskScripts().parseForm(form)
            # saving the errata levels entered in the form
            RHEA = form.data['RHEA']
            RHSA = form.data['RHSA']
            RHBA = form.data['RHBA']
            oldrhea = ''
            oldrhsa = ''
            oldrhba = ''
            # errata = Errata.objects.get(pk=1)
            # TaskScripts().parseServerForm('Errata',errata)
            # This keeps the exists errata levels set if none are entered in the form
            if not Errata.objects.exists():
                errata = Errata(pk=1)
            else:
                errata = Errata.objects.get(pk=1)
                oldrhea = errata.RHEA
                oldrhsa = errata.RHSA
                oldrhba = errata.RHBA
            errata_list = {'RHEA': RHEA, 'RHSA': RHSA, 'RHBA': RHBA}
            # checkErrata is a check for any clear returns to remove errata levels
            new_erratas = ModMaint().checkErrata(errata_list)
            if new_erratas['RHEA'] == 'clear':
                errata.RHEA = ''
            elif new_erratas['RHEA']:
                errata.RHEA = RHEA
            elif oldrhea:
                errata.RHEA = oldrhea
            else:
                pass
            if new_erratas['RHSA'] == 'clear':
                errata.RHSA = ''
            elif new_erratas['RHSA']:
                errata.RHSA = RHSA
            elif oldrhsa:
                errata.RHSA = oldrhsa
            else:
                pass
            if new_erratas['RHBA'] == 'clear':
                errata.RHBA = ''
            elif new_erratas['RHBA']:
                errata.RHBA = RHBA
            elif oldrhba:
                errata.RHBA = oldrhba
            else:
                pass
            errata.save()
            # recalculates the desired errata for each host
            Satellite().recalcPlerrata()
            return HttpResponseRedirect(reverse('autopatch:errata'))
    else:
        form = ErrataForm()
    args = {}
    args.update(csrf(request))
    # Checking if errata levels exist
    # if they exist then they are returned to the template
    if Errata.objects.exists():
        # errata = Errata.objects.first()
        errata = Errata.objects.first()
        args['RHEA'] = errata.RHEA
        args['RHSA'] = errata.RHSA
        args['RHBA'] = errata.RHBA
        # TaskScripts().parseServerForm('Errata does exist',errata)
    else:
        args['RHEA'] = 0
        args['RHSA'] = 0
        args['RHBA'] = 0
        # TaskScripts().parseServerForm('Errata doesnt exist!','no errata')
    args['form'] = form
    return render_to_response('autopatch/update_errata.html', args)

def Home(request):
    template = 'autopatch/base.html'
    context = {'encouragement': encouragement()}
    return render(request, template, context)

def ProdView(request):
    env = "Prod"
    field = ".prod."
    if Hosttotal.objects.filter(env=env).exists():
        h = Hosttotal.objects.get(env=env)
        prodtotal = h.total
    else:
        prodtotal = None
    if(request.GET.get('mybtn')):
        total = ModMaint().hostCount(env, field)
        prodtotal = total.get("total")
    prod_list = Server.objects.all().filter(env="prod").order_by('server')
    context = {'host_list': prod_list, 'total': prodtotal, 'env': env, 'encouragement': encouragement()}
    return render(request, 'autopatch/host_list.html', context)

def StageView(request):
    env = "Stage"
    field = ".stage."
    if Hosttotal.objects.filter(env=env).exists():
        h = Hosttotal.objects.get(env=env)
        stagetotal = h.total
    else:
        stagetotal = None
    if(request.GET.get('mybtn')):
        total = ModMaint().hostCount(env, field)
        stagetotal = total.get("total")
    stage_list = Server.objects.all().filter(env="stage").order_by('server')
    context = {'host_list': stage_list, 'total': stagetotal, 'env': env, 'encouragement': encouragement()}
    return render(request, 'autopatch/host_list.html', context)

def QAView(request):
    env = "QA"
    field = ".qa."
    if Hosttotal.objects.filter(env=env).exists():
        h = Hosttotal.objects.get(env=env)
        qatotal = h.total
    else:
        qatotal = None
    if(request.GET.get('mybtn')):
        total = ModMaint().hostCount(env, field)
        qatotal = total.get("total")
    qa_list = Server.objects.all().filter(env="qa").order_by('server')
    context = {'host_list': qa_list, 'total': qatotal, 'env': env, 'encouragement': encouragement()}
    return render(request, 'autopatch/host_list.html', context)

def DevView(request):
    env = "Dev"
    field = ".dev"
    if Hosttotal.objects.filter(env=env).exists():
        h = Hosttotal.objects.get(env=env)
        devtotal = h.total
    else:
        devtotal = None
    if(request.GET.get('mybtn')):
        total = ModMaint().hostCount(env, field)
        devtotal = total.get("total")
    dev_list = Server.objects.all().filter(env="dev").order_by('server')
    context = {'host_list': dev_list, 'total': devtotal, 'env': env, 'encouragement': encouragement()}
    return render(request, 'autopatch/host_list.html', context)

@sensitive_post_parameters()
@sensitive_variables()
def SatId(request):
    # SatId will get the ID of each server in Satellite
    # There are 4 buttons on the patching tasks page, one for each env
    context = {'encouragement': encouragement()}
    if request.POST:
        form = LoginForm(request.POST)
        # TaskScripts().parseSatForm(request, form)
        if form.is_valid():
            # Get variables from the form
            user = form.cleaned_data['loginname']
            pswd = form.cleaned_data['password']
            url = form.cleaned_data['satellite']
            URL = "https://"+url+"/rpc/api"
            env = form.cleaned_data['environment']
            # using xmlrpc to get a session key from the satellite server
            client = xmlrpc.client.Server(URL, verbose=0)
            session = client.auth.login(user, pswd)
            # Get list of hosts in an env
            host_list = Server.objects.all().filter(env=env).order_by('server')
            # Loop through each host and get satellite ID
            for host in host_list:
                servername = host.server
                if host.satid:
                    # TaskScripts().parseSatForm(servername, "already has a satid")
                    pass
                else:
                    client = xmlrpc.client.Server(URL, verbose=0)
                    data = client.system.getId(session, servername)
                    # TaskScripts().parseSatForm(servername, data)
                    if data:
                        getid = data[0].get('id')
                        host.satid = getid
                        # TaskScripts().parseSatForm(servername, getid)
                        host.save()
                    else:
                        pass
            # context = {'getid': getid}
            client.auth.logout(session)
    else:
        pass
    return HttpResponseRedirect(reverse('autopatch:tasks'), context)

@sensitive_variables('pswd', 'password', 'form')
@sensitive_post_parameters('password')
def SatUpdates(request):
    # SatId will get the ID of each server in Satellite
    # There are 4 buttons on the patching tasks page, one for each env
    context = {'encouragement': encouragement()}
    errata_levels = {}
    errata = Errata.objects.first()
    if errata:
        errata_levels['rhea'] = errata.RHEA
        errata_levels['rhsa'] = errata.RHSA
        errata_levels['rhba'] = errata.RHBA
    else:
        pass
    if request.POST:
        form = LoginForm(request.POST)
        # TaskScripts().parseSatForm(request, form)
        if form.is_valid():
            user = form.cleaned_data['loginname']
            pswd = form.cleaned_data['password']
            url = form.cleaned_data['satellite']
            URL = "https://"+url+"/rpc/api"
            env = form.cleaned_data['environment']
            client = xmlrpc.client.Server(URL, verbose=0)
            session = client.auth.login(user, pswd)
            #host_list = Server.objects.all().filter(env=env).order_by('server')
            host_list = Server.objects.all().order_by('server')
            for host in host_list:
                servername = host.server
                if host.satid:
                    updates = []
                    satid = host.satid
                    # TaskScripts().parseSatForm(servername, env)
                    client = xmlrpc.client.Server(URL, verbose=0)
                    errata_list = client.system.getRelevantErrata(session,satid)
                    if errata_list:
                        # TaskScripts().parseSatForm(servername, erratas)
                        for erratum in errata_list:
                            # updates.append(erratum['advisory_name']+' ')
                            updates.append(erratum["advisory_name"])
                            # all_updates = str(updates).strip('[]').replace("'","")
                            all_updates = set(updates)
                            # TaskScripts().parseSatForm(host.server,all_updates)
                        needed_updates = Satellite().desiredErrata(all_updates)
                        # TaskScripts().parseSatForm(needed_updates, all_updates)
                        if needed_updates:
                            # host.plerrata = str(needed_updates).strip('[]').replace("'","")
                            host.plerrata = str(needed_updates).replace("'",'"')
                            # TaskScripts().parseSatForm(servername, host.plerrata)
                            host.uptodate = 0
                        else:
                            host.plerrata = ""
                            host.uptodate = 1
                        host.updates = str(all_updates).replace("'",'"')
                        host.save()
                    else:
                        pass

                else:
                    pass
            client.auth.logout(session)
    else:
        pass
    return HttpResponseRedirect(reverse('autopatch:tasks'), context,)

def resultView(request, pk):
    args = []
    server = get_object_or_404(Server, pk=pk)
    template_name = 'autopatch/results.html'
    hostgroup = "nothing"
    exclude = "nothing"
    skip = []
    if request.POST.get('set_param'):
        form = ServerForm(request.POST)
        # test1 = "Recognizes form"
        # test2 = pk
        # TaskScripts().parseServerForm(test1, test2)
        if form.is_valid():
            exclude = form.data['exclude']
            hostgroup = form.data['hostgroup']
            skip = form.cleaned_data['skip']
            comments = form.cleaned_data['comments']
            s = Server.objects.get(pk=pk)
            # test1 = [exclude, hostgroup, skip, comments]
            # test2 = pk
            # TaskScripts().parseServerForm(test1, test2)
            if exclude:
                s.exclude = exclude
            if hostgroup:
                s.hostgroup = hostgroup
            s.skip = skip
            if comments:
                s.comments = comments
            s.save()
        else:
            # test1 = "Form not valid"
            # test2 = ""
            # TaskScripts().parseServerForm(test1, test2)
            pass
    else:
        # test1 = "Doesn't recognize form"
        # test2 = ""
        # TaskScripts().parseServerForm(test1, test2)
        pass
    id_number = pk
    context = {'exclude': exclude, 'encouragement': encouragement(), 'hostgroup': hostgroup, 'skip': skip}
    return HttpResponseRedirect(reverse('autopatch:detail', kwargs={'pk':id_number}), context)

def DetailView(request, pk):
    server = get_object_or_404(Server, pk=pk)
    if server.updates != None:
        server.updates = server.updates.strip('{}').replace('"','').replace(' ', '').split(',')
    if server.plerrata != None:
        server.plerrata = server.plerrata.strip('{}').replace('"','').replace(' ', '').split(',')
    template_name = 'autopatch/results.html'
    context = {'encouragement': encouragement(), 'server': server}
    return render_to_response('autopatch/results.html', context,
                              context_instance=RequestContext(request))

# Patching Task Related Views
# ##########################################
class TasksView(generic.ListView):
    template_name = 'autopatch/patching-tasks.html'
    def get_queryset(self):
        return Server.objects.all().order_by("server")
    def get_context_data(self):
        return {'encouragement': encouragement()}

class Unicorns(generic.ListView):
    template_name = 'autopatch/unicorns.html'
    def get_queryset(self):
        return Server.objects.all().order_by("server")
    def get_context_data(self):
        return {'encouragement': encouragement()}

def security(request):
    return render(request, 'autopatch/security.html')

# Views not currently being used
# ##########################################
def create(request):
    if request.POST:
        form = ServerForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/autopatch/')
    else:
        form = ServerForm()
    args = {}
    args.update(csrf(request))
    args['form'] = form
    return render_to_response('autopatch/create_server.html', args)

def GetList(request):
    if(request.GET.get('mybtn')):
        # mypythoncode.mypythonfunction( int(request.GET.get('mytextbox')) )
        manifests = str(request.GET.get('mytextbox'))
    else:
        manifests = None
    if manifests:
        # Server.objects.all().delete()
        url_list = []
        paths = []
        mgmt = []
        # host_list = HostList()
        myurl = urllib.request.urlopen(manifests)
        html = myurl.read()
        soup = bs4.BeautifulSoup(html, "html.parser")
        for link in soup.findAll("a"):
            if ".com" in link.string:
                path = link.get("href")
                maint_path = manifests+"/"+link.string+'/maint.yaml'
                syspatch_data = ModMaint().getMaint(maint_path)
                mgmt1 = syspatch_data.get('mgmt')
                exclude1 = syspatch_data.get('exclude')
                skip1 = syspatch_data.get('skip')
                hostgroup1 = syspatch_data.get('hostgroup')
                if not Server.objects.filter(server=link.string).exists():
                    s = Server(server=link.string)
                    s.server = link.string
                    s.mgmt = mgmt1
                    s.exclude = exclude1
                    s.skip = skip1
                    s.hostgroup = hostgroup1
                else:
                    s = Server(server=link.string)
                    s.server = link.string
                    s.mgmt = mgmt1
                    s.exclude = exclude1
                    s.skip = skip1
                    s.hostgroup = hostgroup1
                s.save()
                url_list.append(link.string)
            else:
                pass
        context = {'manifests': manifests, 'url_list': url_list, 'check': "worked", 'paths': paths, 'mgmt1': mgmt1, 'skip1': skip1}
    else:
        context = {'manifests': manifests}
    return render(request, 'autopatch/get_list.html', context)
