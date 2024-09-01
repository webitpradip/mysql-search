from django import forms

class MySQLConnectionForm(forms.Form):
    host = forms.CharField(label='MySQL Host', max_length=100)
    database = forms.CharField(label='Database Name', max_length=100)
    username = forms.CharField(label='Username', max_length=100)
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
    mysql_version = forms.ChoiceField(choices=[('5.7', 'MySQL 5.7'), ('8.0', 'MySQL 8.0')])
    search_text = forms.CharField(label='Search Text', max_length=100)
    clear_log = forms.BooleanField(label='Clear Log and Start New Search', required=False)
