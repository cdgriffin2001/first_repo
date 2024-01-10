from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from hello.forms import RegistrationForm, BidForm
from django.contrib import messages
from hello.models import UserProfile,Artwork,NFT, NFT_bid,ArtworkGraphImage, ArtworkPriceHistory, Bid, PriceHistory
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
import matplotlib
from datetime import datetime
import matplotlib.pyplot as plt
import mplfinance as mpf
import pandas as pd
import base64
import io
from django.utils import timezone
from datetime import timedelta
from hello.forms import ArtworkForm
from hello.models import CustomUser, Interests
import ast, random
import nltk
nltk.download('punkt')
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize


from hello.models import ArtworkPriceHistory,ArtworkGraphImage
matplotlib.use('Agg')


def sold_art_details(request):
    artwork_id=request.GET.get('artwork_id')
    user=request.user
    art = Artwork.objects.get(id=artwork_id)
    artist_name = art.artist
    nft_all=NFT.objects.filter(artwork_id=artwork_id,is_for_sale=True)

    highest_bid = NFT_bid.objects.filter(artwork=artwork_id).order_by('-bid_amount').first()
    # print(highest_bid)
    # print(art.is_for_sale)

    price_history_objects = ArtworkPriceHistory.objects.filter(artwork=art)
    
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
    print(df)
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
    previous_graphs=ArtworkGraphImage.objects.filter(Artwork=art,user=User)
    if previous_graphs:
        previous_graphs.delete()
        print('delete')
    if graphic:
        artwork_graph_object=ArtworkGraphImage(image=graphic,Artwork=art,user=User)
        artwork_graph_object.save()
    else:
        print('else')
        artwork_graph_object=ArtworkGraphImage.objects.filter(Artwork=art,user=User).first()


    if request.method == 'POST':
        action = request.POST.get('button')
        if action=="post art":
            art.is_for_sale=True
            art.save()
    # print(art.is_for_sale)

    if nft_all.exists():
        lowest_id_nft = nft_all.first()
        nft_id= lowest_id_nft.id
        nft=NFT.objects.filter(id=nft_id).first()
    else:
        nft=0
        print("No available NFTs for sale.")

    if artist_name != user:
        print('good')
        context = {
            'artwork': art,
            'highest_bid':highest_bid,
        }
        return render(request, 'sold_art_details.html',context)
    else:
        art = Artwork.objects.get(id=artwork_id)
        artist_name = art.artist# get rid of this later only for development
        messages.error(request,'Cannot purchase your own art')
        context = {
            'artwork': art,
            'nft':nft,
            'highest_bid':highest_bid,
            'graphic':graphic,
            'artwork_id':artwork_id
        }
        return render(request, 'sold_art_details.html',context)

# add additonal pictures opiton
# fix keywords '_'/doubles : 'contemporary_art_movements', 'contemporary_art_mov', 'digital_art', 'digital_art']
def art_post(request, artist_id):
    artist = get_object_or_404(CustomUser, id=artist_id)
    artworks = Artwork.objects.filter(artist=artist)
    draft_id = request.GET.get('draft_id')  # Retrieve the draft_id from query parameters

    if draft_id:
        draft = get_object_or_404(Artwork, id=draft_id)
        form = ArtworkForm(request.POST or None, request.FILES or None, instance=draft)
        form.initial = draft.__dict__  # Prepopulate the form with the draft information
    else:
        form = ArtworkForm(request.POST or None, request.FILES or None)
 
    if request.method == 'POST':
        action = request.POST.get('action')
        if form.is_valid():
            keywords=[]
            artwork = form.save(commit=False)
            user=request.user
            artwork.artist = user
 
            if action == 'Post Art':
                artwork.is_draft = False  
                artwork.is_for_sale=False
                artwork.owner=request.user
                
                word = []
                keywords = ['artwork','art']

                keywords.append(artwork.name)
                description = artwork.description

                for letter in description:
                    if letter != ' ':
                        word.append(letter)
                    else:
                        keyword = ''.join(word)
                        keywords.append(keyword)
                        word = []

                # To capture the last keyword after the loop finishes (if any)
                if word:
                    keyword = ''.join(word)
                    print(keyword)
                    keywords.append(keyword)

                stemmer = PorterStemmer()
                stemmed_words = []  # Create a new list to store the stemmed words

                for word in keywords:
                    root_word = stemmer.stem(word)
                    if root_word not in stemmed_words: 
                        if root_word not in keywords:
                            stemmed_words.append(root_word)

                keywords.extend(stemmed_words)
                print(keywords)

                artwork.keywords=keywords
                artwork.save()
                messages.success(request, 'Artwork posted successfully.')
                return redirect('art_tags')
            elif action == 'Save to Drafts':
                artwork.is_draft = True  # Set is_draft to True for saving as draft
                artwork.save()
                messages.success(request, 'Artwork saved to drafts.')
                return redirect('art_post', artist_id=artist_id)
            else:
                print(f'form is valid but {action} not post or draft check: {form} or {artwork}')

        else:
            if action == 'Post Art':
                messages.error(request, 'Error creating artwork. Please check the form.')
            elif action == 'Save to Drafts':
                # Remove specific field errors for saving to drafts
                form.errors.pop('name', None)
                form.errors.pop('description', None)
                form.errors.pop('shares_count', None)
                form.errors.pop('share_price', None)

                # Check if only main_image and artist fields are missing
                if any(field for field in form.errors.keys() if field):
                    messages.error(request, "Error creating draft. Please provide at minimum a main image.")
                    return redirect('art_post', artist_id=artist_id)
                else:
                    artwork = form.save(commit=False)
                    artwork.artist = request.user
                    artwork.is_draft = True  # Set is_draft to True for saving as draft
                    artwork.save()
                    messages.success(request, 'Artwork saved to drafts.')
                    return redirect('art_post', artist_id=artist_id)

    context = {
        'artist': artist,
        'artworks': artworks,
        'form': form,
    }

    return render(request, 'art_post.html', context)


def art_details(request):
    artwork_id=request.GET.get('artwork_id')
    user=request.user
    # if request.method== 'POST':
        # artwork_id=request.POST.get('artwork_id')
    print(artwork_id)
    art = Artwork.objects.get(id=artwork_id)
    artist_name = art.artist
    if artist_name != user:
        print('good')
        context = {
            'artwork': art,
        }
        return render(request, 'art_details.html',context)
    else:
        art = Artwork.objects.get(id=artwork_id)
        artist_name = art.artist# get rid of this later only for development
        messages.error(request,'Cannot purchase your own art')
        context = {
            'artwork': art,
        }
        return render(request, 'art_details.html',context)


def purchase_art(request):
    artwork_id=request.GET.get('artwork_id')

    # artwork_id = request.POST.get('artwork_id')
    art = Artwork.objects.get(id=artwork_id)
    
    
    if request.method == 'POST':
        pass

    else:
        print('not post')
    
    context={
        'art':art
    }
    return render(request, 'place_bid.html',context)


def place_bid(request):
    graphic=request.GET.get('graphic')
    if request.method == 'POST':
        artwork_id = request.POST.get('artwork_id')
        print(artwork_id)
        artwork = Artwork.objects.get(id=artwork_id)
        form = BidForm(request.POST)
        if form.is_valid():
            bid = form.save(commit=False)
            bid.artwork = artwork
            bid.bidder = request.user
            bid.save()
            context={
                'artwork': artwork,
                # 'graphic':graphic
            }
            return render(request,'art_details.html',context)
        else:
            print('form not valid')
            print(form.errors)
            print(form.cleaned_data)
    else:
        
        form = BidForm()

    context = {
        # 'artwork': artwork,
        'form': form,
        # 'graphic':graphic
    }

    return render(request, 'place_bid.html', context)

# add private sale between two users 
def confirm_sale(request): 
    if request.method=='POST':
        artwork_id=request.POST.get('artwork_id')
        art = Artwork.objects.get(id=artwork_id)
        new_owner=request.user
        art.owner = new_owner

        highest_bid = Bid.objects.filter(artwork_id=artwork_id).order_by('-bid_amount').first()
        art.art_price = float(highest_bid.bid_amount)
        # print(art.art_price)

        new_share_price = float(highest_bid.bid_amount) / art.shares_count
        art.share_price = new_share_price
        print(f'share price: {art.share_price} for art_id {art.id}')
        
        num_of_sales=art.number_of_sales
        if num_of_sales>0.1:
            # print('nft is being re-sold')
            pass
        if num_of_sales<0.1:
            num_of_sales+=1
            count=0
            for i in range(art.shares_count):
                count+=1
                nft = NFT(artwork=art, owner=art.owner, is_for_sale=True)
                nft.main_image=art.main_image
                nft.nft_price=art.share_price
                nft.name=f'{art.name} #{count}'
                nft.NFT_count=art.shares_count

                art_keywords_str=art.keywords
                art_keywords_list = art_keywords_str[1:-1].split(', ')
                keywords = [keyword.strip("'") for keyword in art_keywords_list]
                keywords.extend(['nft', 'nfts'])
                # print(keywords)
                nft.keywords=keywords

                index_to_replace = nft.keywords.index('artwork')
                nft.keywords[index_to_replace] = 'nfts'
                index_to_replace = nft.keywords.index('art')
                nft.keywords[index_to_replace] = 'nft'
                # print(nft.keywords)
                nft.save()

                print('nft saved')                   
        art.number_of_sales=num_of_sales
        art.has_NFT=True
        art.is_for_sale=False
        art.updated_at=timezone.now()
        art.clear_bids()
        art.save()
        print('art saved')

        Artworkprice_history = ArtworkPriceHistory(artwork=art, date=timezone.now(), price=art.art_price)
        Artworkprice_history.save()
        print('artwork price history saved')

        art.update_percent_change()
        print('update art percent change')

        nfts=NFT.objects.filter(artwork=artwork_id)
        for nft in nfts:
            print('iterating thru nfts')
            previous_price = nft.price_history.filter(date__lt=timezone.now()).order_by('-date').first()
            print(f'previous price for each nft:{previous_price}')
            price_history = PriceHistory(
                nft=nft,
                date=timezone.now(),
                price=art.share_price,
                previous_price=previous_price.price if previous_price else art.share_price
                )
            price_history.save()
            print(f'nft price history saved for:{price_history} ')

            nft.update_percent_change()
       
        return render(request,'confirm_sale.html')
    else:
        print('error')


def art_tags(request): 
    user=request.user
    # getting the wrong artwork need to pass it directly from art post to this view maybe pass the art id?
    artwork=Artwork.objects.filter(artist=user,is_for_sale=False,is_draft=False).first()

    if request.method == 'POST':
        art_styles_mapping = {
            'realisim': 'realism',
            'abstract': 'abstract',
            'impressionisim': 'impressionism',
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

        keywords=ast.literal_eval(artwork.keywords)
        artwork.art_styles = []
        artwork.generes = []
        artwork.historical_periods = []
        artwork.mediums = []

        stemmer = PorterStemmer()

        for field, style in art_styles_mapping.items():
            if request.POST.get(field):
                artwork.art_styles.append(style)
                keywords.append(style)
                keywords.append(stemmer.stem(style))

        for field, genre in genres_mapping.items():
            if request.POST.get(field):
                artwork.generes.append(genre)
                keywords.append(genre)
                keywords.append(stemmer.stem(genre))

        for field, period in periods_mapping.items():
            if request.POST.get(field):
                artwork.historical_periods.append(period)
                keywords.append(period)
                keywords.append(stemmer.stem(period))

        for field, medium in mediums_mapping.items():
            if request.POST.get(field):
                artwork.mediums.append(medium)
                keywords.append(medium)
                keywords.append(stemmer.stem(medium))
        
        artwork.is_for_sale=True
        artwork.keywords=keywords
        artwork.save()
        # print(artwork)
        # print(artwork.is_for_sale)
        # print(artwork.keywords)


        artworks = Artwork.objects.filter(is_draft=False,is_for_sale=True)
        sold_artworks=Artwork.objects.filter(is_draft=False,is_for_sale=False)
        try:
            # Retrieve the user profile associated with the logged-in user
            user_profile = UserProfile.objects.get(user=request.user)
        except UserProfile.DoesNotExist:
            # If UserProfile does not exist, create a new UserProfile object for the user
            user_profile = UserProfile.objects.create(user=request.user)

        context = {
            'artworks' : artworks,
            'sold_artworks':sold_artworks,
            'user_profile': user_profile,
        }

        return render(request,'artist_page.html',context)
        
    return render(request,'art_tags.html')

# - fix! error with literal eval/art tags, idk?
def art_gallery(request):
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
    artworks = Artwork.objects.filter(is_draft=False)
    print(artworks)

    artwork_scores = []

    for art in artworks:
        art_tags = {}
        for field in ['art_styles', 'generes', 'historical_periods', 'mediums']:
            field_content = getattr(art, field)
            print("Field:", field, "Content:", field_content)
            try:
                tags = ast.literal_eval(getattr(art, field)) or {}
                for tag in tags:
                    art_tags[tag] = 1
            except (ValueError, SyntaxError):
                print("Error evaluating literal:", field_content)
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
    return render(request, 'art_gallery.html', context)



