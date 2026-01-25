from django import forms

class ChatInputForm(forms.Form):
    chat_input = forms.CharField(label="")