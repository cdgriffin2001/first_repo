from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from hello.forms import RegistrationForm, BidForm
from django.contrib import messages
from hello.models import UserProfile,Artwork,NFT, NFT_bid
from django.db.models import Count
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import io, base64
import matplotlib
from datetime import datetime
import matplotlib.pyplot as plt
import mplfinance as mpf
import pandas as pd
import base64
import io

from hello.models import PriceHistory,GraphImage
matplotlib.use('Agg')


# add details about the investor like protfolio growth over time, number of artworks owned etc
def investor_page(request):
    user = request.user
    artworks = Artwork.objects.filter(is_draft=False, owner=user)

    nfts=NFT.objects.filter(owner=user,is_for_sale=False)
    nfts_for_sale=NFT.objects.filter(is_for_sale=True)
    print(nfts_for_sale)


    context = {
        'artworks': artworks,
        'nfts': nfts,
        'nfts_for_sale':nfts_for_sale,
    }

    return render(request, 'investor_page.html', context)


def  NFT_post(request):
    user = request.user
    artworks = Artwork.objects.filter(is_draft=False, owner=user)
    nfts=NFT.objects.filter(is_for_sale=False)
    nft_id=request.GET.get('nft_id')
    nft=NFT.objects.get(id=nft_id)
    nft.is_for_sale=True
    nft.save()
    nfts_for_sale=NFT.objects.filter(is_for_sale=True)

    context={
        'nfts':nfts,
        'artworks':artworks,
        'nfts_for_sale':nfts_for_sale,
    }
    return render(request, 'investor_page.html',context)


def investor_details(request):
    artwork_id = request.GET.get('artwork_id')
    if artwork_id:
        artwork = Artwork.objects.get(id=artwork_id)
        artwork_id = artwork.id
        highest_bid = NFT_bid.objects.filter(artwork=artwork_id).order_by('-bid_amount').first()
    

    nft_id = request.GET.get('nft_id')
    if nft_id:
        nft = NFT.objects.get(id=nft_id)
        artwork = Artwork.objects.get(NFT=nft)
        artwork_id = artwork.id
        highest_bid = NFT_bid.objects.filter(artwork=artwork_id).order_by('-bid_amount').first()
        
        price_history_objects = PriceHistory.objects.filter(nft=nft)
        nft_count=nft.NFT_count

        # Create a dictionary to store prices grouped by day
        prices_by_day = {}

        # Iterate over the price history objects and group prices by day
        for price_history_obj in price_history_objects:
            # Extract the day from the date
            day = price_history_obj.date.date()

            # Convert the price to float
            price = float(price_history_obj.price)

            # Check if the day already exists in the dictionary
            if day in prices_by_day:
                # Update the highest price if necessary
                if price > prices_by_day[day]["High"]:
                    prices_by_day[day]["High"] = price

                # Update the lowest price if necessary
                if price < prices_by_day[day]["Low"]:
                    prices_by_day[day]["Low"] = price

                # Update the closing price if it's a later time on the same day
                if price_history_obj.date > prices_by_day[day]["Date"]:
                    prices_by_day[day]["Close"] = price
                    prices_by_day[day]["Date"] = price_history_obj.date
            else:
                prices_by_day[day] = {
                    "Date": price_history_obj.date,
                    "High": price,
                    "Low": price,
                    "Open": price,
                    "Close": price
                }
                # print(prices_by_day[day])

        # Create the final dictionary in the desired format
        data = {
            "Date": [],
            "Open": [],
            "High": [],
            "Low": [],
            "Close": []
        }
        # Populate the final dictionary
        for day, prices in prices_by_day.items():
            data["Date"].append(str(prices["Date"].date()))
            data["Open"].append(prices["Open"])
            data["High"].append(prices["High"])
            data["Low"].append(prices["Low"])
            data["Close"].append(prices["Close"])

        # Print the final dictionary
        # print(data)
    df = pd.DataFrame(data)
    df['Date'] = pd.to_datetime(df['Date'])
    df.set_index('Date', inplace=True)  # Set 'Date' column as the index

    # Generate the candlestick graph
    mpf.plot(df, type='candle', title="Candlestick Graph", ylabel="Price")

    # Save the graph to a buffer
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()

    # Encode the image as base64 string
    graphic = base64.b64encode(image_png)
    graphic = graphic.decode('utf-8')

    #see if there is existing graph image, if there is delete it and create new one
    User=request.user
    previous_graphs=GraphImage.objects.filter(NFT=nft,user=User)
    if previous_graphs:
        previous_graphs.delete()
    if graphic:
        graph_object=GraphImage(image=graphic,NFT=nft,user=User)
        graph_object.save()
    else:
        graph_object=GraphImage.objects.filter(NFT=nft,user=User).first()

    print(nft.percent_change)
    print(price_history_obj.previous_price)
    print(nft.nft_price)
  

    context = {
        'artwork': artwork,
        'nft': nft,
        'graphic': graphic,
        'highest_bid': highest_bid,
        'artwork_id': artwork_id,
        'nft_id':nft_id,
        'nft_count':nft_count,
        'graph_object':graph_object,
    }

    return render(request, 'investor_details.html', context)

