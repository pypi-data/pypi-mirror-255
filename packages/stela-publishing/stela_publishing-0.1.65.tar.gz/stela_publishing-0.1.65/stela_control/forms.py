from django import forms
import imghdr, os
from django.core.validators import RegexValidator, EmailValidator, URLValidator
from django.http import JsonResponse
import re, phonenumbers, datetime
from django.contrib.auth.forms import SetPasswordForm, AuthenticationForm, PasswordResetForm
from phonenumbers import geocoder, carrier
from django.core.validators import EmailValidator, MinLengthValidator, MaxLengthValidator
from django.utils.html import strip_tags
from django.utils.text import slugify
from .functions import caption_optimizer
from datetime import date, timedelta
from geolocation.models import City, Country
from django.forms import BaseFormSet
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from crispy_forms.helper import FormHelper
from accounts.models import UserBase
from .models import (
    Newsletter, BillingRecipt, ItemProducts, ItemServices,ItemDiscount, 
    Templates, Content, Inventory, Elements, TemplateSections, StelaColors,
    Variant, Sizes, Gallery, Bulletpoints, VariantsImage, Wallet, DynamicBullets, 
    DataEmail, Category, SitePolicy, LegalProvision, Support, SupportResponse, ChatSupport, 
    FacebookPostPage, FacebookPageComments, FacebookPageCommentsReply,FacebookPageEvent, 
    FacebookPageLikes, FacebookPageMessages, FAQ, Contact, Comments, FacebookPageShares, 
    FacebookPostMedia, IGPost, ContactResponse, IGMediaContent, Company, SocialLinks, ImageGallery,
    SetFaq, Reviews, ProStelaExpert, LiteraryWork, Resource, BillFile, Booking, APIStelaClient, Team,
    JobApplication, ProfileGallery, CommentsWorks
)
import re

text_regex = RegexValidator(r'^[A-Za-zÀ-ÿ0-9,.\s¿¡!?]+$', flags=re.UNICODE, message=_("The text is not valid."))
content_regex = r'^[A-Za-zÀ-ÿ0-9,.\s¿¡!?]+$'
email_regex = RegexValidator(regex=r'^[^@]+@[^@]+\.[^@]+$', message=_("Invalid email format."))
price_regex = RegexValidator(regex=r'^\d+(\.\d{1,2})?$', message="Enter a valid price.")

class DateInput(forms.DateInput):
    input_type = 'text'

FIRST_NAME_PLACEHOLDER = _('Enter your first name')
LAST_NAME_PLACEHOLDER = _('Enter your last name')
EMAIL_PLACEHOLDER = _('Enter your email address')
PHONE_PLACEHOLDER = _('Enter your phone number')
ADDRESS_PLACEHOLDER = _('Enter your address')
POSITION_APPLIED_PLACEHOLDER = _('Enter the position you are applying for')
SALARY_EXPECTATIONS_PLACEHOLDER = _('Enter your salary expectations')
COMMENTS_PLACEHOLDER = _('Any additional comments')

#User Validations
class RegistrationForm(forms.ModelForm):
    email = forms.EmailField(
        validators=[email_regex],
        widget=forms.EmailInput(attrs={
            'class': 'form-control', 'placeholder': _('Email')
        }),
        error_messages={
            'unique': _("This email has already been registered."),
            'invalid': _("Enter a valid email address."),
        },
    )
    username = forms.CharField(
        validators=[text_regex],
        widget=forms.TextInput(attrs={
            'class': 'form-control', 'placeholder': _('Username')
        }),
        error_messages={
            'unique': _("This username is already in use. Please choose a different one."),
            'invalid': _("This username contains invalid characters."),
        },
    )
    full_name = forms.CharField(
        validators=[text_regex],
        widget=forms.TextInput(attrs={
            'class': 'form-control', 'placeholder': _('Full Name') 
        }),
        )
    address = forms.CharField(
        validators=[text_regex],
        widget=forms.TextInput(attrs={
            'class': 'form-control', 'placeholder': _('Address')
        }),
        )
    phone_number = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control', 'placeholder': _('Phone Number')
        }),
        )
    terms = forms.BooleanField(
    required=True, 
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',  
        }),
        label=_("I agree to the terms and conditions"),  
    )
    password1 = forms.CharField(
        strip=False,
        widget=forms.PasswordInput(attrs={
            'autocomplete': 'new-password',
            'class': 'form-control',  
            'placeholder': _("Enter a strong password."), 
        }),
        help_text=_("Enter a strong password.")
    )
    password2 = forms.CharField(
        strip=False,
        widget=forms.PasswordInput(attrs={
            'autocomplete': 'new-password',
            'class': 'form-control',  
            'placeholder': _("Enter the same password for verification."),  
        }),
        help_text=_("Enter the same password for verification.")
    )    
    class Meta:
        model = UserBase
        fields = [
            'email', 'username', 'full_name', 'phone_number', 
            'terms', 'country_profile', 'address', 'city_profile'
        ]

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.fields['city_profile'].queryset = City.objects.none()
        fields_with_labels = ('city_profile', 'country_profile')

        for field_name in self.fields:
            if field_name not in fields_with_labels:  
                self.fields[field_name].label = ''

        if 'country_profile' in self.data:
            try:
                country_id = int(self.data.get('country_profile'))
                self.fields['city_profile'].queryset = City.objects.filter(country_id=country_id).order_by('name')
            except (ValueError, TypeError):
                pass  
        elif self.instance.pk:
            try:
                self.fields['city_profile'].queryset = self.instance.country_profile.city_set.all()
            except:
                self.fields['city_profile'].queryset = City.objects.none()

    def clean_phone_number(self):
        phone_raw = self.cleaned_data.get('phone_number')
        master = UserBase.objects.get(is_superuser=True)
        company = Company.objects.get(owner=master)
        country_code = company.country_legal.code2 
        
        try:
            phone_number = phonenumbers.parse(phone_raw, country_code)
            if not phonenumbers.is_valid_number(phone_number):
                raise ValueError()
            return phonenumbers.format_number(phone_number, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
        except (phonenumbers.phonenumberutil.NumberParseException, ValueError):
            raise ValidationError(_(f'{phone_raw} is not a valid number'))
            
    def clean_email(self):
        email = self.cleaned_data['email']
        if UserBase.objects.filter(email=email).exists():
            raise ValidationError(self.fields['email'].error_messages['unique'])
        return email

    def clean_username(self):
        username = self.cleaned_data['username']
        if UserBase.objects.filter(username=username).exists():
            raise ValidationError(self.fields['username'].error_messages['unique'])
        return username
    
    def clean_password1(self):
        password = self.cleaned_data['password1']
        if len(password) < 8:
            raise forms.ValidationError(_("Password must be at least 8 characters long"))
        if not re.match(r'^[a-zA-Z0-9*.$_]+$', password):
            raise forms.ValidationError(_("Password must contain only alphanumeric characters and some special characters"))
        if password.isdigit():
            raise forms.ValidationError(_("Password must contain at least one letter"))
        if password.isalpha():
            raise forms.ValidationError(_("Password must contain at least one number"))
        return password
    
    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(_('Password_mismatch.'))
        return password2

class LoginForm(forms.Form):
    username = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                'class': 'form-control mb-3', 'placeholder': 'example@email.com', 'id': 'login-username'
                }
            ),
        
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': '**********',
                'id': 'login-pwd',
            }
        )
    )

class UserLoginForm(AuthenticationForm):
    username = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                'class': 'form-control mb-3', 'placeholder': 'example@email.com', 'id': 'login-username'
                }
            ),
        
    )
    password = forms.CharField(widget=forms.PasswordInput(
        attrs={
            'class': 'form-control',
            'placeholder': '********',
            'id': 'login-pwd',
        }
    ))

class UserEditForm(forms.ModelForm):

    email = forms.EmailField(
        validators=[email_regex],
        widget=forms.EmailInput(attrs={
                'class': 'form-control', 'placeholder': _('Email') 
            }),
            )
    username = forms.CharField(
        validators=[text_regex],
        widget=forms.TextInput(attrs={
            'class': 'form-control', 'placeholder': _('Username')
        }),
        )
    full_name = forms.CharField(
        validators=[text_regex],
        widget=forms.TextInput(attrs={
            'class': 'form-control', 'placeholder': _('Full Name') 
        }),
        )
    address = forms.CharField(
        validators=[text_regex],
        widget=forms.TextInput(attrs={
            'class': 'form-control', 'placeholder': _('Address')
        }),
        )
    phone_number = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control', 'placeholder': _('Phone Number')
        }),
        )
    zip = forms.CharField(
        validators=[text_regex],
        widget=forms.TextInput(attrs={
            'class': 'form-control', 'placeholder': _('ZIP/Postal Code')
        }),
        )
    class Meta:
            model = UserBase
            fields = ('email', 'username', 'full_name', 'image', 'country_profile', 'city_profile', 'phone_number', 'address', 'zip')
            
    def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.fields['city_profile'].queryset = City.objects.none()
            self.fields['image'].widget.attrs.update(
                {'class': 'form-control'})
            for field_name in self.fields:
                if field_name != 'image':  
                    self.fields[field_name].label = ''

            if 'country_profile' in self.data:
                try:
                    country_id = int(self.data.get('country_profile'))
                    self.fields['city_profile'].queryset = City.objects.filter(country_id=country_id).order_by('name')
                except (ValueError, TypeError):
                    pass  
            elif self.instance.pk:
                try:
                    self.fields['city_profile'].queryset = self.instance.country_profile.city_set.all()
                except:
                    self.fields['city_profile'].queryset = City.objects.none()

    def clean_phone_number(self):
        phone_raw = self.cleaned_data.get('phone_number')
        master = UserBase.objects.get(is_superuser=True)
        company = Company.objects.get(owner=master)
        country_code = company.country_legal.code2 
        
        try:
            phone_number = phonenumbers.parse(phone_raw, country_code)
            if not phonenumbers.is_valid_number(phone_number):
                raise ValueError()
            return phonenumbers.format_number(phone_number, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
        except (phonenumbers.phonenumberutil.NumberParseException, ValueError):
            raise ValidationError(_(f'{phone_raw} is not a valid number'))
        
class UserPortalForm(forms.ModelForm):
    class Meta:
        model = UserBase
        fields = ('last_login', 'email', 'is_active', 'username', 'full_name', 'image', 
                  'country_profile', 'city_profile', 'phone_number', 'address', 'zip')

    def __init__(self, *args, **kwargs):
        super(UserPortalForm, self).__init__(*args, **kwargs)
        
        # Agregar clases de Bootstrap a todos los widgets
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            
            # Deshabilitar todos los campos excepto 'is_active'
            if field_name != 'is_active':
                field.widget.attrs['disabled'] = 'disabled'
    
class PwdResetForm(PasswordResetForm):

    email = forms.EmailField(
        max_length=254,
        widget=forms.TextInput(attrs={'class': 'form-control mb-3', 'placeholder': 'E-mail','id': 'form-email'}), label=''
    )
    
class PwdResetConfirmForm(SetPasswordForm):
    new_password1 = forms.CharField(
         label=_('New Password'), widget=forms.PasswordInput(
        attrs={'class': 'form-control mb-3', 'placeholder': 'Contraseña', 'id': 'form-newpasswd'}))
     
    new_password2 = forms.CharField(
         label=_('Confirm Password'), widget=forms.PasswordInput(
        attrs={'class': 'form-control mb-3', 'placeholder': 'Contraseña', 'id': 'form-confirmpasswd'}))   
     
    def clean_new_password1(self):
        password = self.cleaned_data['new_password1']
        if len(password) < 8:
            raise forms.ValidationError(_("Password must be at least 8 characters long"))
        if not re.match(r'^[a-zA-Z0-9*.$_]+$', password):
            raise forms.ValidationError(_("Password must contain only alphanumeric characters and some special characters"))
        if password.isdigit():
            raise forms.ValidationError(_("Password must contain at least one letter"))
        if password.isalpha():
            raise forms.ValidationError(_("Password must contain at least one number"))
        return password

class CleanForm(forms.ModelForm):
    class Meta:
        model = UserBase
        fields = ['country_profile','city_profile','phone_number','address']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['city_profile'].queryset = City.objects.none()

        if 'country_profile' in self.data:
            try:
                country_id = int(self.data.get('country_profile'))
                self.fields['city_profile'].queryset = City.objects.filter(country_id=country_id).order_by('name')
            except (ValueError, TypeError):
                pass  # invalid input from the client; ignore and fallback to empty City queryset
        elif self.instance.pk:
            try:
                self.fields['city_profile'].queryset = self.instance.country_profile.city_set.all()
            except:
                self.fields['city_profile'].queryset = City.objects.none()

class DataEmailForm(forms.ModelForm):
    class Meta:
        model = DataEmail
        fields = ['email']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].label = ''
        self.fields['email'].widget.attrs.update(
            {'placeholder': _('Place Your Email')})
        
class CompanyForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        for field_name, field in self.fields.items():
            field.label = ""
            verbose_name = self.Meta.model._meta.get_field(field_name).verbose_name
            field.widget.attrs['placeholder'] = verbose_name
            field.widget.attrs.update(
                {'class': 'form-control'})
            field.required = True
            if 'main_logo' in self.fields:
                self.fields['main_logo'].label = ""
            if 'alter_logo' in self.fields:
                self.fields['alter_logo'].label = ""
            if 'name' in self.fields:
                self.fields['name'].validators.append(text_regex)
            if 'email' in self.fields:
                self.fields['email'].validators.append(email_regex)
            if 'business' in self.fields:
                self.fields['business'].validators.append(text_regex)
            if 'content' in self.fields:
                self.fields['content'].validators.append(text_regex)
            if 'web' in self.fields:
                self.fields['web'].validators.append(text_regex)
            if 'address' in self.fields:
                self.fields['address'].validators.append(text_regex)
                
    class Meta: 
        model = Company
        fields = '__all__'
        exclude = ('owner','city_legal','lang','business')
    
    def clean_phone(self):
        phone=self.cleaned_data.get('phone')
        s = str(phone)
        clean_string = s.replace(" ", "").replace("-", "")
        pattern = r'^\+[\d\s]{10,12}$'
        if not re.match(pattern, clean_string):
            raise forms.ValidationError(_('Only this format is allowed (+123456789)'))
        else:
            clean_number = phonenumbers.parse(clean_string, None)
            if phonenumbers.is_possible_number(clean_number):
                return phone
            else:
                raise forms.ValidationError(_('This phonenumber is not valid'))

class EditCompanyForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        for field_name, field in self.fields.items():
            field.label = ""
            verbose_name = self.Meta.model._meta.get_field(field_name).verbose_name
            field.widget.attrs['placeholder'] = verbose_name
            field.widget.attrs.update(
                {'class': 'form-control'})
            field.required = True
            if 'main_logo' in self.fields:
                self.fields['main_logo'].label = ""
            if 'alter_logo' in self.fields:
                self.fields['alter_logo'].label = ""
            if 'name' in self.fields:
                self.fields['name'].validators.append(text_regex)
            if 'email' in self.fields:
                self.fields['email'].validators.append(email_regex)
            if 'business' in self.fields:
                self.fields['business'].validators.append(text_regex)
            if 'content' in self.fields:
                self.fields['content'].validators.append(text_regex)
            if 'web' in self.fields:
                self.fields['web'].validators.append(text_regex)
            if 'address' in self.fields:
                self.fields['address'].validators.append(text_regex)
        if 'country_legal' in self.data:
            try:
                country_id = int(self.data.get('country_legal'))
                self.fields['city_legal'].queryset = City.objects.filter(country_id=country_id).order_by('name')
            except (ValueError, TypeError):
                pass  
        elif self.instance.pk:
            try:
                self.fields['city_legal'].queryset = self.instance.country_legal.city_set.all()
            except:
                self.fields['city_legal'].queryset = City.objects.none()   
    class Meta: 
        model = Company
        fields = '__all__'
        exclude = ('owner','lang')
    
    def clean_phone(self):
        phone=self.cleaned_data.get('phone')
        s = str(phone)
        clean_string = s.replace(" ", "").replace("-", "")
        pattern = r'^\+[\d\s]{10,12}$'
        if not re.match(pattern, clean_string):
            raise forms.ValidationError(_('Only this format is allowed (+123456789)'))
        else:
            clean_number = phonenumbers.parse(clean_string, None)
            if phonenumbers.is_possible_number(clean_number):
                return phone
            else:
                raise forms.ValidationError(_('This phonenumber is not valid'))
    
class StaffForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ['status', 'full_name', 'description', 'image', 'staff']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control', 'placeholder': _('Status')}),
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Staff Full Name')}),
            'staff': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Staff')}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control' 
            field.widget.attrs['placeholder'] = field.label
            field.label = False
        
        self.fields['image'].widget.attrs.update(
                {'class': 'form-control'})
    
    def clean_image(self):
        image = self.cleaned_data.get("image", False)
        if image:
            if not image.name.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                raise forms.ValidationError(_("Unsupported file format."))
        return image

class EditCompanyForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        for field_name, field in self.fields.items():
            field.label = ""
            verbose_name = self.Meta.model._meta.get_field(field_name).verbose_name
            field.widget.attrs['placeholder'] = verbose_name
            field.widget.attrs.update(
                {'class': 'form-control'})
            field.required = True
            if 'main_logo' in self.fields:
                self.fields['main_logo'].label = ""
            if 'alter_logo' in self.fields:
                self.fields['alter_logo'].label = ""
            if 'name' in self.fields:
                self.fields['name'].validators.append(text_regex)
            if 'email' in self.fields:
                self.fields['email'].validators.append(email_regex)
            if 'business' in self.fields:
                self.fields['business'].validators.append(text_regex)
            if 'content' in self.fields:
                self.fields['content'].validators.append(text_regex)
            if 'web' in self.fields:
                self.fields['web'].validators.append(text_regex)
            if 'address' in self.fields:
                self.fields['address'].validators.append(text_regex)
        if 'country_legal' in self.data:
            try:
                country_id = int(self.data.get('country_legal'))
                self.fields['city_legal'].queryset = City.objects.filter(country_id=country_id).order_by('name')
            except (ValueError, TypeError):
                pass  
        elif self.instance.pk:
            try:
                self.fields['city_legal'].queryset = self.instance.country_legal.city_set.all()
            except:
                self.fields['city_legal'].queryset = City.objects.none()   
    
    class Meta: 
        model = Company
        fields = '__all__'
        exclude = ('owner','lang')
    
    def clean_phone(self):
        phone=self.cleaned_data.get('phone')
        s = str(phone)
        clean_string = s.replace(" ", "").replace("-", "")
        pattern = r'^\+[\d\s]{10,12}$'
        if not re.match(pattern, clean_string):
            raise forms.ValidationError(_('Only this format is allowed (+123456789)'))
        else:
            clean_number = phonenumbers.parse(clean_string, None)
            if phonenumbers.is_possible_number(clean_number):
                return phone
            else:
                raise forms.ValidationError(_('This phonenumber is not valid'))
    
class StaffGalleryForm(forms.ModelForm):
    class Meta: 
            model = ProfileGallery
            fields = ['image']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control' 
            field.widget.attrs['placeholder'] = field.label
            field.label = False

    def clean_image(self):
        image = self.cleaned_data["image"]

        if not image:
            raise forms.ValidationError(_("The image container cannot be empty."))

        image_format = imghdr.what(image)
        if image_format not in ['jpeg', 'png']:
            raise forms.ValidationError(_("The image format is not valid. Only JPEG and PNG files are allowed."))

        return image        

class SocialMediaForm(forms.ModelForm):
    class Meta: 
        model = SocialLinks
        fields = '__all__'
        exclude = ('parent_staff', 'parent_user', 'parent_company',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control' 
            field.widget.attrs['placeholder'] = field.label
            field.label = False
 
class CommentsFormBlog(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CommentsFormBlog, self).__init__(*args, **kwargs)
        self.fields['name'].validators.append(text_regex)
        self.fields['email'].validators.append(email_regex)
        self.fields['name'].label = ''
        self.fields['email'].label = ''
        self.fields['message'].label = ''
        self.fields['message'].required = False
        self.fields['name'].widget.attrs.update({'placeholder': _('Your Name')})
        self.fields['email'].widget.attrs.update({'placeholder': _('Your Email')})
        self.fields['message'].widget.attrs.update({'placeholder': _('Your Message')})
        
    class Meta:
        model = Comments
        fields = ['name', 'email', 'message']

    def clean_message(self):
        message = self.cleaned_data["message"]
        if not message:
            raise forms.ValidationError(_("The message container cannot be empty."))
        return message

class MasterContactForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        for field_name, field in self.fields.items():
            field.label = ""
            verbose_name = self.Meta.model._meta.get_field(field_name).verbose_name
            field.widget.attrs['placeholder'] = verbose_name
            field.widget.attrs.update(
                {'class': 'form-control'})
            field.required = True
            if 'name' in self.fields:
                self.fields['name'].validators.append(text_regex)
            if 'email' in self.fields:
                self.fields['email'].validators.append(email_regex)
            if 'subject' in self.fields:
                self.fields['subject'].validators.append(text_regex)
        
        self.fields['message'].required = False

    class Meta:
        model = Contact
        fields = ['status','name', 'email', 'phone', 'subject', 'message']

    def clean_phone(self):
        phone_raw = self.cleaned_data.get('phone')
        master = UserBase.objects.get(is_superuser=True)
        company = Company.objects.get(owner=master)
        country_code = company.country_legal.code2 
        
        try:
            phone_number = phonenumbers.parse(phone_raw, country_code)
            if not phonenumbers.is_valid_number(phone_number):
                raise ValueError()
            return phonenumbers.format_number(phone_number, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
        except (phonenumbers.phonenumberutil.NumberParseException, ValueError):
            raise ValidationError(_(f'{phone_raw} is not a valid number'))
    
    def clean_message(self):
        message = self.cleaned_data["message"]
        if not message:
            raise forms.ValidationError(_("The message container cannot be empty."))
        return message

class MasterReviewsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        for field_name, field in self.fields.items():
            field.label = ""
            verbose_name = self.Meta.model._meta.get_field(field_name).verbose_name
            field.widget.attrs['placeholder'] = verbose_name
            field.widget.attrs.update(
                {'class': 'form-control'})
            field.required = True

            if 'content' in self.fields:
                self.fields['content'].validators.append(text_regex)
                self.fields['content'].widget.attrs['readonly'] = True

        
        self.fields['content'].required = False

    class Meta:
        model = Reviews
        fields = ['status', 'content'] 

    def clean_content(self):
        content = self.cleaned_data["content"]
        
        if not content:
            raise forms.ValidationError(_("The message is required."))

        return content

class MasterCommentsFormBlog(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        for field_name, field in self.fields.items():
            field.label = ""
            verbose_name = self.Meta.model._meta.get_field(field_name).verbose_name
            field.widget.attrs['placeholder'] = verbose_name
            field.widget.attrs.update(
                {'class': 'form-control'})
            field.required = True
            if 'name' in self.fields:
                self.fields['name'].validators.append(text_regex)
            if 'email' in self.fields:
                self.fields['email'].validators.append(email_regex)
        
        self.fields['message'].required = False
    class Meta:
        model = Comments
        fields = ['status','name', 'email', 'message']

    def clean_message(self):
        message = self.cleaned_data["message"]
        if not message:
            raise forms.ValidationError(_("The message container cannot be empty."))
        return message

class ResponseContactForm(forms.ModelForm):
    class Meta:
        model = ContactResponse
        fields = ['message']

class ResponseContactFormDisabled(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['message'].disabled = True

    class Meta:
        model = ContactResponse
        fields = ['message']

class JobApplicationForm(forms.ModelForm):
    class Meta:
        model = JobApplication
        fields = '__all__'
        
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': FIRST_NAME_PLACEHOLDER,
                'title': 'Please enter your first name.',
                }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': LAST_NAME_PLACEHOLDER,
                'title': 'Please enter your first name.',   
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email Address',
                'title': 'Please enter a valid email address.',
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': PHONE_PLACEHOLDER,
                'title': 'Please enter your phone number.',
                'pattern': '^\+?[0-9]{1,4}?([- ]?[0-9]{1,3}){1,4}$'
            }),
            'address': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': ADDRESS_PLACEHOLDER,
                'title': 'Please enter your address.',
            }),
            'position_applied': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': POSITION_APPLIED_PLACEHOLDER,
                'title': 'Please enter the position you are applying for.',
            }),
            'salary_expectations': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': SALARY_EXPECTATIONS_PLACEHOLDER,
                'title': 'Please enter your salary expectations.',

            }),
            'availability': forms.Select(attrs={
                'class': 'form-control',
                'title': 'Please select your availability.'
            }),
            'comments': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': COMMENTS_PLACEHOLDER,
                'title': 'You can leave additional comments here.'
            }),
            'cv': forms.FileInput(attrs={
                'class': 'form-control',
                'title': 'Please upload your curriculum vitae (CV).'
            }),
        }

        help_texts = {
            'cv': _('Allowed formats: PDF, DOC, DOCX. Maximum size: 5 MB.'),
        }

    def __init__(self, *args, **kwargs):
        super(JobApplicationForm, self).__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            if field_name != 'cv': 
                field.label = False
    
    def clean_email(self):
        email = self.cleaned_data['email']
        if JobApplication.objects.filter(email=email).exists():
            raise forms.ValidationError(_("Email address is already in use."))
        return email

    def clean_cv(self):
        cv = self.cleaned_data.get('cv')
        if cv:
            max_size = 5 * 1024 * 1024  # 5 MB en bytes
            if cv.size > max_size:
                raise forms.ValidationError(_("The CV file is too large. Size must not exceed 5 MB."))
            if not cv.name.lower().endswith(('.pdf', '.doc', '.docx')):
                raise forms.ValidationError(_("The CV file is not in a permitted format. Please upload a PDF, DOC, or DOCX file."))
        return cv
    
    def clean_phone_number(self):
        phone_raw = self.cleaned_data.get('phone_number')
        master = UserBase.objects.get(is_superuser=True)
        company = Company.objects.get(owner=master)
        country_code = company.country_legal.code2 
        
        try:
            phone_number = phonenumbers.parse(phone_raw, country_code)
            if not phonenumbers.is_valid_number(phone_number):
                raise ValueError()
            return phonenumbers.format_number(phone_number, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
        except (phonenumbers.phonenumberutil.NumberParseException, ValueError):
            raise ValidationError(_(f'{phone_raw} is not a valid number'))

#Support
class SupportForm(forms.ModelForm):
    class Meta:
        model = Support
        fields = ['option','message','terms','image']

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.fields['image'].widget.attrs.update(
                    {'class': 'form-control'})

class MasterSupportForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        for field_name, field in self.fields.items():
            field.label = ""
            verbose_name = self.Meta.model._meta.get_field(field_name).verbose_name
            field.widget.attrs['placeholder'] = verbose_name
            field.widget.attrs.update(
                {'class': 'form-control'})
            field.required = True
    class Meta:
        model = Support
        fields = ['status']
        # help_texts = {
        #     'terms': 'Al marcar esta casilla, acepto los términos y condiciones.',
        # }
        # widgets = {
        #     'terms': forms.CheckboxInput(attrs={
        #         'class': 'form-check-input',
        #         'required': 'required'  
        #     }),
        # }

class ChatSupportForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        for field_name, field in self.fields.items():
            field.label = ""
            verbose_name = self.Meta.model._meta.get_field(field_name).verbose_name
            field.widget.attrs['placeholder'] = verbose_name
            field.widget.attrs.update(
                {'class': 'form-control'})
            field.required = True
            
        self.fields['content'].required = False

    class Meta:
        model = ChatSupport
        fields = ['content']

    def clean_content(self):
        content = self.cleaned_data.get("content")
        if content:
            clean_content = caption_optimizer(content)
    
            if not re.match(content_regex, clean_content):
                raise forms.ValidationError(_("The content contains unauthorized characters."))
        else:
            pass

        return clean_content

class ReadOnlySupportForm(forms.ModelForm):
    class Meta:
        model = Support
        fields = ['option','message','terms', 'status']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["option"].disabled = True
        self.fields["message"].disabled = True
        self.fields["terms"].disabled = True

class ReadOnlySupportFormCostumer(forms.ModelForm):
    class Meta:
        model = Support
        fields = ['option','message','terms']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["option"].disabled = True
        self.fields["message"].disabled = True
        self.fields["terms"].disabled = True

#Billing 
class BillingForm(forms.ModelForm):
    class Meta: 
        model = BillingRecipt
        fields = ['report', 'option']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["report"].required = False

class BillingFormSuscription(forms.ModelForm):
    class Meta: 
        model = BillingRecipt
        fields = ['report']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["report"].required = False

class BillingChargeFormPOS(forms.ModelForm):
    class Meta:
        model = ItemProducts
        fields = ['field','qty']
      
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        self.fields['field'].widget.attrs.update(
            {'class': 'form-control col-lg-8 mx-3 mb-4', 'placeholder': 'Field'})
        self.fields['qty'].widget.attrs.update(
            {'class': 'form-control col-lg-2 mx-3 mb-4', 'placeholder': 'qty'})
        self.fields['field'].label = False
        self.fields['qty'].label = False
        self.fields['field'].queryset = Variant.objects.filter(product__lang=self.request.LANGUAGE_CODE)

class BillingChargeFormDynamic(forms.ModelForm):
    class Meta:
        model = ItemServices
        fields = ['field','qty']
      
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        self.fields['field'].widget.attrs.update(
            {'class': 'form-control col-lg-8 mx-3 mb-4', 'placeholder': 'Field'})
        self.fields['qty'].widget.attrs.update(
            {'class': 'form-control col-lg-2 mx-3 mb-4', 'placeholder': 'qty'})
        self.fields['field'].label = False
        self.fields['qty'].label = False
        self.fields['field'].required = True
        self.fields['qty'].required = True
        self.fields['field'].queryset = Elements.objects.filter(parent__owner=self.request.user, parent__yearly=False, parent__type="Service", parent__lang=self.request.LANGUAGE_CODE).order_by('parent').exclude(price=0)   

class BillingDiscountForm(forms.ModelForm):
    class Meta: 
        model = ItemDiscount
        fields = ['field','amount']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['field'].widget.attrs.update(
            {'class': 'form-control col-lg-8 mx-3 mb-4', 'placeholder': 'Field'})
        self.fields['amount'].widget.attrs.update(
            {'class': 'form-control col-lg-2 mx-3 mb-4', 'placeholder': 'amount'})
        self.fields['field'].label = False
        self.fields['amount'].label = False
        self.fields['field'].required = True
        self.fields['amount'].required = True

#invoiceCustom
class RequiredFormSet(BaseFormSet):
    def __init__(self, *args, **kwargs):
       super(RequiredFormSet, self).__init__(*args, **kwargs)
       for form in self.forms:
         form.empty_permitted = False

#developerLoad
class categForm(forms.ModelForm):

    class Meta: 
        model = Category
        exclude = ('slug', 'owner',)
        fields = '__all__'

class TempSecForm(forms.ModelForm):

    class Meta: 
        model = TemplateSections
        fields = ['section']

class StylesForm(forms.ModelForm):

    class Meta: 
        model = Content
        fields = ['parent', 'title', 'media']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['image'].widget.attrs.update(
                {'class': 'form-control'})
        
class ColorsForm(forms.ModelForm):

    class Meta: 
        model = StelaColors
        exclude = ('owner',)
        fields = '__all__'

#inventory Product
class ProductForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["image"].required = True
        self.fields['image'].widget.attrs.update(
                    {'class': 'form-control'})
    class Meta:
        model = Inventory
        exclude = ('slug','owner','type','price','qty', 'sku', 'lang', 'id')
        fields = '__all__'

class WorksForm(forms.ModelForm):
    class Meta:
        model = Inventory
        fields = ['status', 'title', 'description', 'image', 'price', 'url', 'published_date']
        widgets = {
            'status': forms.Select(attrs={
                'placeholder': 'Choose status...',
                'class': 'form-control',  
            }),
            'title': forms.TextInput(attrs={
                'placeholder': 'Title',
                'class': 'form-control',
            }),
            'description': forms.Textarea(attrs={
                'placeholder': 'Description',
                'class': 'form-control',
                'rows': 5,
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
            }),
            'url': forms.URLInput(attrs={
                'placeholder': 'http://example.com',
                'class': 'form-control',
            }),
            'published_date': DateInput(attrs={
                'placeholder': _('Select a date'),
            }),
        }
        labels = {
            'status': '',
            'title': '',
            'description': '',
            'url': '',
        }

    def __init__(self, *args, **kwargs):
        super(WorksForm, self).__init__(*args, **kwargs)
        self.fields['price'].label = 'Price USD'  
        self.fields['price'].widget.attrs.update({
            'placeholder': 'Enter amount',
        })
        self.fields['image'].label = 'Image'
        self.fields['price'].validators = [price_regex]
        self.fields['title'].validators = [text_regex]
        self.fields['image'].widget.attrs.update(
                {'class': 'form-control'})

    def clean_image(self):
        image = self.cleaned_data["image"]

        if not image:
            raise forms.ValidationError(_("The image container cannot be empty."))

        image_format = imghdr.what(image)
        if image_format not in ['jpeg', 'png']:
            raise forms.ValidationError(_("The image format is not valid. Only JPEG and PNG files are allowed."))

        return image

    def clean_description(self):
        content = self.cleaned_data.get("description")
        clean_content=caption_optimizer(content)

        if not content:
            raise forms.ValidationError(_("The content is required."))

        if not re.match(content_regex, clean_content):
            raise forms.ValidationError(_("The content contains unauthorized characters."))

        return content
    
class WorksReviewsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
        for field in self.fields.values():
                field.widget.attrs['placeholder'] = field.label
                field.label = False
                field.required = True
                field.widget.attrs['class'] = 'form-control'  

    class Meta:
        model = Content
        fields = ['status','title','subtitle','media','content']

    def clean_content(self):
        content = self.cleaned_data.get("content")
        clean_content=caption_optimizer(content)

        if not content:
            raise forms.ValidationError(_("The content is required."))

        if not re.match(content_regex, clean_content):
            raise forms.ValidationError(_("The content contains unauthorized characters."))

        return content
                     
class WorksReviewsCommentsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
        for field in self.fields.values():
                field.widget.attrs['placeholder'] = field.label
                field.label = False
                field.widget.attrs['class'] = 'form-control'  
    class Meta:
        model = CommentsWorks
        fields = ['full_name','cover','content']

    def clean_content(self):
        content = self.cleaned_data.get("content")
        clean_content=caption_optimizer(content)

        if not content:
            raise forms.ValidationError(_("The content is required."))

        if not re.match(content_regex, clean_content):
            raise forms.ValidationError(_("The content contains unauthorized characters."))

        return content
    
class ElementsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['image'].widget.attrs.update(
                {'class': 'form-control'})
    class Meta:
        model = Elements
        exclude = ('parent',)
        fields = '__all__'

class CatalogForm(forms.ModelForm):
    class Meta:
        model = Elements
        fields = ['image']
        labels = {
            'image': _('Catalog Image'),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            self.fields['image'].widget.attrs.update(
                {'class': 'form-control'})

class VariantForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["product"].queryset = Inventory.objects.filter(type="Product").order_by('title')
        self.fields['image'].widget.attrs.update(
                {'class': 'form-control'})
    class Meta:
        model = Variant
        fields = '__all__'
        exclude = ('id',)
    
class SizeForm(forms.ModelForm):

    class Meta:
        model = Sizes
        exclude = ('product','id')
        fields = '__all__'

class GalleryForm(forms.ModelForm):

    class Meta:
        model = Gallery
        exclude = ('catalogue', 'id')
        fields = '__all__'

class BulletForm(forms.ModelForm):

    class Meta:
        model = Bulletpoints
        exclude = ('product', 'id')
        fields = '__all__'

class VariantImageForm(forms.ModelForm):

    class Meta:
        model = VariantsImage
        fields = '__all__'
        exclude = ('id',)

class TemplateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['image'].widget.attrs.update(
                        {'class': 'form-control'})
    class Meta:
        model = Templates
        exclude = ('slug', 'id',)
        fields = '__all__'
    
#ContentStela (AboutSection, SliderSection, BoxSection, PortfolioSection, MediaSection, MisionSection, LegalSection, FooterSections, LinkSections)
class StelaAboutForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['media'].widget.attrs.update(
                {'class': 'form-control'})
    class Meta:
        model = Content
        fields = ['title', 'content', 'media', 'status']

class AppstelaForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['media'].widget.attrs.update(
                {'class': 'form-control'})
    class Meta:
        model = Content
        fields = ['appstela','subtitle','content','media','url', 'status'] 

class PathForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = Content
        fields = ['path', 'content', 'status']

class MediaForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['media'].widget.attrs.update(
                {'class': 'form-control'})
    class Meta:
        model = Content
        fields = ['media', 'url', 'status']

class FooterContentForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['content'].label = False

    class Meta:
        model = Content
        fields = ['content', 'status', 'status']

class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = '__all__'

#SiteContent
class TitleContentForm(forms.ModelForm):
    class Meta:
        model = Content
        fields = ['status','title','subtitle',]
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
        for field in self.fields.values():
            field.widget.attrs['placeholder'] = field.label
            field.label = False
           
    def clean_title(self):
        title = self.cleaned_data["title"]

        if not title:
            raise forms.ValidationError(_("The title is required."))
        
        if not re.match(r'^[a-zA-Z0-9\s!.,?;:"\'áéíóúÁÉÍÓÚñÑüÜ]+$', title):
            raise forms.ValidationError(_("The title contains unauthorized characters."))

        return title

    def clean_subtitle(self):
        subtitle = self.cleaned_data["subtitle"]

        if not subtitle:
            raise forms.ValidationError(_("The subtitle is required."))

        if not re.match(r'^[a-zA-Z0-9\s!.,?;:"\'áéíóúÁÉÍÓÚñÑüÜ]+$', subtitle):
            raise forms.ValidationError(_("The subtitle contains unauthorized characters."))

        return subtitle

    def clean_content(self):
        content = self.cleaned_data.get("content")
        clean_content=caption_optimizer(content)

        if not content:
            raise forms.ValidationError(_("The content is required."))

        if not re.match(content_regex, clean_content):
            raise forms.ValidationError(_("The content contains unauthorized characters."))

        return content

class SimpleContentForm(forms.ModelForm):

    class Meta:
        model = Content
        fields = ['status','title','subtitle','media',]
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
        for field in self.fields.values():
            field.widget.attrs['placeholder'] = field.label
            field.label = False
            self.fields['media'].widget.attrs.update(
                {'class': 'form-control'})
            
    def clean_title(self):
        title = self.cleaned_data["title"]

        if not title:
            raise forms.ValidationError(_("The title is required."))
        
        if not re.match(r'^[a-zA-Z0-9\s!.,?;:"\'áéíóúÁÉÍÓÚñÑüÜ]+$', title):
            raise forms.ValidationError(_("The title contains unauthorized characters."))

        return title

    def clean_subtitle(self):
        subtitle = self.cleaned_data["subtitle"]

        if not subtitle:
            raise forms.ValidationError(_("The subtitle is required."))

        if not re.match(r'^[a-zA-Z0-9\s!.,?;:"\'áéíóúÁÉÍÓÚñÑüÜ]+$', subtitle):
            raise forms.ValidationError(_("The subtitle contains unauthorized characters."))

        return subtitle

    def clean_media(self):
        image = self.cleaned_data["media"]

        if not image:
            raise forms.ValidationError(_("The image container cannot be empty."))

        image_format = imghdr.what(image)
        if image_format not in ['jpeg', 'png']:
            raise forms.ValidationError(_("The image format is not valid. Only JPEG and PNG files are allowed."))

        return image
    
class ContentForm(forms.ModelForm):

    class Meta:
        model = Content
        fields = ['status','title','subtitle','media', 'content',]
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
        for field in self.fields.values():
            field.widget.attrs['placeholder'] = field.label
            field.label = False
            self.fields['media'].widget.attrs.update(
                {'class': 'form-control'})
            
    def clean_title(self):
        title = self.cleaned_data["title"]

        if not title:
            raise forms.ValidationError(_("The title is required."))
        
        if not re.match(r'^[a-zA-Z0-9\s!.,?;:"\'áéíóúÁÉÍÓÚñÑüÜ]+$', title):
            raise forms.ValidationError(_("The title contains unauthorized characters."))

        return title

    def clean_subtitle(self):
        subtitle = self.cleaned_data["subtitle"]
        if not subtitle:
            pass
        else:
            if not re.match(r'^[a-zA-Z0-9\s!.,?;:"\'áéíóúÁÉÍÓÚñÑüÜ]+$', subtitle):
                raise forms.ValidationError(_("The subtitle contains unauthorized characters."))

        return subtitle
    
    def clean_media(self):
        image = self.cleaned_data["media"]

        if not image:
            raise forms.ValidationError(_("The image container cannot be empty."))

        image_format = imghdr.what(image)
        if image_format not in ['jpeg', 'png']:
            raise forms.ValidationError(_("The image format is not valid. Only JPEG and PNG files are allowed."))

        return image
 
class ValuesForm(forms.ModelForm):

    class Meta:
        model = Content
        fields = ['status','title','media','content',]
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
        for field in self.fields.values():
            field.widget.attrs['placeholder'] = field.label
            field.label = False
            self.fields['media'].widget.attrs.update(
                {'class': 'form-control'})
            
    def clean_title(self):
        title = self.cleaned_data["title"]

        if not title:
            raise forms.ValidationError(_("The title is required."))
        
        if not re.match(r'^[a-zA-Z0-9\s!.,?;:"\'áéíóúÁÉÍÓÚñÑüÜ]+$', title):
            raise forms.ValidationError(_("The title contains unauthorized characters."))

        return title
    
    def clean_content(self):
        content = self.cleaned_data.get("content")
        clean_content=caption_optimizer(content)

        if not content:
            raise forms.ValidationError(_("The content is required."))

        if not re.match(content_regex, clean_content):
            raise forms.ValidationError(_("The content contains unauthorized characters."))

        return content
    
    def clean_media(self):
        image = self.cleaned_data["media"]

        if not image:
            raise forms.ValidationError(_("The image container cannot be empty."))

        image_format = imghdr.what(image)
        if image_format not in ['jpeg', 'png']:
            raise forms.ValidationError(_("The image format is not valid. Only JPEG and PNG files are allowed."))

        return image

class AboutContentForm(forms.ModelForm):

    class Meta:
        model = Content
        fields = ['status','about','title','media', 'content',]
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
        for field in self.fields.values():
            field.widget.attrs['placeholder'] = field.label
            field.label = False
            self.fields['media'].widget.attrs.update(
                {'class': 'form-control'})
            
    def clean_title(self):
        title = self.cleaned_data["title"]

        if not title:
            raise forms.ValidationError(_("The title is required."))
        
        if not re.match(r'^[a-zA-Z0-9\s!.,?;:"\'áéíóúÁÉÍÓÚñÑüÜ]+$', title):
            raise forms.ValidationError(_("The title contains unauthorized characters."))

        return title

    def clean_content(self):
        content = self.cleaned_data.get("content")
        clean_content=caption_optimizer(content)

        if not content:
            raise forms.ValidationError(_("The content is required."))

        if not re.match(content_regex, clean_content):
            raise forms.ValidationError(_("The content contains unauthorized characters."))

        return content
    
    def clean_media(self):
        image = self.cleaned_data["media"]

        if not image:
            raise forms.ValidationError(_("The image container cannot be empty."))

        image_format = imghdr.what(image)
        if image_format not in ['jpeg', 'png']:
            raise forms.ValidationError(_("The image format is not valid. Only JPEG and PNG files are allowed."))

        return image

class ContentDynamicForm(forms.ModelForm):

    class Meta:
        model = Content
        fields = ['status','media','title','subtitle','content','url',]
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
        for field in self.fields.values():
            field.widget.attrs['placeholder'] = field.label
            field.label = False
            self.fields['media'].widget.attrs.update(
                {'class': 'form-control'})
            
    def clean_title(self):
        title = self.cleaned_data["title"]
        if not re.match(r'^[a-zA-Z0-9\s!.,?;:"\'áéíóúÁÉÍÓÚñÑüÜ]+$', title):
            raise forms.ValidationError(_("The title contains unauthorized characters."))

        if not title:
            raise forms.ValidationError(_("The title is required."))

        return title

    def clean_subtitle(self):
        subtitle = self.cleaned_data["subtitle"]

        if not subtitle:
            raise forms.ValidationError(_("The subtitle is required."))

        if not re.match(r'^[a-zA-Z0-9\s!.,?;:"\'áéíóúÁÉÍÓÚñÑüÜ]+$', subtitle):
            raise forms.ValidationError(_("The subtitle contains unauthorized characters."))

        return subtitle

    def clean_content(self):
        content = self.cleaned_data.get("content")
        clean_content=caption_optimizer(content)

        if not content:
            raise forms.ValidationError(_("The content is required."))

        if not re.match(content_regex, clean_content):
            raise forms.ValidationError(_("The content contains unauthorized characters."))

        return content
    
    def clean_media(self):
        image = self.cleaned_data["media"]

        if not image:
            raise forms.ValidationError(_("The image container cannot be empty."))

        image_format = imghdr.what(image)
        if image_format not in ['jpeg', 'png']:
            raise forms.ValidationError(_("The image format is not valid. Only JPEG and PNG files are allowed."))

        return image

    def clean_url(self):
        url = self.cleaned_data["url"]

        if not url:
            raise forms.ValidationError(_("The URL is required."))
        
        validate = URLValidator()
        try:
            validate(url)
        except ValidationError:
            raise forms.ValidationError("La URL no es válida.")
        return url

class RedirectContentForm(forms.ModelForm):

    class Meta:
        model = Content
        fields = ['status','media','title','subtitle','url',]
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
        for field in self.fields.values():
            field.widget.attrs['placeholder'] = field.label
            field.label = False
            self.fields['media'].widget.attrs.update(
                {'class': 'form-control'})
            
    def clean_title(self):
        title = self.cleaned_data["title"]

        if not title:
            raise forms.ValidationError(_("The title is required."))
        
        if not re.match(r'^[a-zA-Z0-9\s!.,?;:"\'áéíóúÁÉÍÓÚñÑüÜ]+$', title):
            raise forms.ValidationError(_("The title contains unauthorized characters."))

        return title

    def clean_subtitle(self):
        subtitle = self.cleaned_data["subtitle"]

        if not subtitle:
            raise forms.ValidationError(_("The subtitle is required."))

        if not re.match(r'^[a-zA-Z0-9\s!.,?;:"\'áéíóúÁÉÍÓÚñÑüÜ]+$', subtitle):
            raise forms.ValidationError(_("The subtitle contains unauthorized characters."))

        return subtitle

    def clean_content(self):
        content = self.cleaned_data.get("content")
        clean_content=caption_optimizer(content)

        if not content:
            raise forms.ValidationError(_("The content is required."))

        if not re.match(content_regex, clean_content):
            raise forms.ValidationError(_("The content contains unauthorized characters."))

        return content
    
    def clean_media(self):
        image = self.cleaned_data["media"]

        if not image:
            raise forms.ValidationError(_("The image container cannot be empty."))

        image_format = imghdr.what(image)
        if image_format not in ['jpeg', 'png']:
            raise forms.ValidationError(_("The image format is not valid. Only JPEG and PNG files are allowed."))

        return image

    def clean_url(self):
        url = self.cleaned_data["url"]

        if not url:
            raise forms.ValidationError(_("The URL is required."))
        
        validate = URLValidator()
        try:
            validate(url)
        except ValidationError:
            raise forms.ValidationError("La URL no es válida.")
        return url

class StickerContentForm(forms.ModelForm):

    class Meta:
        model = Content
        fields = ['status','media','url']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
        for field in self.fields.values():
            field.widget.attrs['placeholder'] = field.label
            field.label = False
            self.fields['media'].widget.attrs.update(
                {'class': 'form-control'})
        
    def clean_media(self):
        image = self.cleaned_data["media"]

        if not image:
            raise forms.ValidationError(_("The image container cannot be empty."))

        image_format = imghdr.what(image)
        if image_format not in ['jpeg', 'png']:
            raise forms.ValidationError(_("The image format is not valid. Only JPEG and PNG files are allowed."))

        return image

    def clean_url(self):
        url = self.cleaned_data["url"]

        if not url:
            raise forms.ValidationError(_("The URL is required."))
        
        validate = URLValidator()
        try:
            validate(url)
        except ValidationError:
            raise forms.ValidationError("La URL no es válida.")
        return url
            
class GalleryForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['image'].widget.attrs.update(
                {'class': 'form-control'})
    class Meta:
        model = ImageGallery
        fields = ['image'] 

class BulletSimpleForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs['placeholder'] = field.label
            field.label = False

    class Meta:
        model = DynamicBullets
        fields = ['bullet_title','content_bullet'] 

class ImageContentForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['media'].widget.attrs.update(
                {'class': 'form-control'})

    class Meta:
        model = Content
        fields = ['status','media'] 

class PolicyForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs['placeholder'] = field.label
            field.label = False

    class Meta:
        model = SitePolicy
        fields = ['title','section','status']

class LegalProvitionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs['placeholder'] = field.label
            field.label = False

    class Meta:
        model = LegalProvision
        fields = ['clause', 'clause_content']

class FAQForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
        for field in self.fields.values():
            field.widget.attrs['placeholder'] = field.label
            field.label = False
            self.fields['status'].widget.attrs.update(
                {'class': 'custom-select custom-select-sm'})
            self.fields['legal'].widget.attrs.update(
                {'class': 'custom-select custom-select-sm'})
            
    class Meta:
        model = FAQ
        fields = '__all__'
        exclude = ('author','lang',)
    
    def clean_title(self):
        title = self.cleaned_data.get('title')
        
        if not re.match(r'^[a-zA-Z0-9\s!.,?;:"\'áéíóúÁÉÍÓÚñÑüÜ]+$', title):
            raise forms.ValidationError(_("The title contains unauthorized characters."))

        if not title:
            raise forms.ValidationError(_("The title is required."))

        return title

class SetFaqForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
        for field in self.fields.values():
            field.widget.attrs['placeholder'] = field.label
            field.label = False

    class Meta:
        model = SetFaq
        fields = '__all__'
        exclude = ('faq',)
    
    def clean_question(self):
        question = self.cleaned_data["question"]

        if not question:
            raise forms.ValidationError(_("The question is required."))

        if not re.match(r'^[a-zA-Z0-9\s!.,?;:"\'áéíóúÁÉÍÓÚñÑüÜ]+$', question):
            raise forms.ValidationError(_("The question contains unauthorized characters."))

        return question

    def clean_answer(self):
        answer = self.cleaned_data["answer"]
        clean_content=caption_optimizer(answer)

        if not answer:
            raise forms.ValidationError(_("The answer is required."))
        
        if not re.match(content_regex, clean_content):
            raise forms.ValidationError(_("The answer contains unauthorized characters."))

        return answer
    
class BlogForm(forms.ModelForm):

    class Meta:
        model = Content
        fields = ['status','category','title','subtitle','content','media']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
        for field in self.fields.values():
            field.widget.attrs['placeholder'] = field.label
            field.label = False
            field.widget.attrs['class'] = 'form-control'
            
    def clean_title(self):
        title = self.cleaned_data["title"]

        if not title:
            raise forms.ValidationError(_("The title is required."))
        
        if not re.match(r'^[a-zA-Z0-9\s!.,?;:"\'áéíóúÁÉÍÓÚñÑüÜ]+$', title):
            raise forms.ValidationError(_("The title contains unauthorized characters."))

        return title

    def clean_subtitle(self):
        subtitle = self.cleaned_data["subtitle"]

        if not subtitle:
            raise forms.ValidationError(_("The subtitle is required."))

        if not re.match(r'^[a-zA-Z0-9\s!.,?;:"\'áéíóúÁÉÍÓÚñÑüÜ]+$', subtitle):
            raise forms.ValidationError(_("The subtitle contains unauthorized characters."))

        return subtitle

    def clean_content(self):
        content = self.cleaned_data.get("content")
        clean_content=caption_optimizer(content)

        if not content:
            raise forms.ValidationError(_("The content is required."))

        if not re.match(content_regex, clean_content):
            raise forms.ValidationError(_("The content contains unauthorized characters."))

        return content
    
    def clean_media(self):
        media = self.cleaned_data["media"]

        if not media:
            raise forms.ValidationError(_("The media container cannot be empty."))

        image_format = imghdr.what(media)

        if image_format in ['jpeg', 'png']:
            return media
        
        extension = os.path.splitext(media.name.lower())[1]
        if extension in ['.webp', '.mp4', '.jpg']:
            return media
        else:
            raise forms.ValidationError(_("The file format is not valid. Only PNG, JPEG, WEBP, and MP4 files are allowed."))

    def clean_folder_doc(self):
        doc = self.cleaned_data["folder_doc"]
        if not doc:
            pass
        else:
            if not doc.name.endswith('.pdf'):
                raise forms.ValidationError("El archivo debe ser en formato PDF.")

        return doc

    def clean_url(self):
        url = self.cleaned_data["url"]

        if not url:
            raise forms.ValidationError(_("The URL is required."))
        
        validate = URLValidator()
        try:
            validate(url)
        except ValidationError:
            raise forms.ValidationError("La URL no es válida.")
        return url
    
class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['name', 'address', 'email', 'service', 'type']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': _('name'), 'label': ''}),
            'address': forms.TextInput(attrs={'placeholder': _('billing_address'), 'label': ''}),
            'email': forms.EmailInput(attrs={'placeholder': _('email'), 'label': ''}),
            'service': forms.TextInput(attrs={'placeholder': _('service'), 'label': ''}),
            'type': forms.TextInput(attrs={'placeholder': _('type'), 'label': ''}),
        }
    
    name = forms.CharField(validators=[text_regex])
    address = forms.CharField(validators=[text_regex])
    email = forms.EmailField(validators=[email_regex])
    service = forms.CharField(validators=[text_regex])
    type = forms.CharField(validators=[text_regex])
    
    def __init__(self, *args, **kwargs):
        super(BookingForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'  
            field.label = ''

class ConsultingForm(forms.ModelForm):
    class Meta:
        model = Inventory
        fields = ['title', 'description', 'price']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': _('title')}),
            'description': forms.Textarea(attrs={'placeholder': _('description')}),
            'price': forms.NumberInput(attrs={'placeholder': _('price')}),
        }
    
    title = forms.CharField(max_length=255, validators=[text_regex])
    description = forms.CharField(widget=forms.Textarea, validators=[text_regex])
    price = forms.DecimalField(decimal_places=2, validators=[price_regex])
    
    def __init__(self, *args, **kwargs):
        super(ConsultingForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control' 
            field.label = ''

#Email_Marketing
class NewsletterForm(forms.ModelForm):
    
    class Meta: 
        model = DataEmail
        fields = ['email']

    def clean_email(self):
        email = self.cleaned_data['email']
        pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        if not email:
            raise ValidationError(_('Email is required.'))
        elif DataEmail.objects.filter(email=email).exists():
            raise ValidationError(_('This email is already subscribed.'))
        elif not pattern.match(email):
            raise ValidationError(_('The email address is not valid.'))
        return email
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.update(
            {'class': 'form-control required email bg-white border-0', 'placeholder': _('Place Email')})
        self.fields['email'].label=False

class WalletForm(forms.ModelForm):
    class Meta: 
        model = Wallet
        exclude = ('user',)
        fields = '__all__'

#Post Facebook
class DateInput(forms.DateInput):
    input_type = 'date'

class FbPostForm(forms.ModelForm):

    class Meta:
        model=FacebookPostPage
        exclude = ('page' 'feed_id',)
        fields = '__all__'
        widgets = {
            'schedule': DateInput()
        }
           
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['content'].label=False
        self.fields["content"].required = False
        self.fields['content'].widget.attrs.update(
            {'onchange': 'submitTrigger()'})
        self.fields["schedule"].required = False
        self.fields["schedule"].label = False
        self.fields['schedule'].widget.attrs.update({'min': date.today() + timedelta(days=1), 'max': (date.today() + timedelta(days=180)).strftime('%Y-%m-%d')})
        
class FacebookMediaForm(forms.ModelForm):

    class Meta:
        model = FacebookPostMedia
        exclude = ('post',)
        fields = '__all__'

class FacebookEventsForm(forms.ModelForm):

    class Meta:
        model = FacebookPageEvent
        exclude = ('owner',)
        fields = '__all__'
        widgets = {
            'start_time': DateInput(),
            'end_time': DateInput(),

        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['status'].label = False
        self.fields['type'].label = False
        self.fields['category'].label = False
        self.fields['name'].label = False
        self.fields['start_time'].label = False
        self.fields['description'].label = False
        self.fields['description'].required = False
        self.fields['cover'].label = False
        self.fields['cover'].widget.attrs.update(
            {'class': 'form-control'})
        self.fields['description'].widget.attrs.update(
            {'class': 'vh-20'})
        self.fields['start_time'].widget.attrs.update({'min': date.today() + timedelta(days=1), 'max': (date.today() + timedelta(days=180)).strftime('%Y-%m-%d')})

class IGPostForm(forms.ModelForm):

    class Meta:
        model=IGPost
        exclude = ('parent',)
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['status'].label = False
        self.fields['mediatype'].label = False
        self.fields['caption'].label = False
        self.fields['schedule'].label = False
        self.fields['status'].widget.attrs.update(
            {'class': 'custom-select custom-select-sm'})
        self.fields['mediatype'].widget.attrs.update(
            {'class': 'custom-select custom-select-sm'})

class IGMediaForm(forms.ModelForm):

    class Meta:
        model=IGMediaContent
        exclude = ('post',)
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['cover'].widget.attrs.update(
                {'class': 'form-control', 'accept': '.jpg'})
        self.fields['media'].widget.attrs.update(
                {'class': 'form-control', 'accept': '.mp4'})

class SendGridForm(forms.Form):
    email = forms.EmailField(label=_('To Email'))
    subject = forms.CharField(label=_('Subject'))
    client = forms.CharField(label=_('Client or Brand'))
    message = forms.CharField(widget=forms.Textarea, label=_('Report'), required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['placeholder'] = field.label
            field.label = False
        
    def clean_email(self):
        email = self.cleaned_data.get('email')
        epattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        if not re.match(epattern, email):
            raise forms.ValidationError(_('Please enter a valid email.'))
        return email

    def clean_subject(self):
        subject = self.cleaned_data.get('subject')
        tpattern = r"^[a-zA-Z0-9\-/., ñÑáéíóúÁÉÍÓÚ]*$"
        if not re.match(tpattern, subject):
            raise forms.ValidationError(_('Special characters are not allowed.'))
        return subject

    def clean_client(self):
        client = self.cleaned_data.get('client')
        tpattern = r"^[a-zA-Z0-9\-/., ñÑáéíóúÁÉÍÓÚ]*$"
        if not re.match(tpattern, client):
            raise forms.ValidationError(_('Special characters are not allowed.'))
        return client

    def clean_message(self):
        message = self.cleaned_data.get('message')
        message_formatted = caption_optimizer(message)
        print(message_formatted)
        regex = r"^[a-zA-Z0-9\s.,#-ñÑáéíóúÁÉÍÓÚ]*$"
        match = re.match(regex, message_formatted, re.DOTALL)
        if not match:
            print('not validated')
            raise forms.ValidationError(_('Special characters are not allowed.'))
        return message

class ReviewsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        for field_name, field in self.fields.items():
            field.label = ""
            verbose_name = self.Meta.model._meta.get_field(field_name).verbose_name
            field.widget.attrs['placeholder'] = verbose_name
            field.widget.attrs.update(
                {'class': 'form-control'})
            field.required = True
        
        self.fields['content'].required = False

    class Meta:
        model = Reviews
        fields = ['content']

    def clean_content(self):
        content = self.cleaned_data.get("content")
        clean_content=caption_optimizer(content)

        if not content:
            raise forms.ValidationError(_("The message is required."))

        if not re.match(content_regex, clean_content):
            raise forms.ValidationError(_("The message contains unauthorized characters."))

        return content
    
#siteapp Forms
class LiteraryWorkForm(forms.ModelForm):
    class Meta:
        model = LiteraryWork
        fields = ('title', 'author', 'publication_date', 'genre', 'synopsis')
    
    def clean_title(self):
        title = self.cleaned_data['title']
        if len(title) < 5:
            raise forms.ValidationError(_("El title must be at least 5 characters."))
        return title

    def clean_publication_date(self):
        publication_date = self.cleaned_data['publication_date']
        if publication_date.year < 1800:
            raise forms.ValidationError(_("The pub date must be after 1800"))
        return publication_date

class ResourceForm(forms.ModelForm):
    class Meta:
        model = Resource
        fields = ['title', 'file']

class BillFileForm(forms.ModelForm):
    class Meta:
        model = BillFile
        fields = ['title', 'pdf', 'comments']

class BookingConsultingForm(forms.Form):
    name_validator = RegexValidator(r'^[\w\s]+$', _('El nombre solo puede contener letras, números y espacios.'))
    
    address_validator = RegexValidator(
        regex=r'^[A-Za-z0-9 .\-/#,ñáéíóúÑÁÉÍÓÚäëïöüÄËÏÖÜ]+$', 
        message=_("Introduzca una dirección de facturación válida."),
    )

    TYPE_CHOICES = [
        ('in_place', _('In Place')),
        ('streaming', _('Streaming')),
    ]

    name = forms.CharField(
        max_length=100,
        validators=[name_validator],
        required=True
    )

    type = forms.ChoiceField(
        choices=TYPE_CHOICES,
        required=True
    )

    email = forms.EmailField(
        max_length=254,  
        required=True
    )
    
    address = forms.CharField(
        max_length=300,
        validators=[address_validator],
        required=False  
    )

    schedule = forms.DateField(
        input_formats=['%Y-%m-%d'], 
        required=True
    )

    def clean_schedule(self):
        appointment_date = self.cleaned_data.get('schedule')
        if appointment_date and appointment_date < datetime.date.today():
            raise ValidationError(_("La fecha de la cita no puede estar en el pasado."), code='invalid_date')
        return appointment_date
