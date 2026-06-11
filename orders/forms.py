from django import forms
from .models import Order
import re

PERSIAN_REGEX = r'^[\u0600-\u06FF0-9\s،\-\/]+$'

class OrderForm(forms.ModelForm):

    class Meta:
        model = Order
        fields = [
            "first_name", "last_name", "province", "city", "address",
            "phone", "postal_code", "note",
        ]

        widgets = {
            "first_name": forms.TextInput(attrs={
                "placeholder": "نام*",
                "class": "block w-full py-1.5 px-3 text-base outline dark:outline-none outline-1 -outline-offset-1 placeholder:text-gray-400   transition-all col-span-6 text-gray-800 dark:text-gray-100 dark:bg-gray-900 bg-slate-100 border border-transparent hover:border-slate-200 appearance-none rounded-md outline-none focus:bg-white focus:border-indigo-400 focus:ring-2 focus:ring-indigo-100 dark:focus:ring-blue-400 h-11",

            }),
            "last_name": forms.TextInput(attrs={
                "placeholder": "نام خانوادگی*",
                "class": "block w-full py-1.5 px-3 text-base outline dark:outline-none outline-1 -outline-offset-1 placeholder:text-gray-400   transition-all col-span-6 text-gray-800 dark:text-gray-100 dark:bg-gray-900 bg-slate-100 border border-transparent hover:border-slate-200 appearance-none rounded-md outline-none focus:bg-white focus:border-indigo-400 focus:ring-2 focus:ring-indigo-100 dark:focus:ring-blue-400 h-11",

            }),
            "province": forms.TextInput(attrs={
                "placeholder": "استان*",
                "class": "block w-full py-1.5 px-3 text-base outline dark:outline-none outline-1 -outline-offset-1 placeholder:text-gray-400   transition-all col-span-6 text-gray-800 dark:text-gray-100 dark:bg-gray-900 bg-slate-100 border border-transparent hover:border-slate-200 appearance-none rounded-md outline-none focus:bg-white focus:border-indigo-400 focus:ring-2 focus:ring-indigo-100 dark:focus:ring-blue-400 h-11",

            }),
            "city": forms.TextInput(attrs={
                "placeholder": "شهر*",
                "class": "block w-full py-1.5 px-3 text-base outline dark:outline-none outline-1 -outline-offset-1 placeholder:text-gray-400   transition-all col-span-6 text-gray-800 dark:text-gray-100 dark:bg-gray-900 bg-slate-100 border border-transparent hover:border-slate-200 appearance-none rounded-md outline-none focus:bg-white focus:border-indigo-400 focus:ring-2 focus:ring-indigo-100 dark:focus:ring-blue-400 h-11",

            }),
            "address": forms.TextInput(attrs={
                "placeholder": "آدرس و پلاک منزل*",
                "class": "block w-full py-1.5 px-3 text-base outline dark:outline-none outline-1 -outline-offset-1 placeholder:text-gray-400   transition-all col-span-12 text-gray-800 dark:text-gray-100 dark:bg-gray-900 bg-slate-100 border border-transparent hover:border-slate-200 appearance-none rounded-md outline-none focus:bg-white focus:border-indigo-400 focus:ring-2 focus:ring-indigo-100 dark:focus:ring-blue-400 h-11",

            }),
            "phone": forms.TextInput(attrs={
                "placeholder": "تلفن*",
                "class": "block w-full py-1.5 px-3 text-base outline dark:outline-none outline-1 -outline-offset-1 placeholder:text-gray-400   transition-all col-span-6 text-gray-800 dark:text-gray-100 dark:bg-gray-900 bg-slate-100 border border-transparent hover:border-slate-200 appearance-none rounded-md outline-none focus:bg-white focus:border-indigo-400 focus:ring-2 focus:ring-indigo-100 dark:focus:ring-blue-400 h-11",

            }),
            "postal_code": forms.TextInput(attrs={
                "placeholder": "کد پستی*",
                "class": "block w-full py-1.5 px-3 text-base outline dark:outline-none outline-1 -outline-offset-1 placeholder:text-gray-400   transition-all col-span-6 text-gray-800 dark:text-gray-100 dark:bg-gray-900 bg-slate-100 border border-transparent hover:border-slate-200 appearance-none rounded-md outline-none focus:bg-white focus:border-indigo-400 focus:ring-2 focus:ring-indigo-100 dark:focus:ring-blue-400 h-11",
            }),
            "note": forms.TextInput(attrs={
                "placeholder": "توضیحات",
                "class": "block w-full py-1.5 px-3 text-base outline dark:outline-none outline-1 -outline-offset-1 placeholder:text-gray-400   transition-all col-span-12 h-11 text-gray-800 dark:text-gray-100 dark:bg-gray-900 bg-slate-100 border border-transparent hover:border-slate-200 appearance-none rounded-md outline-none focus:bg-white focus:border-indigo-400 focus:ring-2 focus:ring-indigo-100 dark:focus:ring-blue-400",

            }),
        }

    # -----------------------------
    # Number normalization helper
    # -----------------------------
    def persian_to_english_numbers(self, value):
        persian = "۰۱۲۳۴۵۶۷۸۹"
        english = "0123456789"
        return value.translate(str.maketrans(persian, english))

    # -----------------------------
    # Clean Phone
    # -----------------------------
    def clean_phone(self):
        phone = self.cleaned_data["phone"].strip()
        phone = self.persian_to_english_numbers(phone)

        if not phone.isdigit():
            raise forms.ValidationError("شماره تماس نامعتبر است")

        if len(phone) != 11:
            raise forms.ValidationError("شماره تماس باید 11 رقم باشد")

        return phone

    # -----------------------------
    # Clean Postal Code
    # -----------------------------
    def clean_postal_code(self):
        postal_code = self.cleaned_data["postal_code"].strip()
        postal_code = self.persian_to_english_numbers(postal_code)

        if not postal_code.isdigit() or len(postal_code) != 10:
            raise forms.ValidationError("کد پستی نامعتبر است")

        return postal_code

    # -----------------------------
    # Persian-only validator
    # -----------------------------
    def validate_persian(self, value, field_name):
        value = value.strip()

        if not re.match(PERSIAN_REGEX, value):
            raise forms.ValidationError(f"{field_name} باید فارسی باشد")

        return value

    # -----------------------------
    # Apply Persian validation
    # -----------------------------
    def clean_first_name(self):
        return self.validate_persian(self.cleaned_data["first_name"], "نام")

    def clean_last_name(self):
        return self.validate_persian(self.cleaned_data["last_name"], "نام خانوادگی")

    def clean_province(self):
        return self.validate_persian(self.cleaned_data["province"], "استان")

    def clean_city(self):
        return self.validate_persian(self.cleaned_data["city"], "شهر")

    def clean_address(self):
        value = self.cleaned_data["address"].strip()
        if not re.match(r'^[\u0600-\u06FF0-9\s،\-\/]+$', value):
            raise forms.ValidationError("آدرس نامعتبر است")
        return value
