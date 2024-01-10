from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import CustomUser
from .models import UserProfile
from django import forms
from .models import Artwork
from decimal import Decimal
from .models import Bid,NFT_bid,Prefs

class ProfileForm(forms.ModelForm):
    profile_image_data = forms.CharField(required=False, widget=forms.HiddenInput())
    
    class Meta:
        model = UserProfile
        fields = ['bio', 'profile_image','phone_num','e_mail']


class RegistrationForm(UserCreationForm):
    profile_image = forms.ImageField(required=False)
    
    class Meta:
        model = CustomUser
        fields = ('username', 'password1', 'password2','bio','phone_num','e_mail')

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.fields['bio'].required = False

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if CustomUser.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError("This username is already taken.")
        return username

    def save(self, commit=True):
        user = super().save(commit=False)
        profile_image = self.cleaned_data.get('profile_image')
        if profile_image:
            user.profile.profile_image = profile_image  # Assuming a OneToOneField relationship between User and Profile
        if commit:
            user.save()
            user.profile.save()
        return user
    

class ArtworkForm(forms.ModelForm):
    art_price = forms.DecimalField(label='Art Price', disabled=True, required=False)

    class Meta:
        model = Artwork
        fields = ['main_image', 'additional_images', 'name', 'description', 'shares_count', 'share_price', 'art_price']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['main_image'].widget.attrs.update({'id': 'id_main_image'})
        self.fields['additional_images'].widget.attrs.update({'id': 'id_additional_images'})
        self.fields['name'].widget.attrs.update({'id': 'id_art_name'})
        self.fields['description'].widget.attrs.update({'id': 'id_art_description'})
        self.fields['shares_count'].widget.attrs.update({'id': 'id_shares_count', 'min': '1'})
        self.fields['share_price'].widget.attrs.update({'id': 'id_share_price', 'min': '0', 'step': '0.01'})

    def clean(self):
        cleaned_data = super().clean()
        action = self.data.get('action')

        shares_count = cleaned_data.get('shares_count')
        share_price = cleaned_data.get('share_price')

        if action == 'Save to Drafts':
            artist = self.initial.get('artist')
            cleaned_data['artist'] = artist

            name = cleaned_data.get('name')
            description = cleaned_data.get('description')
            shares_count = cleaned_data.get('shares_count')
            share_price = cleaned_data.get('share_price')


            # Clear errors for optional fields
            if name is None:
                self._errors.pop('name', None)
            if description is None:
                self._errors.pop('description', None)
            if shares_count is None:
                self._errors.pop('shares_count', None)
            if share_price is None:
                self._errors.pop('share_price', None)

            # Calculate art_price
        try:
            shares_count = int(shares_count)
            share_price = Decimal(share_price)
            art_price = shares_count * share_price
            cleaned_data['art_price'] = art_price
        except (ValueError, TypeError):

            art_price = Decimal(0)  # Set a default value if the calculation fails

            cleaned_data['art_price'] = art_price

        return cleaned_data


class BidForm(forms.ModelForm):
    class Meta:
        model = Bid
        exclude = ['artwork']
        fields = ['bid_amount']


class NFT_bidForm(forms.ModelForm):
    class Meta:
        model = NFT_bid
        exclude = ['NFT']
        fields = ['bid_amount']


class prefsForm(forms.ModelForm):
    class Meta:
        model=Prefs
        fields=['percent_growth','time_frame','min_price','max_price','sold','for_sale','want_artwork','want_nfts']

    def __init__(self, *args, **kwargs):
        super(prefsForm, self).__init__(*args, **kwargs)
        self.fields['percent_growth'].required = False
        self.fields['time_frame'].required = False
        self.fields['min_price'].required = False
        self.fields['max_price'].required = False
        self.fields['sold'].required = False
        self.fields['for_sale'].required = False
        self.fields['want_artwork'].required = False
        self.fields['want_nfts'].required = False


