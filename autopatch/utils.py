import urllib.request, urllib.error, git, shutil, os, glob, random, xmlrpc.client, xmlrpc.server
from .models import Server,Hosttotal,Errata,Owner,Packages

from django.http import Http404
from django.shortcuts import get_object_or_404

# for satellite
from .forms import LoginForm

# TaskScripts are simple debugging functions
class TaskScripts():
    def parseServerForm(self, test1, test2):
        print("This is the request: ", test1, test2)

# Satellite related util functions
class Satellite():
    def getIds(self, client, request, session, env):
        # This function currently isn't used
        form = LoginForm(request.POST)
        context = {'encouragement': encouragement()}
        # print("Made it to utils: ",request)
        # print("This is the environment: ",env)
        if(env=="dev"):
            dev_list = Server.objects.all().filter(env="dev").order_by('server')
            for host in dev_list:
                servername = host.server
                URL = "https://satellite.corp.redhat.com/rpc/api"
                # print("Servername: ",servername)
        return context

    # function that determines Errata that needs installed
    def desiredErrata(self, updates):
        updates = list(updates)
        # print("attempting to make a list of updates:",type(updates), updates, "updates")
        advisories = ['RHEA','RHSA','RHBA']
        needed_updates = []
        errata = Errata.objects.first()
        errata_levels = {}
        if errata:
            errata_levels['rhea'] = errata.RHEA
            errata_levels['rhsa'] = errata.RHSA
            errata_levels['rhba'] = errata.RHBA
        # Parses the errata levels for the date and ID
        if errata_levels:
            if errata_levels['rhea']:
                rhea_date = int(errata_levels['rhea'].split('-')[1].split(':')[0])
                rhea_id = int(errata_levels['rhea'].split('-')[1].split(':')[1])
                # print("These are the RHEA errata from utils.py:",rhea_date,rhea_id)
            else:
                rhea_date = 0
                rhea_id = 0
                # print("These are the RHEA errata from utils.py:",rhea_date,rhea_id)
            if errata_levels['rhsa']:
                rhsa_date = int(errata_levels['rhsa'].split('-')[1].split(':')[0])
                rhsa_id = int(errata_levels['rhsa'].split('-')[1].split(':')[1])
                # print("These are the RSEA errata from utils.py:",rhsa_date,rhsa_id)
            else:
                rhsa_date = 0
                rhsa_id = 0
                # print("These are the RSEA errata from utils.py:",rhsa_date,rhsa_id)
            if errata_levels['rhba']:
                rhba_date = int(errata_levels['rhba'].split('-')[1].split(':')[0])
                rhba_id = int(errata_levels['rhba'].split('-')[1].split(':')[1])
                # print("These are the RBEA errata from utils.py:",rhba_date,rhba_id)
            else:
                rhba_date = 0
                rhba_id = 0
            # Iteritively checks each available errata with the errata level
            for each in updates:
                if any(x in each for x in advisories):
                    adv_type = each.split('-')[0]
                    date = int(each.split('-')[1].split(':')[0])
                    errata_id = int(each.split('-')[1].split(':')[1])
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
            needed_updates = set(needed_updates)
            return needed_updates

    # Used when errata levels are set to recalc Server.plerrata or planned errata
    def recalcPlerrata(self):
        if Server.objects.all():
            # for host in Server.objects.all().filter(env="dev").order_by('server'):
            for host in Server.objects.all().order_by('server'):
                # print("hostname:",host.server)
                # If updates it will calculate the needed_updates
                if host.updates and host.satid:
                    # The eval method should make the host.updates a set
                    # print("Host updates: ", host.server, "host.updates:", host.updates, "host.satid", host.satid)
                    updates = host.updates.strip('{}').split(",")
                    # print("These are the stored updates: ", type(host.updates), host.updates)
                    # print("These are the formatted host updates: ", type(updates), updates)
                    needed_updates = Satellite().desiredErrata(updates)
                    # print("recalcErrata info:",host.server,":",needed_updates)
                    # Updates whether the host still needs patched
                    if needed_updates:
                        host.plerrata = str(needed_updates).replace("'",'"')
                        # print("This is the needed errata:", type(needed_updates), needed_updates, ":", host.plerrata)
                        host.uptodate = 0
                        host.save()
                    # host doesn't need patched
                    else:
                        host.plerrata = None
                        host.uptodate = 1
                        host.save()
                        # print("host.uptodate",host.server, host.uptodate)
                # marks host as not need patched if no "updates"
                elif host.satid:
                    host.plerrata = None
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
        # retrieve the syspatch_* parameters
        for each in host_paths:
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
                        # print("The following server is unwanted: ", servername)
                        pass
                    elif Server.objects.filter(server=servername).exists():
                        # Checks if the server exists and updates with what is in git
                        # print("servername is being created/modified: ",servername)
                        s = Server.objects.get(server=servername)
                        s.mgmt = mgmt
                        s.exclude = exclude
                        s.skip = skip
                        s.hostgroup = hostgroup
                        s.comments = comments
                        s.env = ModMaint().setEnv(servername)
                        s.owner = owner
                        s.save()
                    else:
                        # server didn't exist in database so it is created in the Server model
                        s = Server(server=servername)
                        s.server = each.split('/')[-1]
                        s.mgmt = mgmt
                        s.exclude = exclude
                        s.skip = skip
                        s.hostgroup = hostgroup
                        s.comments = comments
                        s.env = ModMaint().setEnv(servername)
                        s.owner = owner
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
        elif ".dev" not in server and  ".stage." not in server and ".qa." not in server:
            env = "prod"
        elif ".stage" in server:
            env = "stage"
        elif ".qa." in server:
            env = "qa"
        elif ".dev" in server:
            env = "dev"
        else:
            env = "unassigned"
        return env

    def genCSV(self, servers):
        # function that creates a .csv file with server and syspatch parameters from the Django database
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

    # counts the total number of hosts in an environment
    def hostCount(self, env, field):
        Hosttotal.objects.all().filter(env=env).delete()
        total = 0
        for each in Server.objects.all().order_by("server"):
            s = each.server
            # prod has .util. in the hostname so that needs checked as well
            if env == 'Prod':
                if ".prod." in s or ".util" in s:
                    total += 1
                elif ".dev" not in s and  ".stage." not in s and ".qa." not in s:
                    total += 1
                else:
                    pass
            else:
                if field in s:
                    total += 1
                else:
                    pass
        t = Hosttotal(env=env)
        t.env = env
        t.total = total
        total = {'env': t.env, 'total': t.total}
        t.save()
        return total

    # function that sets host totals for each env
    def allHostTotals(self):
        envs = (('Prod',".prod."), ("Stage",".stage."), ("QA",".qa."), ("Dev",".dev"))
        for env,field in envs:
            total = ModMaint().hostCount(env, field)

    # used to check if an errata leve needs cleared
    def checkErrata(self, errata_list):
        clear = ['Clear', 'clear', 'CLEAR']
        new_erratas = {}
        # checks if someone entered clear
        for key,item in errata_list.items():
            if any(x in item for x in clear):
                errata_object = 'clear'
                new_erratas[key] = errata_object
            else:
                errata_object = item
                new_erratas[key] = errata_object
        #print("this is the new_erratas: ",new_erratas)
        return new_erratas

    # Used delete servers of owners who were excluded and to get a list of the owners
    def excludedOwners(self):
        # Creates a list for output to the autopatch/owners.html template
        if Owner.objects.all():
            servers = []
            server_list = []
            owners_list = Owner.objects.all().order_by('owner')
            # Deleting the servers owned by each excluded owner
            for item in owners_list:
                exclude = item.owner
                Server.objects.filter(owner=exclude).delete()
        else:
            owners_list = []
        return owners_list

    def errataPackages(self, errata_dict):
        for errata in errata_dict:
            # print("Errata and dict value:",errata,errata_dict[errata])
            if not Packages.objects.filter(errata=errata).exists():
                p = Packages(errata=errata)
                p.pkgs = errata_dict[errata]
                # print("The errata doesn't exist in the model ", p)
                p.save()
            else:
                # print("The errata already does exists: ", errata)
                pass
        # for each in Packages.objects.all():
            # print("From the model", each.errata, each.pkgs)
            # print("Packages and type", each.pkgs, type(each.pkgs))
            # pkg_list = eval(each.pkgs)
            # print("The evaluated pkgs list: ", type(pkg_list))
        return True

    def errataExcluded(self, servername):
        # print("############################################")
        # print("The servername input to errataExcluded is: ", servername)
        new_errata = []
        s = Server.objects.get(server=servername)
        # print("The server:", s.server, "the syspatch_yum_excludes", s.exclude)
        excluded_packages = s.exclude.replace(" ",",").split(",")
        # print("These are the excluded packages for: ", s.server,"excludes in list for:", excluded_packages)
        for each in Packages.objects.all():
            errata = each.errata
            # print("This is the list of errata and type", s.plerrata, type(s.plerrata))
            plerrata = eval(s.plerrata)
            # print("THIS is the PLERRATA and type:", plerrata, type(plerrata))
            pkg_list = eval(each.pkgs)
            if any(x in pkg_list for x in excluded_packages):
                # print("This errata IS SOO excluded", errata)
                pass
            elif errata in plerrata:
                # print("The following errata is NOT exlcuded", errata)
                new_errata.append(errata)
            else:
                # print("This ERRATA DEFINATELY does not need updates:", errata)
                pass
        new_errata = set(new_errata)
        new_errata = str(new_errata).replace("'",'"')
        s.plerrata = new_errata
        s.save()
        # print("This is the new_errata set: ", new_errata, type(new_errata))
        # print("############################################")

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
