from django.shortcuts import render, redirect,get_object_or_404
from django.http import JsonResponse
from .models import Book,Order,Wishlist
from django.core.cache import cache
from django.core.paginator import Paginator
import json
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate,login,logout
import stripe
from django.conf import settings
from django.forms.models import model_to_dict
import random

stripe.api_key = settings.STRIPE_SECRET_KEY

 
# /////////////////////////////////////////////////////////////////////////Home///////////////////////////////////////////////////////////////////////
def home(request):
      quotes = cache.get('quote')
      page = Paginator(Book.objects.all(), 5)    
      page_count = request.GET.get('page', 1) 
      page_obj = page.get_page(page_count) 
  
      if not quotes:
          raw = page_obj 
          quotes = list(raw)
          cache.set('quote', quotes, timeout=1000) 
  
      quotes = cache.get('quote') 
      
      return render(request, 'index.html', {'page_obj': page_obj, 'total': str(len(quotes))})


# /////////////////////////////////////////////////////////////////////////Detail///////////////////////////////////////////////////////////////////////
def detail(request, id):
    cache_key = f'product_{id}'
    product = cache.get(cache_key)

    if not product:
        book = get_object_or_404(Book, id=id)
        product = model_to_dict(book)
        cache.set(cache_key, product, timeout=1200)

    return render(request, 'detail.html', {
        'product': product,
        'STRIPE_PUBLISHABLE_KEY': settings.STRIPE_PUBLISHABLE_KEY
    })

# /////////////////////////////////////////////////////////////////////////save product wishlist///////////////////////////////////////////////////////////////////////
@csrf_exempt
def save(request):
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return JsonResponse({'success': False, 'status': 401})

        try:
            data = json.loads(request.body)
            book = get_object_or_404(Book, id=data['id'])
        except (KeyError, json.JSONDecodeError):
            return JsonResponse({'success': False, 'status': 400, 'message': 'Invalid data'})

        # Check if the book is already in user's wishlist
        if not Wishlist.objects.filter(product_id=book.id, user_id=request.user.id).exists():
            Wishlist.objects.create(
                product_id=book.id,
                name=book.name,
                quotes=book.quotes,
                desc=book.desc,
                price=book.price,
                author=book.author, 
                user_id=request.user.id,
                genre= book.genre
            )

        return JsonResponse({'status': True, 'message': 'Book saved to wishlist'})

    return JsonResponse({'message': 'Method not allowed'}, status=405)


@csrf_exempt
def remove_wishlist(request):
    try:  
        data = json.loads(request.body)
        id = data['id']
        query = Wishlist.objects.get(id=id) 
        query.delete()
        return JsonResponse({"objective": 'successfully removed liked item'}, status=200)
    except Exception as e:
        return JsonResponse({"objective": str(e)}, status=400)  
# /////////////////////////////////////////////////////////////////////////Get Wishlist///////////////////////////////////////////////////////////////////////
     

# /////////////////////////////////////////////////////////////////////////Rendering Wishlist///////////////////////////////////////////////////////////////////////
@login_required(login_url='login')
def wishlist(request):
   query = Wishlist.objects.filter(user_id=request.user.id)  
   product = Book.objects.filter()

   return render(request, 'wishlist.html', {'query':query})



# /////////////////////////////////////////////////////////////////////////Search Book///////////////////////////////////////////////////////////////////////
@csrf_exempt
def search(request):
 if request.method =="POST":
     requested_data = json.loads(request.body)
     query = Book.objects.filter(
     Q(name__icontains=requested_data['query']) | Q(author__icontains=requested_data['query'])
)
     if query:
        results=[]
        for q in query:
          data = {
              'id':q.id,
              'name':q.name, 
              'author':q.author
          } 
          results.append(data)
        return JsonResponse(results, safe=False)      
     else:
        return JsonResponse({'message':'no results found'}, safe=False)      
                     
 else:    
     return render(request, 'detail.html')
 

# /////////////////////////////////////////////////////////////////////////User Library///////////////////////////////////////////////////////////////////////    
def library(request):
    return render(request, 'library.html')






# /////////////////////////////////////////////////////////////////////////Authentication Register and Login///////////////////////////////////////////////////////////////////////    

def register(request):
   if request.method=='POST':
      name = request.POST.get('name')
      email = request.POST.get('email')
      password = request.POST.get('password')
      if (name,email,password): 
        if User.objects.filter(username=email):
               return JsonResponse({'objective':'user already exists'}, status=403)
        else:
               query = User(username=email,first_name=name,email=email,password=password)  
               query.set_password(password)
               query.save()
               login(request, query)
               return redirect('home')
      else:  JsonResponse({'objective':'invalid creds'}, status=403)
   else:
      return render(request, 'register.html')



def login_view(request):
   if request.method=='POST':
      email = request.POST.get('email')
      password = request.POST.get('password')
      if (email,password):
        user = authenticate(username = email, password=password)
        if user != None:
           login(request, user)
           return redirect('home')
        else:
           return redirect('login')
           
      else:  JsonResponse({'objective':'invalid creds'})
   else:
      return render(request, 'login.html')
   

   
def logout_view(request):
    logout(request)
    return redirect('login')

# /////////////////////////////////////////////////////////////////////////Purchase triggered///////////////////////////////////////////////////////////////////////
 
     



# /////////////////////////////////////////////////////////////////////////Order Handlers///////////////////////////////////////////////////////////////////////



@csrf_exempt
def create_payment_intent(request):
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        amount = int(data['amount'])  # amount in paisa or cents (not rupees/dollars)
        intent = stripe.PaymentIntent.create(
            amount=amount,
            currency='usd',  # or 'pkr' if supported in your account
            automatic_payment_methods={'enabled': True},
        )
        return JsonResponse({'clientSecret': intent.client_secret})

def checkout(request):
    return render(request, 'checkout.html', {
        'STRIPE_PUBLISHABLE_KEY': settings.STRIPE_PUBLISHABLE_KEY
    })


@csrf_exempt
def save_order(request):
   if request.method=='POST':
      data = json.loads(request.body)
      product_id = data['product_id']
      product= Book.objects.get(id=product_id)
      user_id = request.user.id
      quantity = data['quantity']
      

      if (product_id, user_id, quantity):
          Order.objects.create(product_id=product_id, user_id=user_id, quantity=quantity, name=product.name, quotes =product.quotes,genre=product.genre,year=product.year,pages=product.pages,desc=product.desc,price=product.price,author=product.author)
          return JsonResponse({"objective":"order saved success", "success":True}, status=200)
      else: 
            return JsonResponse({"objective":'data not valid', 'success':False}, status=401)
   else:
      return JsonResponse({"objective":'Method not allowed', 'success':False}, status=405)
   
# get order list
@csrf_exempt
def get_orders(request):
  query = Order.objects.filter(user_id=request.user.id)
  if not query:
      return JsonResponse({'objective':"library is empty","success":False, "empty":True}, status=200)
  products = []
  for q in query:
       data = {
            "id": 1,
            "title": q.quotes,
            "author":q.author,
            "genre":q.genre,
            "year": q.year,
            "pages": q.pages,
            "description": q.desc,
            "dateAdded": q.date,
            "product_id":q.product_id
            
       }
       products.append(data)
  return JsonResponse(products, safe=False, status=200)
  


# add books 
 

@csrf_exempt
def add_books(request):
    try:
        titles = [
            "The Last Dawn", "Echoes of Silence", "Whispers in the Dark", "Fragments of Time",
            "The Forgotten Path", "Journey Beyond Stars", "Shadow and Light", "Tides of Fate",
            "Songs of the Earth", "Memoirs of the Broken"
        ]

        quotes = [
            "Not all those who wander are lost.",
            "Even the darkest night will end and the sun will rise.",
            "Hope is the thing with feathers that perches in the soul.",
            "Every moment is a fresh beginning.",
            "To live will be an awfully big adventure.",
            "The past beats inside me like a second heart.",
            "Time you enjoy wasting was not wasted.",
            "A reader lives a thousand lives before he dies.",
            "Courage is found in unlikely places.",
            "We are all stories in the end."
        ]

        authors = [
            "Harper West", "Daniel Rivers", "Eleanor Bright", "Liam Cross",
            "Sophia Blake", "Noah Reed", "Ava Sinclair", "Mason Hart",
            "Isla Monroe", "Leo Hayes"
        ]

        for _ in range(20):
            Book.objects.create(
                name=random.choice(titles),
                quotes=random.choice(quotes),
                genre=random.choice(['Fiction', 'Non-fiction', 'Sci-Fi', 'Fantasy', 'Biography', 'History', 'Romance']),
                year=random.randint(1950, 2024),
                pages=random.randint(120, 850),
                desc=f"A captivating tale of {random.choice(['hope', 'betrayal', 'love', 'courage', 'redemption'])}, spanning generations.",
                price=random.randint(700, 2500),
                author=random.choice(authors),
                views=random.randint(0, 5000)
            )

        return JsonResponse({'message': '20 books added successfully!'}, status=201)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
