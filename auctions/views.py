from django.contrib.auth import authenticate, login, logout

from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import Category, Comment, User, Listing, Bid, Watchlist_Item


def index(request):
    if request.method == "POST":
        category_name = request.POST["category"]

        if category_name == "all":
            return HttpResponseRedirect(reverse("index"))

        return HttpResponseRedirect(f"categories/{category_name}")

    else:
        listings = Listing.objects.filter(active=True)
        categories = Category.objects.all()
        return render(request, "auctions/index.html", {
            "listings": listings,
            "categories": categories,
        })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

def creating(request):
    if request.method == "POST":

        owner = request.user
        if not owner.is_authenticated:
            categories = Category.objects.all()
            return render(request, "auctions/creating.html", {
                "categories": categories,
                "message": "you must be signed in to create a listing"
            })
        title = request.POST["title"]
        description = request.POST["description"]
        bid = request.POST["bid"]
        image_url = request.POST["image"]
        category_id = request.POST["category_id"]
        category = Category.objects.get(id=category_id)

        listing= Listing.objects.create(
            owner=owner, category=category,
            title=title, description=description,
            image_url=image_url,price=bid,
            )
        listing.save()
        return HttpResponseRedirect(reverse("index"))
    
    else:
        categories = Category.objects.all()
        return render(request, "auctions/creating.html", {
            "categories": categories,
        })
        


def categories(request):
    categories = Category.objects.all()
    for category in categories:
        category.save()
    return render(request, "auctions/categories.html", {
        "categories": categories,
    })



def category(request, category_name):
    if category_name == "all":
        listings = Listing.objects.all()
        categories = Category.objects.all()
        return render(request, "auctions/index.html", {
            "listings": listings,
            "categories": categories,
        })

    categories = Category.objects.all()
    category = Category.objects.filter(name=category_name).first()
    if not category:
        return render(request, "auctions/categories.html", {
        "categories": categories,
        "message": f"there is no category with the name of {category_name}"
        })

    listings = Listing.objects.filter(category=category)
    categories = Category.objects.all().exclude(name=category.name)
    return render(request, "auctions/index.html", {
        "listings": listings,
        "categories": categories,
        "current_category": category,
    })    
    



def listing(request, listing_id):
    listing = Listing.objects.filter(id=listing_id).first()
    comments = Comment.objects.filter(listing=listing)
    owner = False
    winner = None
    try:
        if listing.owner == request.user:

            owner = True
    except:
        pass
    try:
        winner = listing.winner
    except:
        pass

        
        

    if request.method == "GET":
        if not listing:
            return render(request, "auctions/error.html", {
                "message": f"there is no listing with the id {listing_id}",
            })

        return render(request, "auctions/listing.html", {
            "listing": listing,
            "comments": comments,
            "owner": owner,
            "winner": winner,
        })
        
    else:
        money = float(request.POST["bid"])

        if money <= listing.current_price:
            return render(request, "auctions/listing.html", {
                "listing": listing,
                "comments": comments,
                "message": f"the bid must be Greater than {listing.current_price}",
            })
        
        new_bid = Bid.objects.create(user=request.user, listing=listing, money=money)
        new_bid.save()
        
        listing = Listing.objects.get(id=listing_id)
        return render(request, "auctions/listing.html", {
            "listing": listing,
            "comments": comments,
            "message2": "Your bid's been added successufly"
        })   
        
        
        
def add(request, listing_id):
    listing = Listing.objects.filter(id=listing_id).first()

    if not listing:
        return render(request, "auctions/error.html", {
            "message": f"there is no listing with the id {listing_id}",
        })

    watchlist= Watchlist_Item.objects.filter(user=request.user).first()
    if not watchlist:
        watchlist= Watchlist_Item.objects.create(user=request.user)
        watchlist.save()

    watchlists = watchlist.listing.all()
    
    if not listing in watchlists:
        watchlist.listing.add(listing)
        
    return HttpResponseRedirect(reverse("favourite"))

def remove(request, listing_id):
    listing = Listing.objects.get(id=listing_id)
    watchlist= Watchlist_Item.objects.get(user=request.user)

    watchlists = watchlist.listing.all()
    if listing in watchlists:
        watchlist.listing.remove(listing)        

    return HttpResponseRedirect(reverse("favourite")) 

def favourite(request):
    
    watchlist= Watchlist_Item.objects.filter(user=request.user).first()
    watchlists = watchlist.listing.all()

    
    return render(request, "auctions/watchlist.html", {
        "watchlists": watchlists,
    })    

def sell(request, listing_id):
    listing = Listing.objects.get(id=listing_id)
    listing.active = False
    bids = Bid.objects.filter(listing=listing).order_by("-money").first()
    if not bids:
        listing.winner = listing.owner
    else:
        listing.winner = bids.user
    listing.save()
    return HttpResponseRedirect(reverse("listing", kwargs={'listing_id': listing_id}))

def comment(request, listing_id):
    if request.method == "POST":
        listing = Listing.objects.get(id=listing_id)
        comment_text = request.POST["comment"]

        comment = Comment.objects.create(text=comment_text, listing=listing, user=request.user)
        comment.save()
        return HttpResponseRedirect(reverse("listing", kwargs={'listing_id': listing_id}))



    

        
    

    
         
        

    

