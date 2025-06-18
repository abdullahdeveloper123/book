from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .models import Book,Order,Wishlist
from django.core.cache import cache
from django.views.decorators.cache import cache_page
from django.core.paginator import Paginator
import random
import json
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
import requests
from django.contrib.auth.decorators import login_required

# /////////////////////////////////////////////////////////////////////////Home///////////////////////////////////////////////////////////////////////
@login_required(login_url='login')
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
     product = Book.objects.get(id=id)
     product.views = product.views=+1
     product.save()
     return render(request, 'detail.html',{'product':product})
 
# /////////////////////////////////////////////////////////////////////////save product wishlist///////////////////////////////////////////////////////////////////////
@csrf_exempt
def save(request):
  if request.method =='POST':
   try:  
     data = json.loads(request.body)
     product = Book.objects.get(id=data['id'])
     if not Wishlist.objects.filter(product_id=product.id):
       query = Wishlist(product_id = product.id) 
       query.save()
     return JsonResponse({'status':True, 'message':'saved'})
   except Exception as e:
      return JsonResponse({'message':str(e)})
  else:
      return JsonResponse({'message':'method not allowed'})
  
# /////////////////////////////////////////////////////////////////////////Get Wishlist///////////////////////////////////////////////////////////////////////
     

# /////////////////////////////////////////////////////////////////////////Rendering Wishlist///////////////////////////////////////////////////////////////////////
def wishlist(request):
   return render(request, 'wishlist.html')



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

@csrf_exempt
def register(request): 
    if request.method == 'POST':
        data = json.loads(request.body)
        name = data['name']
        email = data['email']
        password = data['password']
        username = name[:-(int(len(name)/2))] + str(random.randint(1000, 9999))
        user = User.objects.create(username=username, email=email, password=password) 
        user.set_password(password)
        user.save()
        tokens =  requests.post('http://127.0.0.1:8000/api/token/',json={"username": username, "password": password})
      
        response = JsonResponse({'objective': 'User saved successfully','data':username}) 
        response.set_cookie(
               key='token_access',
               value=tokens.json()['access'],
               secure=True,
               httponly=True)
            

        response.set_cookie(
              key='token_refresh',
              value=tokens.json()['refresh'],
              secure=True,
              httponly=True
          )

        print(tokens)
         
       
        return  response
    else:
        return render(request, 'register.html')


@csrf_exempt
def login(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')
        password = data.get('password')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return JsonResponse({'objective': 'User not found'}, status=404)

        # Get tokens via SimpleJWT
        tokens = requests.post('http://127.0.0.1:8000/api/token/', json={
            "username": user.username,
            "password": password
        })

        if tokens.status_code == 200:
            token_data = tokens.json()

            response = JsonResponse({'objective': 'Login success'})
            response.set_cookie(
                key='token_access',
                value=token_data['access'],
                httponly=True,
                secure=True
            )
            response.set_cookie(
                key='token_refresh',
                value=token_data['refresh'],
                httponly=True,
                secure=True
            )

            return response

        else:
            return JsonResponse({'objective': 'Invalid credentials'}, status=401)

    else:
        return render(request, 'login.html')



# /////////////////////////////////////////////////////////////////////////Add dummy Books///////////////////////////////////////////////////////////////////////

def add_dummy_books(request):
    sample_books = [
        ("The Silent Forest", "In the stillness, truth finds its voice.", "A suspenseful tale set in an ancient forest where secrets of the past refuse to stay buried.", 650, "Lena Ray", 230),
        ("Echoes of Tomorrow", "The future belongs to those who dare.", "A sci-fi journey through alternate futures, forgotten timelines, and human resilience.", 850, "Jared Quinn", 780),
        ("Songs of Dust", "Even dust carries stories.", "A poetic narrative of lives lost and rediscovered in war-torn lands.", 500, "Aisha Malik", 132),
        ("Digital Gods", "We created them. Now they own us.", "A tech-thriller about AI corporations controlling modern civilization.", 950, "Kevin Hartley", 1025),
        ("Broken Halos", "Not every angel gets to fly.", "A dark fantasy novel about exiled angels living among humans.", 720, "Rina Caldwell", 889),
        ("The Paper Town", "Cities made of lies crumble.", "A mysterious town built on deception, and one journalist's quest for the truth.", 630, "Amir Sohail", 420),
        ("Ashes & Stardust", "From ashes, we rise to stars.", "An epic saga tracing a family’s journey from ruin to cosmic explorers.", 1200, "Claire Demarco", 150),
        ("The Forgotten Verse", "Some poems are better left unread.", "A literary mystery surrounding a lost poem with fatal consequences.", 480, "Yusuf Rahman", 365),
        ("Midnight Chronicles", "At midnight, the world changes.", "A horror anthology featuring chilling tales occurring precisely at midnight.", 560, "Jason Crowe", 700),
        ("Skies of Cyan", "Hope is a color we paint ourselves.", "A war pilot’s memoir of courage, betrayal, and redemption.", 900, "Hana Lee", 990),
        ("Wired Souls", "Humanity's final upload awaits.", "A cyberpunk novel where consciousness can be digitized — for a price.", 1100, "Marcus Wills", 420),
        ("A Memory of Waves", "Time forgets. Water remembers.", "A coastal village cursed by ancient sea spirits.", 640, "Mina Iqbal", 310),
        ("Concrete Dreams", "Cities grow, but people decay.", "Urban drama of four friends chasing success in a ruthless metropolis.", 770, "Sarah Linton", 505),
        ("The Red Widow", "Her love was death itself.", "A gothic romance about a widow suspected of witchcraft.", 550, "Eleanor Nash", 295),
        ("Orbit Zero", "First contact was never peaceful.", "An interplanetary war saga beginning at Earth's orbit.", 880, "Rico Zhang", 612),
        ("The Last Psalm", "Final words matter most.", "A dying priest’s confessions uncover a town’s darkest sins.", 460, "Father Thomas Grey", 278),
        ("Wanderlust Diaries", "Some journeys never end.", "A travel memoir crossing 30 countries and three continents.", 800, "Aliyah Grant", 900),
        ("The Serpent’s Pact", "Trust the untrustworthy.", "A political fantasy where betrayal is the only currency.", 950, "Neil Adarsh", 345),
        ("Chronicles of Ember", "Fire is both destroyer and savior.", "Post-apocalyptic survival in a world scorched by eternal wildfires.", 990, "Carla Moreno", 489),
        ("The Dying Code", "The last virus holds the cure.", "A biotech thriller about a computer virus engineered to save humanity.", 1020, "Sahil Murthy", 1032)
    ]

    for name, quotes, desc, price, author, views in sample_books:
        Book.objects.create(
            name=name,
            quotes=quotes,
            desc=desc,
            price=price,
            author=author,
            views=views
        )

    return JsonResponse({'status': 'saved'})