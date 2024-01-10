from django.contrib.auth.models import AbstractUser
from django.db import models
from datetime import datetime
from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from django import forms
# from django.contrib.postgres.fields import JSONField
from django.db.models import JSONField
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.files import File
import os
from django.db import models
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
from decimal import Decimal



class CustomUser(AbstractUser):
    # Add custom fields or override existing fields/methods
    bio = models.TextField(max_length=500)
    profile_image = models.ImageField(upload_to='profile_pictures/', blank=True, default='profile_pictures/profile_placeholder.png')
    phone_num= models.CharField(max_length=20)
    e_mail= models.EmailField(max_length=250, unique=True, default='')


    # Add any additional methods or behavior
    def get_full_name(self):
        # Custom implementation for getting the full name
        return f"{self.first_name} {self.last_name}"


class UserProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500)
    profile_image = models.ImageField(upload_to='profile_pictures', blank=True)
    phone_num= models.CharField(max_length=20)
    e_mail= models.EmailField(max_length=250, unique=True, default='')

    def __str__(self):
        return str(self.user)
    
    
from django.contrib.auth import get_user_model
User = get_user_model()

class Bid(models.Model):
    artwork = models.ForeignKey('Artwork', on_delete=models.CASCADE, related_name='bids')
    bidder = models.ForeignKey(User, on_delete=models.CASCADE)
    bid_amount = models.DecimalField(max_digits=8, decimal_places=2)
    bid_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.bid_amount}'
    

    def is_highest_bid(self):
        highest_bid = self.artwork.bids.order_by('-bid_amount').first()
        return self == highest_bid


class NFT_bid(models.Model):
    artwork = models.ForeignKey('Artwork', on_delete=models.CASCADE, related_name='bid')
    NFT = models.ForeignKey('NFT', on_delete=models.CASCADE, related_name='bids')
    bidder = models.ForeignKey(User, on_delete=models.CASCADE)
    bid_amount = models.DecimalField(max_digits=8, decimal_places=2)
    bid_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.bid_amount}'
    

    def is_highest_bid(self):
        highest_bid = self.NFT.bids.order_by('-bid_amount').first()
        return self == highest_bid


class GraphImage(models.Model):
    image=models.ImageField(upload_to='graph_image/')
    NFT=models.ForeignKey('NFT', on_delete=models.CASCADE, related_name='graph')
    user= models.ForeignKey(User, on_delete=models.CASCADE)


class ArtworkGraphImage(models.Model):
    image=models.ImageField(upload_to='artwork_graph_image/')
    Artwork=models.ForeignKey('Artwork', on_delete=models.CASCADE, related_name='graph')
    user= models.ForeignKey(User, on_delete=models.CASCADE)



class Prefs(models.Model):
    percent_growth=models.DecimalField(max_digits=50,decimal_places=2, default=0.00, blank=True, null=True)
    time_frame=models.CharField(max_length=100,blank=True,null=True)
    min_price=models.DecimalField(max_digits=50, decimal_places=2, default=0.00,null=True)
    max_price=models.DecimalField(max_digits=50, decimal_places=2, default=0.00,null=True)
    sold=models.BooleanField(default=False)
    for_sale=models.BooleanField(default=True)
    want_artwork=models.BooleanField(default=True)
    want_nfts=models.BooleanField(default=True)
    user=models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,related_name='user_prefs')



# add fields like +0.5% gorwth that auto updats/ other things like that for NFT too
class Artwork(models.Model):
    artist = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,related_name='artworks_created')
    main_image = models.ImageField(upload_to='artworks/')
    additional_images = models.ImageField(upload_to='artworks/', blank=True)
    # additional_images = ArrayField(models.ImageField(upload_to='artworks/'), blank=True)
    name = models.CharField(max_length=255)
    description = models.TextField()
    shares_count = models.IntegerField(default=0)
    share_price = models.DecimalField(max_digits=50, decimal_places=2, default=0.00)
    art_price = models.DecimalField(max_digits=50, decimal_places=2, default=0.00)
    is_draft = models.BooleanField(default=False)
    has_NFT = models.BooleanField(default=False)
    is_for_sale=models.BooleanField(default=False)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,related_name='artworks_owned')
    number_of_sales=models.IntegerField(default=0)
    keywords=models.CharField(max_length=90000000, blank=True,default='')
    percent_change = models.CharField(max_length=9000000,blank=True,default='')
    

    # interest tags
    art_styles = models.CharField(max_length=200, blank=True)
    generes=models.CharField(max_length=200, blank=True)
    historical_periods=models.CharField(max_length=200, blank=True)
    mediums=models.TextField(blank=True)
                              
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clear_bids(self):
        Bid.objects.filter(artwork=self).delete()

    def __str__(self):
        return self.name
    
    def update_percent_change(self):
        latest_price_entry = self.price_history.order_by('-date').first()
        if latest_price_entry is not None:
            current_price = Decimal(self.art_price)
            previous_price = latest_price_entry.previous_price
            print(f'current price: {current_price}')
            print(f'previous price: {previous_price}')


            percent_change = ((current_price - previous_price) / previous_price) * 100
            percent_change = round(percent_change, 2)

            # Update the percent_change field of the NFT object
            if current_price > previous_price:
                indicator = '+'
                self.percent_change = f'{indicator}{percent_change}%'
            elif current_price == previous_price:
                indicator = ''
                self.percent_change = f'{indicator}{percent_change}%'
            else:
                self.percent_change = f'{percent_change}%'
                
        self.save()


class ArtworkPriceHistory(models.Model):
    artwork = models.ForeignKey(Artwork, on_delete=models.CASCADE, related_name='price_history')
    price = models.DecimalField(max_digits=8, decimal_places=2)
    date = models.DateTimeField(default=timezone.now)
    previous_price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    
    def save(self, *args, **kwargs):
        self.date = timezone.now()
        self.nft=self.artwork
        self.price=self.price

        try:
            print('get the previous price')
            print(self.previous_price)
            self.previous_price = self.get_previous_day_price()
            super().save(*args, **kwargs)
            print('saved')
        except Exception as e:
            print('An error occurred during save:', e)
        else:
            print('super saved')

    #this part all good
    def get_previous_day_price(self):
        print('in get previous price')
        previous_day = self.date - timedelta(days=1)
        
        # get previous day's price:
        previous_price_entry = ArtworkPriceHistory.objects.filter(artwork=self.artwork, date__date=previous_day, date__lt=self.date).order_by('-date').first()
        print(f'prev price entry in get prev day price: {previous_price_entry}')
        
        if previous_price_entry==None or 0:
            # get first entry of nft's price
            opening_price=ArtworkPriceHistory.objects.filter(artwork=self.artwork).order_by('date').first()
            if opening_price:
                print(f'open price/first day: {opening_price}, opening_price.price: {opening_price.price} opening_price.date:{opening_price.date}')
                return opening_price.price
            else:
                if self.previous_price:
                    print(f'no opening price, check if it has one:{self.previous_price}')
                    return self.previous_price
                else:
                    print(f'no opening price or previous price so self.price: {self.price}')
                    return self.price
        
        else:
            print(f'prev price entry.price: { previous_price_entry.price} prev_price_entry.date:{previous_price_entry.date}')
            return previous_price_entry.price if previous_price_entry else 0




class NFT(models.Model):
    artwork = models.ForeignKey('Artwork', on_delete=models.CASCADE, related_name='NFT')
    main_image = models.ImageField(upload_to='nfts/')
    is_for_sale=models.BooleanField(default=False)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,related_name='NFTs_owned')
    nft_price=models.DecimalField(max_digits=50, decimal_places=2, default=0.00)
    NFT_count = models.IntegerField(default=0)
    dates = models.DateTimeField(auto_now_add=True)
    keywords=models.CharField(max_length=9000000,blank=True,default='')
    name=models.CharField(max_length=255)

    # previous_days_closing_price=models.DecimalField(max_digits=50, decimal_places=2, default=0.00)
    percent_change = models.CharField(max_length=9000000,blank=True,default='')


    updated_at = models.DateTimeField(auto_now=True)

    def num_owned(self):
        return NFT.objects.filter(artwork=self.artwork, is_for_sale=False).count()

    def clear_bids(self):
            NFT_bid.objects.filter(NFT=self).delete()
    
    def update_percent_change(self):
        latest_price_entry = self.price_history.order_by('-date').first()
        if latest_price_entry is not None:
            current_price = Decimal(self.nft_price)
            previous_price = latest_price_entry.previous_price
            print(f'current price: {current_price}')
            print(f'previous price: {previous_price}')


            percent_change = ((current_price - previous_price) / previous_price) * 100
            percent_change = round(percent_change, 2)

            # Update the percent_change field of the NFT object
            if current_price > previous_price:
                indicator = '+'
                self.percent_change = f'{indicator}{percent_change}%'
            elif current_price == previous_price:
                indicator = ''
                self.percent_change = f'{indicator}{percent_change}%'
            else:
                self.percent_change = f'{percent_change}%'
        
        # old way I got price hist:    
        # nfts_price_hist=PriceHistory.objects.filter(nft=self,date__lt=timezone.now().date()
        # ).order_by('-date').first()

        self.save()
        

class PriceHistory(models.Model):
    nft = models.ForeignKey(NFT, on_delete=models.CASCADE, related_name='price_history')
    price = models.DecimalField(max_digits=8, decimal_places=2)
    date = models.DateTimeField(default=timezone.now)
    previous_price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    
    def save(self, *args, **kwargs):
        self.date = timezone.now()
        self.nft=self.nft
        self.price=self.price

        try:
            print('get the previous price')
            print(self.previous_price)
            self.previous_price = self.get_previous_day_price()
            super().save(*args, **kwargs)
            print('saved')
        except Exception as e:
            print('An error occurred during save:', e)
        else:
            print('super saved')

    #this part all good
    def get_previous_day_price(self):
        print('in get previous price')
        previous_day = self.date - timedelta(days=1)
        
        # get previous day's price:
        previous_price_entry = PriceHistory.objects.filter(nft=self.nft, date__date=previous_day, date__lt=self.date).order_by('-date').first()
        print(f'prev price entry in get prev day price: {previous_price_entry}')
        
        if previous_price_entry==None or 0:
            # get first entry of nft's price
            opening_price=PriceHistory.objects.filter(nft=self.nft).order_by('date').first()
            if opening_price:
                print(f'open price/first day: {opening_price}, opening_price.price: {opening_price.price} opening_price.date:{opening_price.date}')
                return opening_price.price
            else:
                if self.previous_price:
                    print(f'no opening price, check if it has one:{self.previous_price}')
                    return self.previous_price
                else:
                    print(f'no opening price or previous price so self.price: {self.price}')
                    return self.price
        
        else:
            print(f'prev price entry.price: { previous_price_entry.price} prev_price_entry.date:{previous_price_entry.date}')
            return previous_price_entry.price if previous_price_entry else 0



class Watchlist(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    artwork = models.ManyToManyField(Artwork)
    nft=models.ManyToManyField(NFT)
    # Add any additional fields as needed


class Interests(models.Model):
    art_styles = models.CharField(max_length=200, blank=True)
    generes=models.CharField(max_length=200, blank=True)
    historical_periods=models.CharField(max_length=200, blank=True)
    mediums=models.TextField(blank=True)
    user=models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,related_name='interests')
    categories = JSONField(default=dict)
    watchlist = models.ForeignKey(Watchlist, on_delete=models.CASCADE, null=True, blank=True)
    # use these to repopulate ?
    # realisim=models.BooleanField(default=False)
