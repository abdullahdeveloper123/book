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
                user_id=request.user.id
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
      user_id = request.user.id
      quantity = data['quantity']

      if (product_id, user_id, quantity):
          Order.objects.create(product_id=product_id, user_id=user_id, quantity=quantity)
          return JsonResponse({"objective":"order saved success", "success":True}, status=200)
      else: 
            return JsonResponse({"objective":'data not valid', 'success':False}, status=401)
   else:
      return JsonResponse({"objective":'Method not allowed', 'success':False}, status=405)
   
