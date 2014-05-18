#!/usr/bin/env python
# Code here literally inspired by axelpale's example on file uploads

from django import forms

class DocumentForm(forms.Form):
    blob = forms.FileField(label='Select a file')
