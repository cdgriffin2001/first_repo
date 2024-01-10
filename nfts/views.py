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
from hello.models import PriceHistory, GraphImage, Interests
from datetime import datetime
import matplotlib
from datetime import datetime
import matplotlib.pyplot as plt
import mplfinance as mpf
import pandas as pd
import base64
import io,random,ast

from hello.models import ArtworkPriceHistory,ArtworkGraphImage
matplotlib.use('Agg')



def NFT_Bid(request):
    artwork_id=request.GET.get('artwork_id')
    art=Artwork.objects.get(id=artwork_id)
    # nft_all=NFT.objects.filter(artwork_id=artwork_id,is_for_sale=True)
    nft_id=request.GET.get('nft_id')
    nft=NFT.objects.filter(id=nft_id).first()
    User=request.user
    graph_object=GraphImage.objects.filter(NFT=nft,user=User).first()

    # if nft_all.exists():
    #     lowest_id_nft = nft_all.first()
    #     nft_id= lowest_id_nft.id
    # else:
    #     print("No available NFTs for sale.")

    context = {
        'nft': nft,
        'art':art,
        'nft_id':nft_id,
        'artwork_id':artwork_id,
        # 'graph_object':graph_object
    }
    return render(request, 'NFT_bid.html',context)


def NFT_place_bid(request):
    nft_id=request.POST.get('nft_id')
    nft = NFT.objects.filter(id=nft_id).first()
    User=request.user
    graph_object=GraphImage.objects.filter(NFT=nft,user=User).first()


    if request.method== 'POST':    
        # print(nft_id)
        # nft = NFT.objects.filter(id=nft_id).first()
        nft_artwork=nft.artwork
        artwork_id=nft_artwork.id
        art=Artwork.objects.get(id=artwork_id)
        form = NFT_bidForm(request.POST)
        if form.is_valid():
            bid = form.save(commit=False)
            bid.NFT = nft
            # print(bid.NFT)
            bid.bidder = request.user
            bid.artwork=nft_artwork
            bid.save()
            context={
                'nft': nft,
                'artwork':art,
                'nft_id':nft_id,
                'graph_object':graph_object,
                'artwork_id':artwork_id
            }
            return render(request,'investor_details.html',context)
        else:
            print('form not valid')
            print(form.errors)
            print(form.cleaned_data)

    context={
        'nft':nft,
        'art':art,
        'graph_object':graph_object,
        'artwork_id':artwork_id,
    }
    return render(request, 'NFT_Bid.html',context)


def confirm_nft_sale(request):
    if request.method=='POST':
        nft_id=request.POST.get('nft_id')

        nft = NFT.objects.get(id=nft_id)
        new_owner=request.user
        nft.owner=new_owner

        nft_artwork=nft.artwork
        artwork_id=nft_artwork.id
        art=Artwork.objects.get(id=artwork_id)

        highest_bid = NFT_bid.objects.filter(NFT=nft).order_by('-bid_amount').first()
        sold_price=float(highest_bid.bid_amount)


        art.art_price = (float(art.art_price))+(float(highest_bid.bid_amount))-(float(art.share_price))
        new_share_price = float(art.art_price) / art.shares_count
        art.share_price = new_share_price
        art.save()

        price_history = PriceHistory(nft=nft, date=datetime.now(), price=sold_price)
        price_history.save()
        nft.update_percent_change()

        nft.NFT_count=art.shares_count
        nft.dates=art.updated_at
        nft.is_for_sale=False
        nft.nft_price=sold_price
        nft.clear_bids()
        nft.save()

        Artworkprice_history = ArtworkPriceHistory(artwork=art, date=datetime.now(), price=art.art_price)
        Artworkprice_history.save()
    
        return render(request,'confirm_NFT_sale.html')
    else:
        print('error')


def nft_gallery(request):
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
    nfts = NFT.objects.all()

    relevant_nfts = []
    relevance_scores=[]
    count=0

    for nft in nfts:
        art_tags = {}
        for field in ['art_styles', 'generes', 'historical_periods', 'mediums']:
            nft_art=nft.artwork
            field_content = getattr(nft_art, field)
            print("Field:", field, "Content:", field_content)
            try:
                tags = ast.literal_eval(getattr(nft_art, field)) or {}
                for tag in tags:
                    art_tags[tag] = 1
            except (ValueError, SyntaxError):
                print("Error evaluating literal:", field_content)
                
            relevance_score = sum(1 for check in interests_list if check in art_tags)

        if count<66:
            if not relevant_nfts or relevance_score > relevance_scores[0]:
                relevant_nfts.append(nft)
                relevance_scores.append(relevance_score)
                count+=1
    
        if 66<count<100:
            relevant_nfts.append((nft,relevance_score))
            count+=1

        if count>100:
            relevant_nfts.clear()
            relevance_scores=0 
            count=0
            pass
    
    random.shuffle(relevant_nfts)
    print(relevant_nfts)


    context = {
        'artworks': relevant_nfts,
        'nfts': nfts,
    }
    return render(request, 'nft_gallery.html', context)



