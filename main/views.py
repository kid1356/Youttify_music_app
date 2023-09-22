from django.http.response import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .models import playlist_user,Profile
from django.urls.base import reverse
from django.contrib.auth import authenticate,login,logout
from youtube_search import YoutubeSearch
import json
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
import uuid
from django.conf import settings

# import cardupdate
@csrf_exempt
def logIn_view(request):
  if request.method == "POST":
      username = request.POST.get('username')
      password = request.POST.get('password')
      
      if not username or not password:
         messages.info(request,"both username and password are required.")
         return redirect("/login/")
      
      user_obj = User.objects.filter(username = username).first()
      if user_obj is None:
         messages.info(request, "User not found")
         return redirect("/login/")
      
      user = authenticate(request, username=username, password=password)

      if user is None:
          messages.error(request, 'wrong password.')
          return redirect("/login/")
      
      login(request, user)
      return redirect('/home/')

  return render(request , 'login.html')

@csrf_exempt
def register_view(request):
  if request.method == "POST":
      username = request.POST.get('username')
      email = request.POST.get('email')
      password = request.POST.get('password')

      if User.objects.filter(username = username).first():
         messages.warning(request, "username is taken")
         return redirect('/signup/')
      if User.objects.filter(email = email).first():
         messages.info(request, "Email is taken")
         return redirect('/signup/')
      
      user_obj = User(username = username , email = email)
      user_obj.set_password(password)
      user_obj.save()

      profile_obj = Profile.objects.create(user = user_obj)
      profile_obj.save()
      messages.success(request,"Register Successfully.Now LogIn")
      return redirect('/signup/')
  
  return render(request , 'signup.html')

def logoutview(request):
  logout(request)
  return redirect('login')

def send_forget_password_email(email,token):  #generating tokens and sending email
   subject = "Your forget password link."
   message = f'Hi, Click on this link to reset your Password http://127.0.0.1:8000/change-password/{token}/'
   email_from = settings.EMAIL_HOST_USER
   recipient_list = [email]
   send_mail(subject,message, email_from, recipient_list)
   return True


def Forget_password(request):  # forget password view
    if request.method == 'POST': 
      username = request.POST.get('username')
      
      if not User.objects.filter(username = username).first():
         messages.error(request, "No User found")
         return redirect('/forget-password/')
      
      user_obj = User.objects.get(username = username)
      token = str(uuid.uuid4())
      profile_obj = Profile.objects.get(user = user_obj)
      profile_obj.forget_password_token = token
      profile_obj.save()
      send_forget_password_email(user_obj.email,token)
      messages.success(request, "Email is sent.")
      return redirect("/forget-password/")
    
    return render(request, 'forget_password.html')


def changepassword(request, token):  # change password view
   context ={}
   
   profile_obj = Profile.objects.filter(forget_password_token = token).first()
   context = {'user_id' : profile_obj.user.id}

   if request.method == "POST":
      new_password = request.POST.get('new_password')
      confirm_password = request.POST.get('confirm_password')
      user_id = request.POST.get('user_id')

      if user_id is None:
         messages.error(request,'No User is found with this username')
         return redirect(f'/change-password/{token}/')
      
      if new_password != confirm_password:
         messages.info(request, "Both Password should be equal")
         return redirect(f'/change-password/{token}/')

      user_obj = User.objects.get(id = user_id)
      user_obj.set_password(new_password)
      user_obj.save()
      return redirect('/login/')

   
   return render(request, 'change_password.html', context)   


f = open('card.json', 'r')
CONTAINER = json.load(f)

@login_required(login_url='/login/')
def default(request):
    global CONTAINER


    if request.method == 'POST':

        add_playlist(request)
        return HttpResponse("")
    
    song = 'kSFJGEHDCrQ'
    return render(request, 'player.html',{'CONTAINER':CONTAINER, 'song':song})



def playlist(request):
    cur_user = playlist_user.objects.get(username = request.user)
    try:
      song = request.GET.get('song')
      song = cur_user.playlist_song_set.get(song_title=song)
      song.delete()
    except:
      pass
    if request.method == 'POST':
        add_playlist(request)
        return HttpResponse("")
    song = 'kSFJGEHDCrQ'
    user_playlist = cur_user.playlist_song_set.all()
    # print(list(playlist_row)[0].song_title)
    return render(request, 'playlist.html', {'song':song,'user_playlist':user_playlist})


def search(request):
  if request.method == 'POST':

    add_playlist(request)
    return HttpResponse("")
  try:
    search = request.GET.get('search')
    song = YoutubeSearch(search, max_results=10).to_dict()
    song_li = [song[:10:2],song[1:10:2]]
    # print(song_li)
  except:
    return redirect('/')

  return render(request, 'search.html', {'CONTAINER': song_li, 'song':song_li[0][0]['id']})




def add_playlist(request):
    cur_user = playlist_user.objects.get(username = request.user)

    if (request.POST['title'],) not in cur_user.playlist_song_set.values_list('song_title', ):

        songdic = (YoutubeSearch(request.POST['title'], max_results=1).to_dict())[0]
        song__albumsrc=songdic['thumbnails'][0]
        cur_user.playlist_song_set.create(song_title=request.POST['title'],song_dur=request.POST['duration'],
        song_albumsrc = song__albumsrc,
        song_channel=request.POST['channel'], song_date_added=request.POST['date'],song_youtube_id=request.POST['songid'])
