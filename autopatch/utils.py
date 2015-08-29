import urllib.request, urllib.error, git, shutil, os, glob, random
from django.http import Http404
from .models import Server,Hosttotal,Errata,Owner
from django.shortcuts import get_object_or_404
# for satellite
import xmlrpc.client, xmlrpc.server
from .forms import LoginForm

# TaskScripts are simple debugging functions
class TaskScripts():
    def parseForm(self, form):
        # print("This is the form:",form)
        RHEA = form.data['RHEA']
        errata = Errata.objects.first()
        # errata = errata.RHBA
        # errata = get_object_or_404(Errata, pk=1)
        # errata = Errata.objects.all()
        # server = Server.objects.filter(pk=1)
        # print(server)
        print("This is the errata: ",errata)
        print("This is RHEA",RHEA)
        print("############################")

    def parseSatForm(self, servername, erratas):
        # if form.is_valid():
        #     URL = form.cleaned_data['satellite']
        #     print("This is the Satellite URL",URL)
        # #env = form.data['environment']
        # submit = form.data['submit']
        # print("Form data: ", env, submit)
        print("This is the request: ", servername, erratas)
        # print("This is the form : ", form)
        # print("This is the button: ", btn)

    def parseServerForm(self, test1, test2):
        print("This is the request: ", test1, test2)

# Satellite related util functions
class Satellite():
    def getIds(self, client, request, session, env):
        # This function currently isn't used
        form = LoginForm(request.POST)
        # env = form.data['environment']
        context = {'encouragement': encouragement()}
        # print("Made it to utils: ",request)
        # print("This is the environment: ",env)
        if(env=="dev"):
            dev_list = Server.objects.all().filter(env="dev").order_by('server')[:5]
            for host in dev_list:
                servername = host.server
                URL = "https://satellite.corp.redhat.com/rpc/api"
                print("Servername: ",servername)
        return context

    def desiredErrata(self, updates):
        advisories = ['RHEA','RHSA','RHBA']
        needed_updates = []
        errata = Errata.objects.first()
        errata_levels = {}
        if errata:
            errata_levels['rhea'] = errata.RHEA
            errata_levels['rhsa'] = errata.RHSA
            errata_levels['rhba'] = errata.RHBA
        # print("The errata levels", errata_levels, "These are the updates available",updates)
        # Parses the errata levels for the date and ID
        if errata_levels:
            if errata_levels['rhea']:
                rhea_date = errata_levels['rhea'].split('-')[1].split(':')[0]
                rhea_id = errata_levels['rhea'].split('-')[1].split(':')[1]
                # print("These are the RHEA errata from utils.py:",rhea_date,rhea_id)
            else:
                rhea_date = 0
                rhea_id = 0
                # print("These are the RHEA errata from utils.py:",rhea_date,rhea_id)
            if errata_levels['rhsa']:
                rhsa_date = errata_levels['rhsa'].split('-')[1].split(':')[0]
                rhsa_id = errata_levels['rhsa'].split('-')[1].split(':')[1]
                # print("These are the RSEA errata from utils.py:",rhsa_date,rhsa_id)
            else:
                rhsa_date = 0
                rhsa_id = 0
                # print("These are the RSEA errata from utils.py:",rhsa_date,rhsa_id)
            if errata_levels['rhba']:
                rhba_date = errata_levels['rhba'].split('-')[1].split(':')[0]
                rhba_id = errata_levels['rhba'].split('-')[1].split(':')[1]
                # print("These are the RBEA errata from utils.py:",rhba_date,rhba_id)
            else:
                rhba_date = 0
                rhba_id = 0
                # print("These are the RBEA errata from utils.py:",rhba_date,rhba_id)
            # Iteritively checks each available errata with the errata level
            for each in updates:
                if any(x in each for x in advisories):
                    adv_type = each.split('-')[0]
                    date = each.split('-')[1].split(':')[0]
                    errata_id = each.split('-')[1].split(':')[1]
                    # print("The data and id of the advisory are: ", each, adv_type,date, errata_id)
                    # If the available errata is equal to or older than the level
                    # it is added to the needed_updates list
                    # and it be saved as Server.plerrata
                    if adv_type == 'RHEA':
                        if date < rhea_date:
                            needed_updates.append(each)
                        elif date <= rhea_date and errata_id <= rhea_id:
                            needed_updates.append(each)
                        else:
                            pass
                    if adv_type == 'RHSA':
                        if date < rhsa_date:
                            needed_updates.append(each)
                        elif date <= rhsa_date and errata_id <= rhsa_id:
                            needed_updates.append(each)
                        else:
                            pass
                    if adv_type == 'RHBA':
                        if date < rhba_date:
                            needed_updates.append(each)
                        elif date <= rhba_date and errata_id <= rhba_id:
                            needed_updates.append(each)
                        else:
                            pass
                else:
                    pass
            # print("These are the needed updates!:",needed_updates)
            return needed_updates

    # Used when errata levels are set to recalc Server.plerrata or planned errata
    def recalcPlerrata(self):
        if Server.objects.all():
            for host in Server.objects.all().filter(env="dev").order_by('server'):
                # print("hostname:",host.server)
                # If updates it will calculate the needed_updates
                if host.updates and host.satid:
                    updates = host.updates.replace(" ","").split(',')
                    # print("These are the host updates: ", updates)
                    needed_updates = Satellite().desiredErrata(updates)
                    host.plerrata = str(needed_updates).strip('[]').replace("'","")
                    # print("recalcErrata info:",host.server,":",needed_updates)
                    # Updates whether the host still needs patched
                    if needed_updates:
                        # host.plerrata = needed_updates
                        host.uptodate = 0
                        host.save()
                    # host doesn't need patched
                    else:
                        host.uptodate = 1
                        host.save()
                        # print("host.uptodate",host.server, host.uptodate)
                # marks host as not need patched if no "updates"
                elif host.satid:
                    host.uptodate = 1
                    host.save()
                    # print("host.uptodate",host.server, host.uptodate)
                else:
                    # print("host.uptodate",host.server, "no updates")
                    pass
        else:
            # print("No servers to update the desired errata.")
            pass

class ModMaint():
    # Function called by Git view that imports host data from a git repo by cloning
    def parseGit(self, manifests):
        # unwanted_owners is a list of syspatch_owner attribs that will be ignored
        unwanted_owners = ModMaint().unwantedOwners()
        git_path = 'autopatch/manifests'
        if not os.path.isdir(git_path):
            repo = git.Repo.clone_from(manifests,'autopatch/manifests')
            # print("this is the repo: ",repo)
        else:
            shutil.rmtree(git_path)
            repo = git.Repo.clone_from(manifests,'autopatch/manifests')
            # print("The path already exists",git_path)
        host_paths = []
        host_paths.extend(glob.glob(git_path+'/nodes/*'))
        # print("Host Paths",host_paths)
        for each in host_paths:
            # print("This is the host path: ",each)
            mgmt = ''
            hostgroup = ''
            exclude = ''
            skip = ''
            comments = ''
            owner = ''
            pathname = each+'/maint.yaml'
            if os.path.exists(pathname):
                with open(pathname, 'rt') as myfile:
                    lines = myfile.readlines()
                    for i in lines:
                        if 'syspatch_mgmt: IT-Platops' == i.split("\n")[0]:
                            mgmt = i.split(":")[1].strip().split("\n")[0]
                        if 'syspatch_hostgroup' == i.split(":")[0]:
                            hostgroup = i.split(":")[1].strip().split("\n")[0]
                        if 'syspatch_yum_excludes' == i.split(":")[0]:
                            exclude = i.split(":")[1].strip().split("\n")[0]
                        if 'syspatch_skip' == i.split(":")[0]:
                            # skip = i.split(":")[1].strip().split("\n")[0]
                            if i.split(":")[1].strip().split("\n")[0] is '1':
                                skip = True
                            elif i.split(":")[1].strip().split("\n")[0] is '0':
                                skip = False
                        if 'syspatch_comment' == i.split(":")[0]:
                            comments = i.split(":")[1].strip().split("\n")[0]
                        if 'syspatch_owner' == i.split(":")[0]:
                            owner = i.split(":")[1].strip().split("\n")[0]
                    servername = each.split('/')[-1]
                    # ignoring hosts that have an owner in unwanted_owners
                    if any(x in owner for x in unwanted_owners):
                        print("The following server is unwanted: ", servername)
                    elif Server.objects.filter(server=servername).exists():
                        # print("servername is being created/modified: ",servername)
                        s = Server.objects.get(server=servername)
                        s.mgmt = mgmt
                        s.exclude = exclude
                        s.skip = skip
                        s.hostgroup = hostgroup
                        s.comments = comments
                        s.env = ModMaint().setEnv(servername)
                        s.owner = owner
                        # print("server: ",s.server)
                        s.save()
                    else:
                        s = Server(server=servername)
                        s.server = each.split('/')[-1]
                        s.mgmt = mgmt
                        s.exclude = exclude
                        s.skip = skip
                        s.hostgroup = hostgroup
                        s.comments = comments
                        s.env = ModMaint().setEnv(servername)
                        s.owner = owner
                        # print("server: ",s.server)
                        s.save()
                myfile.close()
        envs = (('Prod',".prod."), ("Stage",".stage."), ("QA",".qa."), ("Dev",".dev"))
        for env,field in envs:
            total = ModMaint().hostCount(env, field)

    # Function use to create list of hosts to ignore
    def unwantedOwners(self):
        owner_list = []
        owners = Owner.objects.all()
        for item in owners:
            owner = item.owner
            owner_list.append(owner)
        return owner_list

    def setEnv(self, server):
        env = ""
        if ".prod." in server or ".util" in server:
            env = "prod"
            # print("1st check:", server, " in: ",env)
        elif ".dev" not in server and  ".stage." not in server and ".qa." not in server:
            env = "prod"
            # print("2nd check:", server, " in: ",env)
        elif ".stage" in server:
            env = "stage"
            # print("3rd check:", server, " in: ",env)
        elif ".qa." in server:
            env = "qa"
            # print("4rd check:", server, " in: ",env)
        elif ".dev" in server:
            env = "dev"
            # print("5rd check:", server, " in: ",env)
        else:
            env = "unassigned"
        return env

    def getMaint(self, url):
        syspatch = {}
        lines = []
        try:
            myurl = urllib.request.urlopen(url)
            lines = myurl.readlines()
        except urllib.error.HTTPError as e:
            # raise Http404("Poll does not exist")
            pass
        mgmt = ""
        hostgroup = ""
        exclude = ""
        skip = ""
        for i in lines:
            if b'syspatch_mgmt: IT-Platops' == i.split(b"\n")[0]:
                mgmt = i.split(b":")[1].strip().split(b"\n")[0]
            if b'syspatch_hostgroup' == i.split(b":")[0]:
                hostgroup = i.split(b":")[1].strip().split(b"\n")[0]
            if b'syspatch_yum_excludes' == i.split(b":")[0]:
                exclude = i.split(b":")[1].strip().split(b"\n")[0]
            if b'syspatch_skip' == i.split(b":")[0]:
                skip = i.split(b":")[1].strip().split(b"\n")[0]
            syspatch = {'mgmt': mgmt, 'hostgroup': hostgroup, 'exclude': exclude, 'skip': skip}
            # print(syspatch)
            # if syspatch is not dict:
            # syspatch = {}
        return syspatch

    def genCSV(self, servers):
        s = []
        params = [['Hostname','Excluded packages','Skip','Hostgroup','Comments','Pastebin Link (If Errors Are Present)']]
        # for host in Server.objects.all():
        for each in servers:
            host = Server.objects.all().get(server=each)
            # print("THIS IS THE HOST: ",host)
            hostname = host.server
            # print("THIS IS THE HOSTNAME: ",hostname)
            exclude = host.exclude
            skip = host.skip
            hostgroup = host.hostgroup
            comments = host.comments
            params.append([hostname, exclude, skip, hostgroup])
        return params

    def hostCount(self, env, field):
        Hosttotal.objects.all().filter(env=env).delete()
        total = 0
        for each in Server.objects.all().order_by("server"):
            s = each.server
            if env == 'Prod':
                if ".prod." in s or ".util" in s:
                    total += 1
                    # print("1st check servername: ",s)
                elif ".dev" not in s and  ".stage." not in s and ".qa." not in s:
                    total += 1
                    # print("2nd check servername: ",s)
                else:
                    # print(s,"Not a server in: ",env)
                    pass
            else:
                if field in s:
                    total += 1
                    # print("servername: ",s)
                else:
                    # print("Not a server in: ",env)
                    pass
        t = Hosttotal(env=env)
        t.env = env
        t.total = total
        total = {'env': t.env, 'total': t.total}
        t.save()
        return total

    def checkErrata(self, errata_list):
        clear = ['Clear', 'clear', 'CLEAR']
        new_erratas = {}
        #print("This is the errata_list: ", errata_list)
        for key,item in errata_list.items():
            if any(x in item for x in clear):
                errata_object = 'clear'
                TaskScripts().parseServerForm('clearing',errata_object)
                new_erratas[key] = errata_object
            else:
                errata_object = item
                TaskScripts().parseServerForm('saving',errata_object)
                new_erratas[key] = errata_object
        #print("this is the new_erratas: ",new_erratas)
        return new_erratas

def encouragement():
    return random.choice(['You are wonderful.',
                          'You have a phenomenal attitude.',
                          'You are the wind beneath my wings.',
                          'You are crazy, but in a good way.',
                          'I wish I was more like you.',
                          'I admire your strength and perseverance.',
                          'You are an incredibly sensitive person who inspires joyous feelings in all those around you.',
                          'Stay Classy',
                          'Be excellent to each other.'])
