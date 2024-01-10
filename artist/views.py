from django.shortcuts import render, redirect
from hello.models import UserProfile
from hello.models import CustomUser
from hello.forms import ProfileForm
from hello.models import Artwork
from hello.forms import ArtworkForm
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from hello.forms import ArtworkForm
from hello.models import Artwork
from hello.models import NFT
from hello.models import NFT_bid
from hello.forms import NFT_bidForm
from hello.models import PriceHistory, GraphImage
from datetime import datetime
import matplotlib
from datetime import datetime
import matplotlib.pyplot as plt
import mplfinance as mpf
import pandas as pd
import base64
import io
from django.core.files import File
import os
from django.conf import settings
from hello.models import ArtworkPriceHistory,ArtworkGraphImage
matplotlib.use('Agg')


def draft_view(request):
    artist_id = request.user.id
    draft_id=request.POST.get('draft_id')
    user = request.user
    drafts = Artwork.objects.filter(artist=user, is_draft=True)
    context = {
        'user': user,
        'drafts': drafts,
        'artist_id':artist_id,
        'draft_id':draft_id
    }
    return render(request, 'draft_view.html', context)


def delete_draft(request):
    artist = request.user
    print(artist)
    draft_id=request.POST.get('draft_id')
    print(draft_id)
    draft = Artwork.objects.get(id=draft_id)
    draft.delete()

    return redirect('draft_view')

# add details about artist like net worth of art and nft, growth of value over time all that 
# add way to add artist to watchlist, make it so you click to toggle between sold artworks or art for sale
# add artist only data like how many ppl added u to wathclist other data 
def artist_page(request):
    artworks = Artwork.objects.filter(is_draft=False,is_for_sale=True)
    sold_artworks=Artwork.objects.filter(is_draft=False,is_for_sale=False)
    try:
        # Retrieve the user profile associated with the logged-in user
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        # If UserProfile does not exist, create a new UserProfile object for the user
        user_profile = UserProfile.objects.create(user=request.user)
        
    # use this code to set default profile picture
    # default_image_path=os.path.join(settings.MEDIA_ROOT, 'profile_pictures', 'profile_placeholder.jpg')
    # with open(default_image_path, 'rb') as img_file:
    #     user_profile.profile_image.save(
    #         os.path.basename(default_image_path),
    #         File(img_file)
    #     ) 
    # print(user_profile.profile_image)

    context = {
        'artworks' : artworks,
        'sold_artworks':sold_artworks,
        'user_profile': user_profile,
    }
    
    return render(request, 'artist_page.html', context)


def edit_profile(request, artist_id):
    user = request.user
    artworks = Artwork.objects.filter(artist=user, is_draft=False)
    try:
        # Retrieve the user profile associated with the logged-in user
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        # If UserProfile does not exist, create a new UserProfile object for the user
        user_profile = UserProfile.objects.create(user=request.user)

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            if 'save_changes' in request.POST:
                # Save the form data to update the artist's profile
                profile_image = request.FILES['profile_image']
                print(profile_image)
                if profile_image:
                    user_profile.profile_image = profile_image
                    user_profile.save()
                    # if user_profile.profile_image and user_profile.profile_image.read() != profile_image.read():
                    #     user_profile.profile_image.delete()
                    #     print('delete')         
                form.save()  # Save the rest of the form data
                print(user_profile.profile_image.name)

                return redirect('artist_page')

    else:
        form = ProfileForm(instance=user_profile)

    context = {
        'artworks': artworks,
        'form': form,
        'artist_id': artist_id,
        'user_profile': user_profile
    }

    return render(request, 'edit_profile.html', context)


def delete_artwork(request):
    artist = request.user
    artwork_id=request.POST.get('artwork_id')
    artwork = Artwork.objects.get(id=artwork_id, artist=artist)
    artwork.delete()

    return redirect('artist_page')



