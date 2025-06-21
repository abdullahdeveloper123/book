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
@login_required(login_url='login')
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
@login_required(login_url='login')
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

@login_required(login_url='login')
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



@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            password = data.get('password')
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Invalid JSON'}, status=400)

        if email and password:
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                return JsonResponse({'success': True, 'redirect_url': '/'})
            else:
                return JsonResponse({'success': False, 'message': 'Invalid credentials'})
        else:
            return JsonResponse({'success': False, 'message': 'Email and password required'}, status=400)
    else:
        # If GET or other method, return your login form
        return render(request, 'login.html')

@login_required(login_url='login')
def logout_view(request):
    logout(request)
    return redirect('login')

# /////////////////////////////////////////////////////////////////////////Recommendations triggered///////////////////////////////////////////////////////////////////////

def recommended_books(request):
    user_id = request.user.id
    purchases = Order.objects.filter(user_id=user_id)

    # Get distinct genres from user's purchased orders
    owned_genres = purchases.values_list('genre', flat=True).distinct()

    if owned_genres.exists():
        # If user has purchased genres, pick 4 random books from those
        books = Book.objects.filter(genre__in=owned_genres).order_by('?')[:4]
    else:
        # Otherwise, pick any 4 random books
        books = Book.objects.order_by('?')[:4]

    # Prepare recommendations list
    recommendations = []
    for book in books:
        recommendations.append({
            'name': book.name,
            'author': book.author,
            'price': book.price,
            'product_id':book.id,
            'quote':book.quotes
        })

    return JsonResponse({'recommendations': recommendations})
     
# /////////////////////////////////////////////////////////////////////////Top trending books ///////////////////////////////////////////////////////////////////////

def top_viewed_books(request):
    top_books = Book.objects.order_by('-views')[:5]
    data = []
    
    for q in top_books:
        data.append({
            "id": q.id,
            "title": q.quotes,
            "author": q.author,
            "name":q.name,
            "genre": q.genre,
            "year": q.year,
            "pages": q.pages,
            "description": q.desc,
            "price":q.price
        })
    if not cache.get('top_books'):
           cache.set('top_books', data, timeout=1500)
    result = cache.get('top_books')
    return JsonResponse(result, safe=False)


# /////////////////////////////////////////////////////////////////////////Order Handlers///////////////////////////////////////////////////////////////////////


@login_required(login_url='login')
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

 

@login_required(login_url='login')
@csrf_exempt
def save_order(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            product_id = data.get('product_id')
            quantity = data.get('quantity')

            if not (product_id and quantity and int(quantity) > 0):
                return JsonResponse({"objective": "Invalid data", "success": False}, status=400)

            product = get_object_or_404(Book, id=product_id)
            user_id = request.user.id

            # Create order
            Order.objects.create(
                product_id=product.id,
                user_id=user_id,
                quantity=quantity,
                name=product.name,
                quotes=product.quotes,
                genre=product.genre,
                year=product.year,
                pages=product.pages,
                desc=product.desc,
                price=product.price,
                author=product.author
            )

            # Increment views and save
            product.views += 1
            product.save()

            return JsonResponse({"objective": "Order saved successfully", "success": True}, status=200)

        except Exception as e:
            return JsonResponse({"objective": f"Error: {str(e)}", "success": False}, status=500)

    else:
        return JsonResponse({"objective": "Method not allowed", "success": False}, status=405)
   
# get order list
@login_required(login_url='login')
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
