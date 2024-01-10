from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from .forms import RegistrationForm
from .models import ArtworkPriceHistory
from datetime import datetime
from django.contrib import messages
from django.contrib.auth import authenticate, login
from .forms import RegistrationForm,prefsForm
from .models import UserProfile,Prefs
from .models import Artwork
from .forms import BidForm, ProfileForm
from django.db.models import Max
from .models import Bid, NFT,PriceHistory,Interests,CustomUser,Watchlist
from datetime import datetime, timedelta
from django.db.models import F, Value, Sum, FloatField, ExpressionWrapper
import ast
import random
import json
import string
from django.db.models import F
from django.db import models
import random, logging
from django.http import JsonResponse
from operator import itemgetter
from django.utils import timezone
from datetime import timedelta
import os
from twilio.rest import Client
from django.urls import reverse
import base64

from django.http import HttpResponse


import nltk
nltk.download('punkt')
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize




########tools############

def similarity_score(str1, str2):
    # Convert both strings to lowercase to make the comparison case-insensitive
    str1 = str1.lower()
    str2 = str2.lower()

    len1 = len(str1)
    len2 = len(str2)

    dp = [[0] * (len2 + 1) for _ in range(len1 + 1)]

    for i in range(1, len1 + 1):
        for j in range(1, len2 + 1):
            if str1[i - 1] == str2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])

    return dp[len1][len2]

def find_similar_usernames(search_req, users):
    threshold = 3  # Set your desired similarity threshold here

    similar_usernames = []
    username_ids=[]

    for user in users:
        if isinstance(user, UserProfile):
            username = user.user.username

            max_score = 0
            for req in search_req:
                score = similarity_score(req, username)
                max_score = max(max_score, score)

            if max_score >= threshold:
                similar_usernames.append(username)
                username_ids.append(user.id)
    

    zipped_user_results = list(zip(similar_usernames, username_ids))
    for i, (username, user_id) in enumerate(zipped_user_results):
        zipped_user_results[i] = (username, user_id, max_score)

    zipped_user_results.sort(key=lambda x: x[2], reverse=True)


    return zipped_user_results
 
def generate_verification_code(length=6):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

# add remove/append for repop data in rest of fields
def save_and_repop_interests(request):
    
    User=request.user

    try:
        interests=Interests.objects.filter(user=User).first()
        if interests is None:
            interests=Interests.objects.create(user=User)
    except Interests.DoesNotExist:
        interests=Interests.objects.create(user=User)

    repop_data = [category for category, count in interests.categories.items() if count > 0]
    # print(f'check repop data in tool:{repop_data}')

    saved=False


    if request.method == 'POST':

        # print(f'check post data:{request.POST}')
        User=request.user

        art_styles_mapping = {
            'realisim': 'realism',
            'abstract': 'abstract',
            'impressionism': 'impressionism',
            'cubisim': 'cubism',
            'surrealisim': 'surrealism',
            'pop_art': 'pop_art',
            'minimalism': 'minimalism',
            'contemporary': 'contemporary',
            'street_art': 'street_art',
            'digital_art': 'digital_art',
        }

        genres_mapping = {
            'landscape': 'landscape',
            'portrait': 'portrait',
            'still_life': 'still_life',
            'figurative': 'figurative',
            'wildlife': 'wildlife',
            'historical': 'historical',
            'conceptual': 'conceptual',
            'nature': 'nature',
            'fantasy_sci_fi': 'fantasy_sci_fi',
        }

        periods_mapping = {
            'renaissance': 'renaissance',
            'baroque': 'baroque',
            'romanticism': 'romanticism',
            'modernism': 'modernism',
            'post_impressionism': 'post_impressionism',
            'art_nouveau': 'art_nouveau',
            'expressionism': 'expressionism',
            'abstract_expressionism': 'abstract_expressionism',
            'contemporary_art_movements': 'contemporary_art_movements',
        }

        mediums_mapping = {
            'painting': 'painting',
            'drawing': 'drawing',
            'sculpture': 'sculpture',
            'photography': 'photography',
            'printmaking': 'printmaking',
            'mixed_media': 'mixed_media',
            'digital_art': 'digital_art',
            'collage': 'collage',
            'installation_art': 'installation_art',
        }

        # print(interests.categories)
        # print(interests.art_styles)

        art_styles_list = []  # Initialize as a list
        for field, style in art_styles_mapping.items():
            # print(f' checking fields in post: {request.POST.get(field)}')
            if request.POST.get(field) and style not in interests.art_styles:
                # print(f'field:{field} and style: {style} from post is not in interests.art_styles: {interests.art_styles}')
                art_styles_list.append(style)
                # print(f' style appended:{style}')
            elif not request.POST.get(field) and style in repop_data:
                # print(f' field form post: {request.POST.get(field)} and style: {style}, are not in repop_data: {repop_data}')
                interests.art_styles = interests.art_styles.replace(style, '').strip(', ')
                repop_data.remove(style)
                del interests.categories[style]

        if art_styles_list:
            # print(f'there is art styles list:{art_styles_list}')
            new_art_styles = ', '.join(art_styles_list)
            # print(f'joined art_styles_list to {new_art_styles}')
            if interests.art_styles:
                # print( f'there is interests.art_styles {interests.art_styles}' )
                interests.art_styles = ', '.join([interests.art_styles, new_art_styles]).strip(', ')
                for style in art_styles_list:
                    interests.categories.setdefault(style, 0)
                    repop_data.append(style)
                    interests.categories[style] += 1
            else:
                # print(f'there is no interests.art_styles:{interests.art_styles}')
                interests.art_styles = new_art_styles
                # print(f' set the new art_styles:{new_art_styles} as interests')
                for style in art_styles_list:
                    repop_data.append(style)
                    interests.categories[style] = 1
        else:
            interests.art_styles = ''
       
        # Handle genres
        genres_list = []
        for field, genre in genres_mapping.items():
            if request.POST.get(field) and genre not in interests.generes:
                genres_list.append(genre)
            elif not request.POST.get(field) and genre in repop_data:
                interests.generes = interests.generes.replace(genre, '').strip(', ')
                del interests.categories[genre]

        if genres_list:
            new_genres = ', '.join(genres_list)
            if interests.generes:
                interests.generes = ', '.join([interests.generes, new_genres]).strip(', ')
                for genre in genres_list:
                    interests.categories.setdefault(genre, 0)
                    interests.categories[genre] += 1
            else:
                interests.generes = new_genres
                for genre in genres_list:
                    interests.categories[genre] = 1
        else:
            interests.generes = ''

        # Handle historical periods
        periods_list = []
        for field, period in periods_mapping.items():
            if request.POST.get(field) and period not in interests.historical_periods:
                periods_list.append(period)
            elif not request.POST.get(field) and period in repop_data:
                interests.historical_periods = interests.historical_periods.replace(period, '').strip(', ')
                del interests.categories[period]

        if periods_list:
            new_periods = ', '.join(periods_list)
            if interests.historical_periods:
                interests.historical_periods = ', '.join([interests.historical_periods, new_periods]).strip(', ')
                for period in periods_list:
                    interests.categories.setdefault(period, 0)
                    interests.categories[period] += 1
            else:
                interests.historical_periods = new_periods
                for period in periods_list:
                    interests.categories[period] = 1
        else:
            interests.historical_periods = ''

        # Handle mediums
        mediums_list = []
        for field, medium in mediums_mapping.items():
            if request.POST.get(field) and medium not in interests.mediums:
                mediums_list.append(medium)
            elif not request.POST.get(field) and medium in repop_data:
                interests.mediums = interests.mediums.replace(medium, '').strip(', ')
                del interests.categories[medium]

        if mediums_list:
            new_mediums = ', '.join(mediums_list)
            if interests.mediums:
                interests.mediums = ', '.join([interests.mediums, new_mediums]).strip(', ')
                for medium in mediums_list:
                    interests.categories.setdefault(medium, 0)
                    interests.categories[medium] += 1
            else:
                interests.mediums = new_mediums
                for medium in mediums_list:
                    interests.categories[medium] = 1
        else:
            interests.mediums = ''

        interests.save()
        saved=True
        

    return (repop_data,saved)
####################################################

# add settings? idk what I would put in there
def hello(request):
    context={

    }

    return render(request,'base.html',context)

# add forgot username/password
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return render(request,'base.html')  # Redirect to the home page after successful login
        else:
            error_message = "Invalid username or password."
            return render(request, 'login.html', {'error_message': error_message})
    else:
        return render(request, 'login.html')

# add send verification to email or sms text they pick, then enter confirm code to reset 
def forgot_pass(request):
    first_step=True
    if request.POST:
        username=request.POST.get('username_entry')
        users=UserProfile.objects.all()
        for user in users:
            if username==user.user.username:
                contact_method=request.POST.get('contact_method')
                if contact_method=='text':
                    user=UserProfile.objects.filter(user=user.id).first() 

                    pass
                if contact_method=='email':
                    pass
                
                not_valid=False
                verification_code = generate_verification_code()
                context={
                    'verification_code':verification_code,
                    'not_valid':not_valid
                }
                return render(request,'forgot_pass.html',context)
            else:
                not_valid=True
                context={
                    'not_valid':not_valid
                }
                return render(request,'forgot_pass.html',context)
    context={
        'first_step':first_step
    }

    return render(request,'forgot_pass.html',context)

# maybe do so you can enter either password, text or email
def forgot_username(request):
    if request.POST:
        password=request.POST.get('password_entry')
        users=UserProfile.objects.all()
        for user in users:
            if password==user.user.password:
                return render(request,'base.html')
            else:
                not_valid=True
                context={
                    'not_valid':not_valid
                }
                return render(request,'forgot_username.html',context)

    return render(request,'forgot_username.html')


def reset_pass(request):


    context={

    }
    return render(request,'pass_reset.html',context)

def logout_view(request):

    userProfile=UserProfile.objects.all()
    customUser=CustomUser.objects.all()
    artwork=Artwork.objects.all()
    nft=NFT.objects.all()
    pricehistory=PriceHistory.objects.all()
    artworkPriceHistory=ArtworkPriceHistory.objects.all()
    watchlist=Watchlist.objects.all()
    interests=Interests.objects.all()
    prefs=Prefs.objects.all()

    # userProfile.delete()
    # customUser.delete()
    # artwork.delete()
    # nft.delete()
    # pricehistory.delete()
    # artworkPriceHistory.delete()
    # watchlist.delete()
    # interests.delete()
    # prefs.delete()


    logout(request)
    return render(request,'base.html')

# add checks on the html to make sure password is strong, and phone num/e_mail are in valid form
# add check to make sure username/phone num/email/ anything isn't alreayd being used
def register_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password1'])
            user.save()
            
            bio = form.cleaned_data['bio']
            profile_image = form.cleaned_data['profile_image']
            phone_num = form.cleaned_data['phone_num']
            e_mail = form.cleaned_data['e_mail']
            
            UserProfile.objects.create(user=user, bio=bio, profile_image=profile_image,phone_num=phone_num,e_mail=e_mail)
            
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            return render(request,'base.html') 
        else:
            # Print form errors
            print(form.errors)
            messages.error(request, 'Invalid form data. Please correct the errors.')
    else:
        form = RegistrationForm()
    
    return render(request, 'register.html', {'form': form})


def gallery(request):

    user = request.user
    nfts = NFT.objects.filter(is_for_sale=True)
    
    # interests_all=Interests.objects.all()
    # interests_all.delete()
    # print(interests_all)

    try:
        interests=Interests.objects.filter(user=user).first()
        if interests is None:
            interests=Interests.objects.create(user=user)
    except Interests.DoesNotExist:
        interests=Interests.objects.create(user=user)


    interests_list = list(interests.categories.keys())
    artworks = Artwork.objects.filter(is_draft=False, is_for_sale=True)


    artwork_scores = []

    for art in artworks:
        art_tags = {}
        for field in ['art_styles', 'generes', 'historical_periods', 'mediums']:
            tags = ast.literal_eval(getattr(art, field)) or {}
            for tag in tags:
                art_tags[tag] = 1
        relevance_score = sum(1 for check in interests_list if check in art_tags)
        artwork_scores.append((art, relevance_score))

    # Sort artworks by relevance score in ascending order
    artwork_scores.sort(key=lambda x: x[1])

    # Get the top 66 relevant artworks
    top_66_artworks = [score[0] for score in artwork_scores[-66:]][::-1]

    # Get the remaining artworks (up to 100 in total) to complete the list
    remaining_artworks = [score[0] for score in artwork_scores[:-66]][::-1]
    additional_artworks = remaining_artworks[:100 - len(top_66_artworks)]

    # Combine the top 66 most relevant artworks with additional artworks
    all_artworks = top_66_artworks + additional_artworks

    random.shuffle(all_artworks)


    context = {
        'artworks': all_artworks,
        'nfts': nfts,
    }
    return render(request, 'gallery.html', context)


def public_profile(request ,user_id=None):
    user_id=request.GET.get('user_id')
    if user_id is not None:
        artist_profile = UserProfile.objects.get(id=user_id)
        artworks = Artwork.objects.filter(artist_id=artist_profile.id, is_draft=False, is_for_sale=True)
        sold_artworks = Artwork.objects.filter(is_draft=False, is_for_sale=False)

    else:
        artwork_id=request.GET.get('artwork_id')
        art = Artwork.objects.get(id=artwork_id)
        artist_name = art.artist
        artist_profile = UserProfile.objects.get(user__username=artist_name)
        artworks = Artwork.objects.filter(artist_id=artist_profile.id,is_draft=False,is_for_sale=True)
        sold_artworks=Artwork.objects.filter(is_draft=False,is_for_sale=False)

    context = {
        # 'art': art,
        'user_profile': artist_profile,
        'artworks':artworks,
        'sold_artworks':sold_artworks
    }

    return render(request, 'public_profile.html', context)


def art_styles(request):

    repop_data,saved=save_and_repop_interests(request)

    if saved==True: 
        return render(request, 'gallery.html')
    
    context={
        'repop_data':repop_data
    }

    return render(request, 'art_styles.html',context)


def add_to_watchlist(request):
    artwork_id = request.POST.get('artwork_id')
    nft_id = request.POST.get('nft_id')
    user = request.user

    # interests_all=Interests.objects.all()
    # interests_all.delete()

    # Create or update the Watchlist model for the user
    watchlist, _ = Watchlist.objects.get_or_create(user=user)

    try:
        interests=Interests.objects.filter(user=user).first()
        if interests is None:
            interests=Interests.objects.create(user=user)
    except Interests.DoesNotExist:
        interests=Interests.objects.create(user=user)

    print(interests.categories)

    if artwork_id:
        # Add the artwork to the watchlist
        artwork = Artwork.objects.get(id=artwork_id)
        if artwork not in watchlist.artwork.all():
            watchlist.artwork.add(artwork)

            if artwork.art_styles:
                styles = ast.literal_eval(artwork.art_styles)
                for style in styles:
                    interests.categories.setdefault(style, 0)
                    interests.categories[style] += 1

            if artwork.generes:
                generes = ast.literal_eval(artwork.generes)
                for genere in generes:
                    interests.categories.setdefault(genere, 0)
                    interests.categories[genere] += 1

            if artwork.historical_periods:
                historical_periods = ast.literal_eval(artwork.historical_periods)
                for period in historical_periods:
                    interests.categories.setdefault(period, 0)
                    interests.categories[period] += 1

            if artwork.mediums:
                mediums = ast.literal_eval(artwork.mediums)
                for medium in mediums:
                    interests.categories.setdefault(medium, 0)
                    interests.categories[medium] += 1
     
    if nft_id:
        print('nft')
        # Add the NFT to the watchlist
        nft = NFT.objects.get(id=nft_id)
        if nft not in watchlist.nft.all():
            watchlist.nft.add(nft)

            artwork=nft.artwork
            if artwork.art_styles:
                styles = ast.literal_eval(artwork.art_styles)
                for style in styles:
                    interests.categories.setdefault(style, 0)
                    interests.categories[style] += 1

            if artwork.generes:
                generes = ast.literal_eval(artwork.generes)
                for genere in generes:
                    interests.categories.setdefault(genere, 0)
                    interests.categories[genere] += 1

            if artwork.historical_periods:
                historical_periods = ast.literal_eval(artwork.historical_periods)
                for period in historical_periods:
                    interests.categories.setdefault(period, 0)
                    interests.categories[period] += 1

            if artwork.mediums:
                mediums = ast.literal_eval(artwork.mediums)
                for medium in mediums:
                    interests.categories.setdefault(medium, 0)
                    interests.categories[medium] += 1

    # print(watchlist.artwork)
    watchlist.save()

    # Set the watchlist for the interests model
    interests.watchlist = watchlist
    interests.save()
    print(interests.categories)

    return HttpResponse('Added to watchlist')


def watchlist(request):
    user = request.user

    # Retrieve the user's watchlist
    watchlist = Watchlist.objects.filter(user=user).first()

    # Get the artworks and NFTs from the watchlist
    artworks = watchlist.artwork.all() if watchlist else []
    nfts = watchlist.nft.all() if watchlist else []

    context = {
        'artworks': artworks,
        'nfts': nfts,
    }
    return render(request, 'watchlist.html', context)


def filters(request):
    user=request.user

    try:
        draft = Prefs.objects.get(user=user)
        print('exists')
    except Prefs.DoesNotExist:
        print('create')
        draft = Prefs.objects.create(user=user)
        print(f'default sold check {draft.sold}')

    if draft:
        form = prefsForm(request.POST or None, request.FILES or None, instance=draft)
        form.initial = {
            'percent_growth': draft.percent_growth,
            'time_frame': draft.time_frame,
            'min_price': draft.min_price,
            'max_price': draft.max_price,
            'sold': draft.sold,
            'for_sale': draft.for_sale,
            'want_artwork': draft.want_artwork,
            'want_nfts': draft.want_nfts,
        }
      
    else:
        form = prefsForm(request.POST or None, request.FILES or None)


    if request.method == 'POST':
        if 'reset_filters' in request.POST:
            artworks=Artwork.objects.filter(is_for_sale=True)
            nfts=NFT.objects.filter(is_for_sale=True)

            prefs = form.save(commit=False)
            prefs.time_frame=None
            prefs.min_price=None
            prefs.max_price=None
            prefs.percent_growth=None
            prefs.want_artwork=True
            prefs.want_nfts=True
            prefs.sold=False
            prefs.for_sale=True
            prefs.save()
            return render(request, 'art_gallery.html',context={'artworks':artworks,'nfts':nfts})
        
        elif 'save_changes' in request.POST:
            # print(form.errors)
            if form.is_valid():
                prefs = form.save(commit=False)
                user=request.user
                prefs.artist = user

                time_frame = request.POST.get('time_frame')

                for_sale=request.POST.get('for_sale')
                if for_sale:
                    for_sale=bool(for_sale)
                else:
                    for_sale=False
               
                sold=request.POST.get('sold')
                if sold:
                    sold=bool(sold)
                else:
                    sold=False

                want_artwork=request.POST.get('want_artwork')
                if want_artwork:
                    want_artwork=bool(want_artwork)
                else:
                    want_artwork=False

                want_nfts=request.POST.get('want_nfts')
                if want_nfts:
                    want_nfts=bool(want_nfts)
                else:
                    want_nfts=False

                try:
                    percent_growth = float(request.POST.get('percent_growth', None))
                    min_price = float(request.POST.get('min_price', 0))
                    max_price = float(request.POST.get('max_price', float('inf')))
                    if min_price:
                        prefs.min_price=min_price
                    if max_price:
                        prefs.max_price=max_price
                    if percent_growth:
                        prefs.percent_growth=percent_growth
                except ValueError:
                    percent_growth = None
                    min_price=0
                    max_price=float('inf')

                current_date = datetime.now().date()
                if time_frame == 'week':
                    start_date = current_date - timedelta(days=7)
                    prefs.time_frame='week'
                elif time_frame == 'month':
                    start_date = current_date - timedelta(days=30)
                    prefs.time_frame='month'
                elif time_frame == 'year':
                    start_date = current_date - timedelta(days=365)
                    prefs.time_frame='year'
                elif time_frame=='any':
                    start_date = datetime(2000, 1, 1).date()
                    prefs.time_frame='any'
                else:
                    start_date = None
                    prefs.time_frame=start_date
                    # Handle invalid time frame input
                    return render(request, 'art_gallery.html', {'artworks': [], 'nfts': []})
                
                artworks = Artwork.objects.filter(is_draft=False, price_history__date__range=(start_date, current_date))
                nfts = NFT.objects.filter(price_history__date__range=(start_date, current_date))

                filtered_artworks = []
                filtered_nfts = []
                if want_artwork:
                    for artwork in artworks:
                        initial_price = artwork.price_history.order_by('date').first().price
                        current_price = artwork.price_history.order_by('date').last().price
                        percent_change = ((current_price - initial_price) / initial_price) * 100
                        if percent_change >= percent_growth and min_price <= artwork.art_price <= max_price:
                            if artwork not in filtered_artworks:
                                filtered_artworks.append(artwork)
                        if for_sale:
                            if artwork.is_for_sale==True:
                                if artwork not in filtered_artworks:
                                    filtered_artworks.append(artwork)
                        if sold:
                            if artwork.is_for_sale==False:
                                if artwork not in filtered_artworks:
                                    filtered_artworks.append(artwork)
                    
                if want_nfts:
                    for nft in nfts:
                        initial_price = nft.price_history.order_by('date').first().price
                        current_price = nft.price_history.order_by('date').last().price
                        percent_change = ((current_price - initial_price) / initial_price) * 100
                        if percent_change >= percent_growth and min_price <= nft.nft_price <= max_price:
                            if nft not in filtered_nfts:
                                filtered_nfts.append(nft)
                        if for_sale:
                            if nft.is_for_sale==True:
                                if nft not in filtered_nfts:
                                    filtered_nfts.append(nft)
                        if sold:
                            if nft.is_for_sale==False:
                                if nft not in filtered_nfts:
                                    filtered_nfts.append(nft)
                
                        # Update prefs object based on checkbox selections
               
                prefs.want_artwork = want_artwork
                prefs.want_nfts = want_nfts
                prefs.sold = sold
                prefs.for_sale = for_sale

                form.save()

            context = {
                'artworks': filtered_artworks,
                'nfts': filtered_nfts,
                'form' :form,
            }
            return render(request, 'art_gallery.html', context)
    
    return render(request, 'filters.html', context={'form':form,})

# make grwoth high to low, make clickon/dropdowns like goat,
def search(request):

    search=request.POST.get('search')
    if search:
        print(search)

    user=request.user
    try:
        draft = Prefs.objects.get(user=user)
    except Prefs.DoesNotExist:
        draft=None
        print('error no prefs object for user')

    if draft is not None:
        form = prefsForm(request.POST or None, request.FILES or None, instance=draft)
        form.initial = {
            'percent_growth': draft.percent_growth,
            'time_frame': draft.time_frame,
            'min_price': draft.min_price,
            'max_price': draft.max_price,
            'sold': draft.sold,
            'for_sale': draft.for_sale,
            'want_artwork': draft.want_artwork,
            'want_nfts': draft.want_nfts,
        }   
    else:
        form=None
        print('error no draft/form')

    if request.method == 'POST':
        if 'reset_filters' in request.POST:
            artworks=Artwork.objects.filter(is_for_sale=True)
            nfts=NFT.objects.filter(is_for_sale=True)

            prefs = form.save(commit=False)
            prefs.time_frame=None
            prefs.min_price=None
            prefs.max_price=None
            prefs.percent_growth=None
            prefs.want_artwork=True
            prefs.want_nfts=True
            prefs.sold=False
            prefs.for_sale=True
            form.save()

            return render(request, 'art_gallery.html',context={'artworks':artworks,'nfts':nfts})
        
        elif 'save_changes' or 'search' in request.POST:
            if form.is_valid():
                prefs = form.save(commit=False)
                user=request.user
                prefs.artist = user

                time_frame = request.POST.get('time_frame')

                for_sale=request.POST.get('for_sale')
                if for_sale:
                    for_sale=bool(for_sale)
                else:
                    for_sale=False
               
                sold=request.POST.get('sold')
                if sold:
                    sold=bool(sold)
                else:
                    sold=False

                want_artwork=request.POST.get('want_artwork')
                if want_artwork:
                    want_artwork=bool(want_artwork)
                else:
                    want_artwork=False

                want_nfts=request.POST.get('want_nfts')
                if want_nfts:
                    want_nfts=bool(want_nfts)
                else:
                    want_nfts=False

                try:
                    percent_growth = request.POST.get('percent_growth')
                    if percent_growth:
                        percent_growth=float(percent_growth)
                    else:
                        percent_growth=None
                    min_price = float(request.POST.get('min_price', 0))
                    max_price = request.POST.get('max_price')
                    if percent_growth:
                        prefs.percent_growth=percent_growth
                    if min_price:
                        prefs.min_price=min_price   
                    if max_price:
                        prefs.max_price=max_price
                except ValueError:
                    percent_growth = None
                    min_price=0
                    max_price=float('inf')

                current_date = datetime.now().date()
                if time_frame == 'week':
                    start_date = current_date - timedelta(days=7)
                    prefs.time_frame='week'
                elif time_frame == 'month':
                    start_date = current_date - timedelta(days=30)
                    prefs.time_frame='month'
                elif time_frame == 'year':
                    start_date = current_date - timedelta(days=365)
                    prefs.time_frame='year'
                elif time_frame=='any':
                    start_date = datetime(2000, 1, 1).date()
                    prefs.time_frame='any'
                else:
                    start_date = None
                    prefs.time_frame=start_date
                
            prefs.want_artwork = want_artwork
            prefs.want_nfts = want_nfts
            prefs.sold = sold
            prefs.for_sale = for_sale
            form.save()

            print('save changes:')
            repop_data,saved=save_and_repop_interests(request)

            changedFilters=request.POST.get('changedFilters','')
            if changedFilters:
                changedFilters=json.loads(changedFilters)
                print(f'changed filters: {changedFilters}')
                for filter in changedFilters:
                    for key in filter:
                        switch=filter[key]
                        if switch=='on' or switch=='True':
                            repop_data.append(key)
                        if switch=='off':
                            # check repop data to see if need pop
                            # print(repop_data)
                            pass
            response = HttpResponse("Option selected and stored as a cookie.")
            print(f'repop data: {repop_data}')
            repop_data_json = json.dumps(repop_data)
            response.set_cookie('repop_data', repop_data_json)
            print(f'cookie has been set, response:{response}')
            print(f'repop_data_json: {repop_data_json}')


            repop_data=request.COOKIES.get('repop_data','')
            print('in search view still__________')
            if repop_data:
                print(repop_data)
                repop_data=json.loads(repop_data)
                print(f'repop_cookie: {repop_data}')
            else:
                print('problem w repop cookies ')
                print(repop_data)
            print('out of search____________________')
            
        
            context={
                'repop_data':repop_data,
                'form':form,
                'response':response
            }
            return render(request,'search.html',context)
                
    
    else:
        print('not post: ')
        repop_data,saved=save_and_repop_interests(request)

        changedFilters = request.COOKIES.get('changedFilters', '')
        print(changedFilters)

    context={
        'repop_data':repop_data,
        'form':form,
    }
    return render(request,'search.html',context)

# percent gorwth high to low, price high to low filters
def search_req(request): 

    user=request.user
    form_data=request.POST.get('form_data')
    parsed_data = dict(item.split('=') for item in form_data.split('&'))
    # print(parsed_data)

    repop_data=request.COOKIES.get('repop_data','')
    if repop_data:
        print(repop_data)
        repop_data=json.loads(repop_data)
        print(f'repop_cookie: {repop_data}')
    else:
        print('problem w repop cookies ')
        print(repop_data)

    try:
        draft = Prefs.objects.get(user=user)
    except Prefs.DoesNotExist:
        draft=None
        print('error no prefs object for user')

    if draft is not None:
        form = prefsForm(request.POST or None, request.FILES or None, instance=draft)
        form.initial = {
            'percent_growth': draft.percent_growth,
            'time_frame': draft.time_frame,
            'min_price': draft.min_price,
            'max_price': draft.max_price,
            'sold': draft.sold,
            'for_sale': draft.for_sale,
            'want_artwork': draft.want_artwork,
            'want_nfts': draft.want_nfts,
        }
        
        prefs = form.save(commit=False)
    else:
        form=None
        print('error no draft/form')

    percent_growth=parsed_data.get('percent_growth')
    if percent_growth:
        percent_growth=float(percent_growth)
    else:
        percent_growth=None

    time_frame=parsed_data.get('time_frame')

    min_price=parsed_data.get('min_price')
    if min_price:
        min_price=float(min_price)
    else:
        min_price=None
    
    max_price=parsed_data.get('max_price')
    if max_price:
        max_price=float(max_price)
    else:
        max_price=None

    want_artwork=parsed_data.get('want_artwork')
    if want_artwork:
        want_artwork=bool(want_artwork)
    else:
        want_artwork=False

    want_nfts=parsed_data.get('want_nfts')
    if want_nfts:
        want_nfts=bool(want_nfts)
    else:
        want_nfts=False

    sold=parsed_data.get('sold')
    if sold:
        sold=bool(sold)
    else:
        sold=False
    
    for_sale=parsed_data.get('for_sale')
    if for_sale:
        for_sale=bool(for_sale)
    else:
        for_sale=False

    prefs = form.save(commit=False)
    prefs.time_frame=time_frame
    prefs.min_price=min_price
    prefs.max_price=max_price
    prefs.percent_growth=percent_growth
    prefs.want_artwork=want_artwork
    prefs.want_nfts=want_nfts
    prefs.sold=sold
    prefs.for_sale=for_sale
    form.save() 

    try:
        prefs = Prefs.objects.get(user=user)
    except Prefs.DoesNotExist:
        print('error no prefs object for user')
    
    time_frame = prefs.time_frame

    for_sale=prefs.for_sale
    if for_sale:
        for_sale=bool(for_sale)
    else:
        for_sale=False
    
    sold=prefs.sold
    if sold:
        sold=bool(sold)
    else:
        sold=False

    want_artwork=prefs.want_artwork
    if want_artwork:
        want_artwork=bool(want_artwork)
    else:
        want_artwork=False

    want_nfts=prefs.want_nfts
    if want_nfts:
        want_nfts=bool(want_nfts)
    else:
        want_nfts=False

    try:
        percent_growth = prefs.percent_growth
        if percent_growth is None:
            pass
            # print('percent growth none')
        min_price = float(prefs.min_price or 0)
        max_price = float(prefs.max_price or float('inf'))
    except ValueError :
        percent_growth = None
        min_price=0
        max_price=float('inf')

    # print(min_price, max_price)

    current_date = timezone.now() # date()
    if time_frame == 'week':
        start_date = current_date - timezone.timedelta(days=7)
    elif time_frame == 'month':
        start_date = current_date - timezone.timedelta(days=30)
    elif time_frame == 'year':
        start_date = current_date - timezone.timedelta(days=365)
    elif time_frame == 'any':
        start_date = timezone.datetime(2000, 1, 1).date()
    else:
        start_date = timezone.datetime(2000, 1, 1).date()

    # print(start_date)
    # print(current_date)

    artworks = Artwork.objects.filter(is_draft=False, updated_at__range=(start_date, current_date))
    nfts = NFT.objects.filter(updated_at__range=(start_date, current_date))
    # print(artworks)
    
    filtered_results=[]

    if want_artwork:
        artwork_id_list=[]
        artwork_data_list = []
        for artwork in artworks:
            price_history_ordered = artwork.price_history.order_by('date')
            if price_history_ordered.exists():
                initial_price = price_history_ordered.first().price
                current_price = price_history_ordered.last().price
                # initial_price = artwork.price_history.order_by('date').first().price
                # current_price = artwork.price_history.order_by('date').last().price
                percent_change = ((current_price - initial_price) / initial_price) * 100
            else:
                percent_change=0

            artwork_data = {
                # maybe add art id
                "art_price": artwork.art_price,
                "percent_change": percent_change,
                "is_for_sale": artwork.is_for_sale,
                "is_sold": not artwork.is_for_sale
            }

            if artwork.id in artwork_id_list:
                pass
            else:
                artwork_data_list.append(artwork_data)
                artwork_id_list.append(artwork.id)

            for artwork_data in artwork_data_list:
                meets_criteria = True

                if min_price is not None and artwork_data["art_price"] < min_price:
                    meets_criteria = False

                if max_price is not None and artwork_data["art_price"] > max_price:
                    meets_criteria = False

                # print((artwork_data["percent_change"]))
                # print(percent_growth)
                if percent_growth is not None and (artwork_data["percent_change"]) < percent_growth:
                    meets_criteria = False

                if for_sale and not artwork_data["is_for_sale"]:
                    meets_criteria = False

                if sold and artwork_data["is_for_sale"]:
                    meets_criteria = False

                # not sure if this filtering logic is all correct I think so but idk
                if sold and for_sale:
                        meets_criteria = True

                if meets_criteria:
                    filtered_results.append(artwork)
            artwork_data_list.clear()

    if want_nfts:
        nft_id_list=[]
        nft_data_list = []
        for nft in nfts:
            price_history_ordered = nft.price_history.order_by('date')
            if price_history_ordered.exists():
                initial_price = price_history_ordered.first().price
                current_price = price_history_ordered.last().price
                # initial_price = nft.price_history.order_by('date').first().price
                # current_price = nft.price_history.order_by('date').last().price
                percent_change = ((current_price - initial_price) / initial_price) * 100
            else:
                percent_change=0
     
            nft_data = {
                "art_price": nft.nft_price,
                "percent_change": percent_change,
                "is_for_sale": nft.is_for_sale,
                "is_sold": not nft.is_for_sale
            }
            if nft.id in nft_id_list:
                pass
            else:
                nft_data_list.append(nft_data)
                nft_id_list.append(nft.id)

            for nft_data in nft_data_list:
                
                meets_criteria = True

                if min_price is not None and nft_data["art_price"] < min_price:
                    meets_criteria = False

                if max_price is not None and nft_data["art_price"] > max_price:
                    meets_criteria = False

                if percent_growth is not None and nft_data["percent_change"] < percent_growth:
                    meets_criteria = False

                if for_sale and nft_data["is_for_sale"]==False:
                    meets_criteria = False

                if sold and nft_data["is_for_sale"]:
                    meets_criteria = False

                if sold and for_sale:
                    meets_criteria = True
                    
                if meets_criteria:
                    filtered_results.append(nft)
            nft_data_list.clear()
       
    # print(filtered_results)
    search_req = request.POST.get('query', '')

    word = []
    keywords = []

    for letter in search_req:
        if letter != ' ':
            word.append(letter)
        else:
            keyword = ''.join(word)
            keywords.append(keyword)
            word = []

    if word:
        keyword = ''.join(word)
        keywords.append(keyword)

    search_req = keywords

    stemmer = PorterStemmer()
    stemmed_words = []  # Create a new list to store the stemmed words

    for word in search_req:
        root_word = stemmer.stem(word)
        if root_word not in stemmed_words: 
            if root_word not in search_req:
                stemmed_words.append(root_word)

    # Update the original search_req with the stemmed words
    search_req.extend(stemmed_words)
    # print(search_req)

    relevant_artworks = []
    relevant_scores = []

    if want_artwork:
        for art in filtered_results:
            if isinstance(art, Artwork):
                similar_words = []
                word_count = 0
                keywords = art.keywords

                for word in search_req:
                    if word in keywords:
                        word_count += 1
                        similar_words.append(word)
                if word_count > 0:
                    if art not in relevant_artworks:
                        relevant_artworks.append(art)
                        relevant_scores.append(word_count)

    if want_nfts:
        for nft in filtered_results:
            if isinstance(nft, NFT):
                similar_words = []
                word_count = 0
                keywords = nft.keywords

                for word in search_req:
                    if word in keywords:
                        word_count += 1
                        similar_words.append(word)
                if word_count > 0:
                    if nft not in relevant_artworks:
                        relevant_artworks.append(nft)
                        relevant_scores.append(word_count)


    # just set to true until add form fields
    want_users=True
    if want_users:
        users=UserProfile.objects.all()
        zipped_user_results = find_similar_usernames(search_req, users)
        usernames = [item for item,_ ,_ in zipped_user_results]
        # print(usernames)
    
    # print(relevant_artworks)
    relevance_tuples = list(zip(relevant_scores, relevant_artworks))
    relevance_tuples.sort(key=itemgetter(0), reverse=True)
    relevant_results = [item for _, item in relevance_tuples]

    data = []

    if want_users:
        for username, user_id,_ in zipped_user_results:
            user_obj=UserProfile.objects.get(user=user_id)
            image_file=user_obj.profile_image
            with open(image_file.path, 'rb') as f:
                image_data = base64.b64encode(f.read()).decode('utf-8')
            data.append({
                'username': username,
                'public_profile_url': reverse('public_profile') + '?user_id=' + str(user_id),
                'image_data':image_data
            })

    for item in relevant_results:
        if isinstance(item, Artwork):
            art = item
            if art.is_for_sale:
                owner=art.owner.username
                image_file=art.main_image
                with open(image_file.path, 'rb') as f:
                    image_data = base64.b64encode(f.read()).decode('utf-8')
                data.append({
                    'name': art.name,
                    'art_id': art.id,
                    'is_for_sale': True,
                    'art_details_url': reverse('art_details') + '?artwork_id=' + str(art.id),
                    'image_data': image_data,
                    'art_price':art.art_price,
                    'owner':owner,
                    'share_count':art.shares_count,
                    'for_sale':"For Sale"
                  
                })
            else:
                owner=art.owner.username
                image_file=art.main_image
                with open(image_file.path, 'rb') as f:
                    image_data = base64.b64encode(f.read()).decode('utf-8')
                data.append({
                    'name': art.name,
                    'art_id': art.id,
                    'is_not_for_sale': True,
                    'sold_art_details_url': reverse('sold_art_details') + '?artwork_id=' + str(art.id),
                    'image_data':image_data,
                    'art_price':art.art_price,
                    'owner':owner,
                    'share_count':art.shares_count,
                    'for_sale': "Sold",
                })
        elif isinstance(item, NFT):
            nft = item
            if nft.is_for_sale:
                owner=nft.owner.username
                image_file=nft.main_image
                with open(image_file.path, 'rb') as f:
                    image_data = base64.b64encode(f.read()).decode('utf-8')
                data.append({
                    'name': nft.name,
                    'nft_id': nft.id,
                    'is_for_sale': True,
                    'nft_details_url': reverse('investor_details') + '?nft_id=' + str(nft.id),
                    'image_data':image_data,
                    'nft_price':nft.nft_price,
                    'owner':owner,
                    'NFT_count':nft.NFT_count,
                    'for_sale': "Sold",
                    'percent_change':nft.percent_change
                })
            else:
                owner=nft.owner.username
                image_file=nft.main_image
                with open(image_file.path, 'rb') as f:
                    image_data = base64.b64encode(f.read()).decode('utf-8')
                data.append({
                    'name': nft.name,
                    'nft_id': nft.id,
                    'is_not_for_sale': True,
                    'nft_details_url': reverse('investor_details') + '?nft_id=' + str(nft.id),
                    'image_data':image_data,
                    'nft_price':nft.nft_price,
                    'owner':owner,
                    'NFT_count':nft.NFT_count,
                    'for_sale': "Sold",
                    'percent_change':nft.percent_change
                })

    # print(data) 

    return JsonResponse(data, safe=False)
















    # user=request.user

    # print('in test')
    # try:
    #     prefs = Prefs.objects.get(user=user)
    # except Prefs.DoesNotExist:
    #     print('error no prefs object for user')

    # max_price=prefs.max_price
    # min_price=prefs.min_price

    # artworks=Artwork.objects.all()
    # first_relevant_results=[]
    # for artwork in artworks:
    #     if min_price <= artwork.art_price <= max_price:
    #         first_relevant_results.append(artwork)

    # search_req = request.POST.get('query', '')
    # print(search_req)

    # word = []
    # keywords = []

    # for letter in search_req:
    #     if letter != ' ':
    #         word.append(letter)
    #     else:
    #         keyword = ''.join(word)
    #         keywords.append(keyword)
    #         word = []

    # if word:
    #     keyword = ''.join(word)
    #     keywords.append(keyword)

    # search_req = keywords

    # stemmer = PorterStemmer()
    # stemmed_words = []  # Create a new list to store the stemmed words

    # for word in search_req:
    #     root_word = stemmer.stem(word)
    #     if root_word not in stemmed_words: 
    #         if root_word not in search_req:
    #             stemmed_words.append(root_word)

    # # Update the original search_req with the stemmed words
    # search_req.extend(stemmed_words)

    # # print(search_req)

    # relevant_results = []
    # relevant_scores = []

    # for art in first_relevant_results:
    #     if isinstance(art, Artwork):
    #         similar_words = []
    #         word_count = 0
    #         keywords = art.keywords

    #         for word in search_req:
    #             if word in keywords:
    #                 word_count += 1
    #                 similar_words.append(word)
    #         if word_count > 0:
    #             if art not in relevant_results:
    #                 relevant_results.append(art)
    #                 relevant_scores.append(word_count)

    # data = []
    # for item in relevant_results:
    #     if isinstance(item, Artwork):
    #         art = item
    #         if art.is_for_sale:
    #             data.append({
    #                 'name': art.name,
    #                 'art_id': art.id,
    #                 'is_for_sale': True,
    #                 'art_details_url': reverse('art_details') + '?artwork_id=' + str(art.id),
    #             })
    #         else:
    #             data.append({
    #                 'name': art.name,
    #                 'art_id': art.id,
    #                 'is_not_for_sale': True,
    #                 'sold_art_details_url': reverse('sold_art_details') + '?artwork_id=' + str(art.id),
    #             })
    #     elif isinstance(item, NFT):
    #         nft = item
    #         if nft.is_for_sale:
    #             data.append({
    #                 'name': nft.artwork.name,
    #                 'nft_id': nft.id,
    #                 'is_for_sale': True,
    #                 'nft_details_url': reverse('investor_details') + '?nft_id=' + str(nft.id),
    #             })
    #         else:
    #             data.append({
    #                 'name': nft.artwork.name,
    #                 'nft_id': nft.id,
    #                 'is_not_for_sale': True,
    #                 'nft_details_url': reverse('investor_details') + '?nft_id=' + str(nft.id),
    #             })

    # print(data)
    
    # return JsonResponse({"data": data})





 # for artwork in artworks:
        #     initial_price = artwork.price_history.order_by('date').first().price
        #     current_price = artwork.price_history.order_by('date').last().price
        #     percent_change = ((current_price - initial_price) / initial_price) * 100
        #     if min_price or max_price:
        #         if min_price and max_price:
        #             if min_price <= artwork.art_price <= max_price:
        #                 if artwork not in filtered_results:
        #                     filtered_results.append(artwork)
        #         if min_price and not max_price:
        #             if min_price <= artwork.art_price:
        #                 if artwork not in filtered_results:
        #                     filtered_results.append(artwork)
        #         if max_price and not min_price:
        #             if artwork.art_price <= max_price:
        #                 if artwork not in filtered_results:
        #                     filtered_results.append(artwork)
        #         if percent_growth is not None or 0:
        #             percent_growth=float(percent_growth)
        #             if percent_change >= percent_growth and min_price <= artwork.art_price <= max_price:
        #                 if artwork not in filtered_results:
        #                     filtered_results.append(artwork)
        #         if for_sale:
        #             if artwork.is_for_sale==True:
        #                 if artwork not in filtered_results:
        #                     filtered_results.append(artwork)
        #         if sold:
        #             if artwork.is_for_sale==False:
        #                 if artwork not in filtered_results:
        #                     filtered_results.append(artwork)
        #     else:
        #         if percent_growth is not None or 0:
        #             percent_growth=float(percent_growth)
        #             if percent_change >= percent_growth:
        #                 if artwork not in filtered_results:
        #                     filtered_results.append(artwork)
        #         if for_sale:
        #             if artwork.is_for_sale==True:
        #                 if artwork not in filtered_results:
        #                     filtered_results.append(artwork)
        #         if sold:
        #             if artwork.is_for_sale==False:
        #                 if artwork not in filtered_results:
        #                     filtered_results.append(artwork)

        

    # if want_nfts:
    #     for nft in nfts:
    #         initial_price = nft.price_history.order_by('date').first().price
    #         current_price = nft.price_history.order_by('date').last().price
    #         percent_change = ((current_price - initial_price) / initial_price) * 100
    #         if min_price and max_price:
    #             if min_price <= nft.nft_price <= max_price:
    #                 filtered_results.append(artwork)
    #         if min_price and not max_price:
    #             if min_price <= nft.nft_price:
    #                 filtered_results.append(artwork)
    #         if max_price and not min_price:
    #             if nft.nft_price <= max_price:
    #                 filtered_results.append(artwork)
    #         if percent_growth is not None or 0:
    #             percent_growth=float(percent_growth)
    #             if percent_change >= percent_growth and min_price <= nft.nft_price <= max_price:
    #                 if nft not in filtered_results:
    #                     filtered_results.append(nft)
    #         if for_sale:
    #             if nft.is_for_sale==True:
    #                 if nft not in filtered_results:
    #                     filtered_results.append(nft)
    #         if sold:
    #             if nft.is_for_sale==False:
    #                 if nft not in filtered_results:
    #                     filtered_results.append(nft)