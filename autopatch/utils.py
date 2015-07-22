import urllib

class ModMaint():
    def getMaint(self, url):
        syspatch = []
        myurl = urllib.urlopen(url)
        lines = myurl.readlines()
        mgmt = None
        hostgroup = None
        exclude = None
        skip = None
        for i in lines:
            if 'syspatch_mgmt: IT-Platops' == i.split("\n")[0]:
                mgmt = i.split(":")[1].strip().split("\n")[0]
            if 'syspatch_hostgroup' == i.split(":")[0]:
                hostgroup = i.split(":")[1].strip().split("\n")[0]
            if 'syspatch_yum_excludes' == i.split(":")[0]:
                exclude = i.split(":")[1].strip().split("\n")[0]
            if 'syspatch_skip' == i.split(":")[0]:
                skip = i.split(":")[1].strip().split("\n")[0]
            syspatch = {'mgmt': mgmt, 'hostgroup': hostgroup, 'exclude': exclude, 'skip': skip}
        print syspatch
        if syspatch is not dict:
            syspatch = {}
        return syspatch
