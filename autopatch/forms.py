from django import forms
from autopatch.models import Server, Errata

class PostForm(forms.Form):
    content = forms.CharField(max_length=256)
    created_at = forms.DateTimeField()

# class NameForm(form.Form):
#     your_name = forms.CharField(label='Your name', max_length=100)

class EmailForm(forms.Form):
    email = forms.EmailField(max_length=256)

class LoginForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput())
    loginname = forms.CharField(max_length=256)
    satellite = forms.CharField(max_length=256)
    environment = forms.ChoiceField(choices=[('dev', 'dev'),('qa', 'qa'),('stage', 'stage'), ('prod', 'prod')], required=True, label='Environment')

class ErratumForm(forms.Form):
    erratum = forms.CharField(max_length=256)
    environment = forms.ChoiceField(choices=[('dev', 'dev'),('qa', 'qa'),('stage', 'stage'), ('prod', 'prod')], required=True, label='Environment')

class ErrataForm(forms.Form):
    RHEA = forms.CharField(required=False, widget=forms.TextInput(attrs={'size': 25, 'class': 'form-control', 'placeholder': 'RHEA-2015:1625'}))
    RHSA = forms.CharField(required=False, widget=forms.TextInput(attrs={'size': 25, 'class': 'form-control', 'placeholder': 'RHSA-2015:1640'}))
    RHBA = forms.CharField(required=False, widget=forms.TextInput(attrs={'size': 25, 'class': 'form-control', 'placeholder': 'RHBA-2015:1532'}))

class ServerForm(forms.Form):
    #server = forms.CharField(widget=forms.TextInput(attrs={'size': 25, 'class': 'form-control', 'placeholder': 'server01.example.com'}))
    exclude = forms.CharField(required=False, widget=forms.TextInput(attrs={'size': 25, 'class': 'form-control', 'placeholder': 'jbossas*, openjdk*'}))
    #skip = forms.CharField(widget=forms.TextInput(attrs={'size': 25, 'class': 'form-control', 'placeholder': 'False'}))
    skip = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': 'custom-checkbox'}), initial=True)
    hostgroup = forms.CharField(required=False, widget=forms.TextInput(attrs={'size': 25, 'class': 'form-control', 'placeholder': 'JBoss Servers'}))
    #comments = forms.CharField(required=False, widget=forms.TextArea(attrs={'size': 25, 'class': 'form-control', 'placeholder': 'Jmainguy provisioned this server'}))
    comments = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows':4, 'cols':15}))
    satid = forms.CharField(required=False, widget=forms.TextInput(attrs={'size': 25, 'class': 'form-control', 'placeholder': '0123456'}))
    env = forms.CharField(required=False, widget=forms.TextInput(attrs={'size': 25, 'class': 'form-control', 'placeholder': 'Prod'}))
    #updates = forms.TextInput(attrs={'size': 25, 'class': 'form-control', 'placeholder': 'Updates'})

class HostListForm(forms.Form):
    manifests = forms.CharField(max_length=256)
