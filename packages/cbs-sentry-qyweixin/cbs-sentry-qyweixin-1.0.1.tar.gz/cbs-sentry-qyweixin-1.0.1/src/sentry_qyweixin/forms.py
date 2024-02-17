# coding: utf-8

from django import forms


class QYWeixinOptionsForm(forms.Form):
    access_token = forms.CharField(
        max_length=255,
        help_text='QYWeixin Robot access_token'
    )
    title = forms.CharField(
        max_length=255,
        help_text='QYWeixin Robot title'
    )
