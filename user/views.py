from django.shortcuts import render, redirect, get_object_or_404
from .models import Profile
# from feed.models import Post
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.conf import settings
from django.http import HttpResponseRedirect
from .models import Profile, FriendRequest
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm
import random


# Create your views here.
User = get_user_model()

@login_required
def users_list(request):
    users = Profile.objects.exclude(user=request.user)
    sent_friend_requests = FriendRequest.objects.filter(from_user=request.user)
    sent_to = []
    friends = []
    for user in users:
        friend = user.friends.all()
        for f in friend:
            if f in friends:
                friend = friend.exclude(user=f.user)
        friends += friend
    
    my_friends = request.user.profile.friends.all()

    for i in my_friends:
        if i in friends:
            friends.remove(i)
    if request.user.profile in friends:
        friends.remove(request.user.profile)

    random_list = random.sample(list(users), min(len(list(users)), 10))
    for r in random_list:
        if r in friends:
            random_list.remove(r)
    friends+=random_list
    
    for i in my_friends:
        if i in friends:
            friends.remove(i)
    
    for se in sent_friend_requests:
        sent_to.append(se.to_user)

    context = {
        'users': friends,
        'sent' : sent_to
    }

    return render(request,"users/users_list.html",context)


def friend_list(request):
    p = request.user.profile
    friends = p.friends.all()
    context = {
        'friends':friends
    }
    return render(request, "users/friend_list.html",context)

@login_required
def send_friend_request(request,id):
    user = get_object_or_404(User,id=id)
    f_request, created = FriendRequest.objects.get_or_create(
        from_user=request.user,
        to_user=user
    )
    return HttpResponseRedirect('/users/{}'.format(user.profile.slug))

@login_required
def cancel_friend_request(request,id):
    user = get_object_or_404(User,id=id)
    f_request = FriendRequest.objects.filter(
        from_user=request.user,
        to_user=user
    ).first()
    f_request.delete()
    return HttpResponseRedirect('/users/{}'.format(user.profile.slug))

@login_required
def accept_friend_request(request,id):
    from_user = get_object_or_404(User,id=id)
    f_request = FriendRequest.objects.filter(
        from_user=from_user,
        to_user=request.user
        ).first()
    user_1 = f_request.to_user
    user_2 = from_user
    user_1.profile.friends.add(user_2.profile)
    user_2.profile.friends.add(user_1.profile)
    if (FriendRequest.objects.filter(from_user=request.user,to_user=from_user).first()):
        request_rev = FriendRequest.objects.filter(from_user=request.user,to_user=from_user)
        request_rev.delete()
    f_request.delete()
    return HttpResponseRedirect('/users/{}'.format(request.user.profile.slug))

@login_required
def delete_friend_request(request,id):
    from_user = get_object_or_404(User,id=id)
    f_request = FriendRequest.objects.filter(from_user=from_user,to_user=request.user).first()
    f_request.delete()
    return HttpResponseRedirect('/users/{}'.format(request.user.profile.slug))

def delete_friend(request, id):
    user_profile = request.user.profile
    friend_profile = get_object_or_404(Profile,id=id)
    user_profile.friends.remove(friend_profile)
    friend_profile.friends.remove(user_profile)
    return HttpResponseRedirect('/users/{}'.format(friend_profile.slug))

@login_required
def profile_view(request,slug):
    profile = Profile.objects.filter(slug=slug).first()
    user = profile.user
    sent_friend_requests = FriendRequest.objects.filter(from_user = user)
    rec_friend_requests = FriendRequest.objects.filter(to_user = user)
    user_posts = Post.objects.filter(user_name=user)

    friends = profile.friends.all()

    # es este usuario dentro de amigos
    button_status = 'none'

    if p not in request.user.profile.friends.all():
        button_status='not_friend'

        # si ya hemos enviado la solicitud
        if len(FriendRequest.objects.filter(from_user=request.user).filter(to_user=user)) == 1:
            button_status = 'friend_request_sent'

        # Si hemos recibido solicitud de amistad
        if len(FriendRequest.objects.filter(from_user=user).filter(to_user=request.user))==1:
            button_status="friend_request_received"

    context = {
        'u':user,
        'button_status':button_status,
        'friens_list':friends,
        'sent_friend_requests':rec_friend_requests,
        'post_count':user_posts.count
    }

    return render(request,"users/profile.html",context)
