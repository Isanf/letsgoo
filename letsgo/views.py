from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.urls import reverse_lazy, reverse
from django.contrib.auth.models import User
from .models import VideoPost, Comment, UserData, StepPost, Category, AccessTuto, Purchage
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
import datetime
from datetime import timedelta
from django.db.models import Sum


#purchage_page***********************************************************************************************************************
def purchage_page(request):
    if request.user.is_authenticated:
        user_obj = User.objects.get(username=request.user.username)
        counter = Purchage.objects.filter(customer=user_obj, pack__gt=0).aggregate(Sum('pack'))['pack__sum']
        params = {'counter':counter}
        return render(request, 'pay.html', params)
    else:
        messages.warning(request, 'You are not login.')
        messages.warning(request, 'Vous n\'êtes pas connecté.')
        return render(request, 'pay.html')

#purchage***********************************************************************************************************************
def purchage(request):
    try:
        user_obj = User.objects.get(username=request.user.username)
    except ObjectDoesNotExist:
        return render(request, '404.html')
    if request.method == 'GET':
        purchage_obj = Purchage.objects.create(customer=user_obj, pack=5, activated = True)
        purchage_obj.save()
        messages.success(request, 'Payment done. Paiement réussi :) ')
        return render(request, 'home.html')
    else:
        user_obj = User.objects.get(username=request.user.username)
        counter = Purchage.objects.filter(customer=user_obj, pack__gt=0).aggregate(Sum('pack'))['pack__sum']
        params = {'counter':counter}
        return redirect(request, 'pay.html', params)




#****************************Here The indentation logic was strange***This_function_is more than I estimated************************************************************
#verifyAccess***********************************************************************************************************************************************************
def verify_access(request, creator_id, video_id, step_id):
    try:
        session_obj = User.objects.get(username=request.user.username)
    except:
        messages.warning(request, 'You are not login.')
        messages.warning(request, 'Vous n\'êtes pas connecté.')
        return redirect('home')
    try:
        video_obj = VideoPost.objects.get(id=video_id)
    except ObjectDoesNotExist:
        return render(request, '404.html')
    try:
        if step_id == 1:
            step_obj = StepPost.objects.filter(post=video_obj).first()
        else:
            step_obj = StepPost.objects.get(id=step_id, post=video_obj)
    except ObjectDoesNotExist:
        return render(request, '404.html')


    video_comments = Comment.objects.filter(post=video_obj).order_by('-id')

    video_steps = StepPost.objects.filter(post=video_obj).order_by('id')

    # Increase Views of Video if User visit this page
    if request.user not in video_obj.video_views.all():
        video_obj.video_views.add(request.user)

    # Increase Likes of Video if User like this video
    is_liked = False
    if session_obj in video_obj.likes.all():
        is_liked = True
    else:
        is_liked = False
    params = {'video':video_obj, 'step':step_obj, 'comments': video_comments, 'steps': video_steps, 'is_liked':is_liked}

    creator_obj = User.objects.get(id=creator_id)

    try:
        purchage_obj = Purchage.objects.filter(customer=session_obj, pack__gt=0).first()
    except:
        return render(request, '404.html')
    if purchage_obj:
        try:
            accessTuto_list = AccessTuto.objects.filter(customer=session_obj, creator=creator_obj)
        except:
            return render(request, '404.html')
        if accessTuto_list:
            for accessTuto_obj in accessTuto_list:
                start = accessTuto_obj.access_date
                end = datetime.date.today()
                delta = datetime.timedelta(days=1)
                counter = 0

                while start <= end:
                    counter += 1
                    start += delta
                if counter <= 30:
                    return render(request, 'watch_step.html', params)
                else:
                    access_tuto_obj = AccessTuto.objects.create(customer=session_obj, creator=creator_obj)
                    access_tuto_obj.save()
                    decrement = purchage_obj.pack - 1
                    purchage_obj.pack = decrement
                    purchage_obj.save()
                    return render(request, 'watch_step.html', params)
        else:
            access_tuto_obj = AccessTuto.objects.create(customer=session_obj, creator=creator_obj)
            access_tuto_obj.save()
            decrement = purchage_obj.pack - 1
            purchage_obj.pack = decrement
            purchage_obj.save()
            return render(request, 'watch_step.html', params)
    else:
        return redirect('nav')






def search(request):
    query = request.GET['search_query']
    try:
        user_obj = User.objects.filter(username__icontains=query)
    except:
        user_obj = User.objects.none()
    params = {'user_obj': user_obj}

    return render(request, 'search_page.html', params)


#FindVideo****************************************************************************************************************************
def search_video(request):
    query = request.GET['search_video']
    try:
        video_obj = VideoPost.objects.filter(title__icontains=query)
    except:
        video_obj = VideoPost.objects.none()
    params = {'video_obj': video_obj}

    return render(request, 'search_video.html', params)


#list_categories*********************************************************************************************************************
def list_categories(request):
    if not request.user.is_authenticated:
        messages.warning(request, 'vous n\'êtes pas connecté!')
        return render(request, 'home.html')
    else:
        categories = Category.objects.all().order_by('id')
        params = {'categories': categories}
        return render(request, 'list_categories.html', params)


#delete_categ************************************************************************************************************************
def delete_categ(request):
    if request.method == 'GET':
        category = request.GET['categId']
        category_obj = Category.objects.get(id=category)
        category_obj.delete()
        return render(request, 'list_categories.html')
    else:
        return JsonResponse({'status': 'not ok'})


#add_category************************************************************************************************************************
def add_category(request):
    if request.method == 'POST':
        title = request.POST['title']
        thumb_nail = request.FILES['thumbnail_img']
        add_category = Category( title=title, thumbnail=thumb_nail)
        add_category.save()
        messages.success(request, 'Category '+str(title)+' has been uploaded.')
        messages.success(request, 'La catégorie '+str(title)+' a été téléchargée.')

    return render(request, 'add_category.html')



#upload_video***********************************************************************************************************************
def upload_video(request):
    if request.method == 'POST':
        title = request.POST['title']
        desc = request.POST['desc']
        video_file = request.FILES['fileName']
        thumb_nail = request.FILES['thumbnail_img']
        cate = request.POST['category']
        user_obj = User.objects.get(username=request.user)
        upload_video = VideoPost(user=user_obj, category=cate, title=title, desc=desc, video_file=video_file, thumbnail=thumb_nail)
        upload_video.save()
        messages.success(request, 'Video has been uploaded. Now add short videos in steps explaining how to get the performences demontrated in the uploaded video:)')
        messages.success(request, 'La vidéo a été téléchargée. Ajoutez maintenant de courtes vidéos par étapes expliquant comment obtenir les performances démontrées dans la vidéo téléchargée :)')
        params = {'video':upload_video}
        return render(request, 'upload_step.html', params)

    categories = Category.objects.all()
    params = {'categories':categories}
    return render(request, 'upload.html', params)




#Stepper***********************************************************************************************************************
def upload_step(request,  video_id):
    if request.method == 'POST':
        title = request.POST['title']
        desc = request.POST['desc']
        video_file = request.FILES['fileName']
        user_obj = User.objects.get(username=request.user)
        video_obj = VideoPost.objects.get(id=video_id)
        upload_step = StepPost(user=user_obj, post=video_obj, title=title, desc=desc, video_file=video_file)
        upload_step.save()
        video_steps = StepPost.objects.filter(post=video_obj).order_by('id')
        messages.success(request, 'Video Step '+str(video_steps.count())+' has been uploaded:)')
        messages.success(request, 'L\'étape '+str(video_steps.count())+' de la video a été enregistré:)')
        stepsnext = video_steps.count() + 1
        params = {'video':video_obj, 'stepsnext':stepsnext}
        return render(request, 'upload_step.html', params)

    return render(request, 'upload.html')


#videos_bycatego********************************************************************************************************************************
def videos_bycatego(request, category_title):
    if not request.user.is_authenticated:
        messages.warning(request, 'You are not login to watch this video.')
        messages.warning(request, 'Vous n\'êtes pas connecté pour regarder cette vidéo.')
        return redirect('home')
    else:
        session_obj = User.objects.get(username=request.user.username)
        all_videos = VideoPost.objects.filter(category=category_title).order_by('-id')
        categories = Category.objects.all().order_by('id')
        counter = Purchage.objects.filter(customer=session_obj, pack__gt=0).aggregate(Sum('pack'))['pack__sum']
        params = {'all_videos': all_videos, 'categories': categories, 'counter':counter}
        return render(request, 'filter.html', params)


def home(request):
    if not request.user.is_authenticated:
        demo_videos = VideoPost.objects.all().order_by('-id')[:5]
        categories = Category.objects.all().order_by('id')
        params = {'videos': demo_videos, 'categories': categories}
        return render(request, 'welcome.html', params)
    else:
        session_obj = User.objects.get(username=request.user.username)
        all_videos = VideoPost.objects.all().order_by('-id')
        categories = Category.objects.all().order_by('id')
        counter = Purchage.objects.filter(customer=session_obj, pack__gt=0).aggregate(Sum('pack'))['pack__sum']
        params = {'all_videos': all_videos, 'categories': categories, 'counter':counter}
        return render(request, 'home.html', params)

#watch_video*************************************************************************************************************************
def watch_video(request, video_id):
    try:
        video_obj = VideoPost.objects.get(id=video_id)
    except ObjectDoesNotExist:
        return render(request, '404.html')
    try:
        session_obj = User.objects.get(username=request.user.username)
    except:
        messages.warning(request, 'You are not login to watch this video.')
        messages.warning(request, 'Vous n\'êtes pas connecté pour regarder cette vidéo.')
        return redirect('home')

    video_comments = Comment.objects.filter(post=video_obj).order_by('-id')

    video_steps = StepPost.objects.filter(post=video_obj).order_by('id')


    # Increase Views of Video if User visit this page

    if request.user not in video_obj.video_views.all():
        video_obj.video_views.add(request.user)

    # Increase Likes of Video if User like this video

    is_liked = False
    if session_obj in video_obj.likes.all():
        is_liked = True
    else:
        is_liked = False
    counter = Purchage.objects.filter(customer=session_obj, pack__gt=0).aggregate(Sum('pack'))['pack__sum']
    params = {'video':video_obj, 'video_id':video_id, 'comments': video_comments, 'steps': video_steps, 'is_liked':is_liked, 'counter':counter}
    return render(request, 'watch_video.html', params)


#watch_next_video*******************************************************************************************************************************
def watch_next_video(request, video_id):
    session_obj = User.objects.get(username=request.user.username)
    video_obj = VideoPost.objects.filter(id__lt=video_id).order_by('id').first()
    if video_obj is None:
        video_obj = VideoPost.objects.first()

    video_comments = Comment.objects.filter(post=video_obj).order_by('-id')
    video_steps = StepPost.objects.filter(post=video_obj).order_by('id')

     # Increase Views of Video if User visit this page

    if request.user not in video_obj.video_views.all():
        video_obj.video_views.add(request.user)



    # Increase Likes of Video if User like this video

    is_liked = False
    if session_obj in video_obj.likes.all():
         is_liked = True
    else:
         is_liked = False

    counter = Purchage.objects.filter(customer=session_obj, pack__gt=0).aggregate(Sum('pack'))['pack__sum']

    params = {'video':video_obj, 'video_id':video_id, 'comments': video_comments, 'steps': video_steps, 'is_liked':is_liked, 'counter':counter}
    return render(request, 'watch_video.html', params)


#watch_prev_video**********************************************************************************************************************************
def watch_prev_video(request, video_id):
    session_obj = User.objects.get(username=request.user.username)
    video_obj = VideoPost.objects.filter(id__gt=video_id).order_by('id').first()
    if video_obj is None:
        video_obj = VideoPost.objects.last()

    video_comments = Comment.objects.filter(post=video_obj).order_by('-id')

    video_steps = StepPost.objects.filter(post=video_obj).order_by('id')
    video_comments = Comment.objects.filter(post=video_obj).order_by('-id')

    video_steps = StepPost.objects.filter(post=video_obj).order_by('id')


     # Increase Views of Video if User visit this page

    if request.user not in video_obj.video_views.all():
        video_obj.video_views.add(request.user)



    # Increase Likes of Video if User like this video

    is_liked = False
    if session_obj in video_obj.likes.all():
         is_liked = True
    else:
         is_liked = False

    counter = Purchage.objects.filter(customer=session_obj, pack__gt=0).aggregate(Sum('pack'))['pack__sum']

    params = {'video':video_obj, 'video_id':video_id, 'comments': video_comments, 'steps': video_steps, 'is_liked':is_liked, 'counter':counter}
    return render(request, 'watch_video.html', params)


#watch_step**************************************************************************************************************************
def watch_step(request, video_id, step_id):
    try:
        video_obj = VideoPost.objects.get(id=video_id)
    except ObjectDoesNotExist:
        return render(request, '404.html')
    try:
        if step_id == 1:
            step_obj = StepPost.objects.filter(post=video_obj).first()
        else:
            step_obj = StepPost.objects.get(id=step_id, post=video_obj)
    except ObjectDoesNotExist:
        return render(request, '404.html')
    try:
        session_obj = User.objects.get(username=request.user.username)
    except:
        messages.warning(request, 'You are not login to watch this video.')
        messages.warning(request, 'Vous n\'êtes pas connecté pour regarder cette vidéo.')
        return redirect('home')

    video_comments = Comment.objects.filter(post=video_obj).order_by('-id')

    video_steps = StepPost.objects.filter(post=video_obj).order_by('id')


    # Increase Views of Video if User visit this page

    if request.user not in video_obj.video_views.all():
        video_obj.video_views.add(request.user)



    # Increase Likes of Video if User like this video

    is_liked = False
    if session_obj in video_obj.likes.all():
        is_liked = True
    else:
        is_liked = False
    params = {'video':video_obj, 'step':step_obj, 'comments': video_comments, 'steps': video_steps, 'is_liked':is_liked}
    return render(request, 'watch_step.html', params)

#watch_next_step**************************************************************************************************************************
def watch_next_step(request, video_id, step_id):
    try:
        video_obj = VideoPost.objects.get(id=video_id)
    except ObjectDoesNotExist:
        return render(request, '404.html')
    try:
        stepid = step_id + 1
        step_obj = StepPost.objects.get(id=stepid, post=video_obj)
    except ObjectDoesNotExist:
        step_obj = StepPost.objects.get(id=step_id, post=video_obj)
        messages.success(request, 'End Tuto. Fin Tuto.')
    try:
        session_obj = User.objects.get(username=request.user.username)
    except:
        messages.warning(request, 'You are not login to watch this video.')
        messages.warning(request, 'Vous n\'êtes pas connecté pour regarder cette vidéo.')
        return redirect('home')

    video_comments = Comment.objects.filter(post=video_obj).order_by('-id')

    video_steps = StepPost.objects.filter(post=video_obj).order_by('id')


    # Increase Views of Video if User visit this page

    if request.user not in video_obj.video_views.all():
        video_obj.video_views.add(request.user)



    # Increase Likes of Video if User like this video

    is_liked = False
    if session_obj in video_obj.likes.all():
        is_liked = True
    else:
        is_liked = False
    counter = Purchage.objects.filter(customer=session_obj, pack__gt=0).aggregate(Sum('pack'))['pack__sum']
    params = {'video':video_obj, 'step':step_obj, 'comments': video_comments, 'steps': video_steps, 'is_liked':is_liked, 'counter':counter}
    return render(request, 'watch_step.html', params)

#watch_prec_step**************************************************************************************************************************
def watch_prec_step(request, video_id, step_id):
    try:
        video_obj = VideoPost.objects.get(id=video_id)
    except ObjectDoesNotExist:
        return render(request, '404.html')
    try:
        stepid = step_id - 1
        step_obj = StepPost.objects.get(id=stepid, post=video_obj)
    except ObjectDoesNotExist:
        step_obj = StepPost.objects.get(id=step_id, post=video_obj)
        messages.success(request, 'Start Tuto. Debut Tuto.')
    try:
        session_obj = User.objects.get(username=request.user.username)
    except:
        messages.warning(request, 'You are not login to watch this video.')
        messages.warning(request, 'Vous n\'êtes pas connecté pour regarder cette vidéo.')
        return redirect('home')

    video_comments = Comment.objects.filter(post=video_obj).order_by('-id')

    video_steps = StepPost.objects.filter(post=video_obj).order_by('id')


    # Increase Views of Video if User visit this page

    if request.user not in video_obj.video_views.all():
        video_obj.video_views.add(request.user)



    # Increase Likes of Video if User like this video

    is_liked = False
    if session_obj in video_obj.likes.all():
        is_liked = True
    else:
        is_liked = False
    counter = Purchage.objects.filter(customer=session_obj, pack__gt=0).aggregate(Sum('pack'))['pack__sum']
    params = {'video':video_obj, 'step':step_obj, 'comments': video_comments, 'steps': video_steps, 'is_liked':is_liked, 'counter':counter}
    return render(request, 'watch_step.html', params)



def add_comment(request):
    if request.method == 'GET':
        video_id = request.GET['video_id']
        comment = request.GET['comment_text']
        video_obj = VideoPost.objects.get(id=video_id)
        session_obj = User.objects.get(username=request.user.username)
        video_comments = Comment.objects.filter(post=video_obj).order_by('-id')
        create_comment = Comment.objects.create(post=video_obj, user=session_obj, comment=comment)
        create_comment.save()

    return JsonResponse({'comment':create_comment.comment, 'count_comments':video_comments.count()})




def add_like(request, video_id):
    user_obj = User.objects.get(username=request.user.username)
    video_obj = VideoPost.objects.get(id=video_id)
    is_liked = False
    if user_obj in video_obj.likes.all():
        video_obj.likes.remove(user_obj)
        is_liked = True
    else:
        video_obj.likes.add(user_obj)
        is_liked = False
    return JsonResponse({'is_liked':is_liked,'likes_count':video_obj.likes.all().count()})




def profile(request, session_username):
    try:
        session_obj = User.objects.get(username=session_username)
    except ObjectDoesNotExist:
        return render(request, '404.html')
    profile_data = UserData.objects.get_or_create(user=session_obj)[0]
    user_posts = VideoPost.objects.filter(user=session_obj).order_by('-id')


    # Category wise Posts

    video_cat_science = VideoPost.objects.filter(user=session_obj, category='Science & Techanology').order_by('-id')
    video_cat_blogs = VideoPost.objects.filter(user=session_obj, category='Blogs').order_by('-id')
    video_cat_fashion = VideoPost.objects.filter(user=session_obj, category='Fashion').order_by('-id')
    video_cat_education = VideoPost.objects.filter(user=session_obj, category='Education').order_by('-id')
    video_cat_food = VideoPost.objects.filter(user=session_obj, category='Food').order_by('-id')

    subscribed = False
    if request.user in profile_data.subscribers.all():
        subscribed = True
    else:
        subscribed = False
    params = {'subscribed':subscribed,'session_obj':session_obj,'user_data':profile_data, 'videos': user_posts, 'sci': video_cat_science, 'blogs': video_cat_blogs, 'fashion': video_cat_fashion, 'edu':video_cat_education, 'food': video_cat_food}
    return render(request, 'profile.html', params)

def dashboard(request, session_username):
    
    if not session_username:
        return redirect('home')

    user_videos = VideoPost.objects.filter(user__username=request.user.username).order_by('-id')
    user_data = UserData.objects.get_or_create(user=User.objects.get(username=request.user.username))[0]
    user_video_likes = 0
    user_videos_views = 0

    for video in user_videos:
        user_video_likes += video.likes.count()
        user_videos_views += video.video_views.count()


    params = {'videos': user_videos, 'user_data': user_data, 'total_likes':user_video_likes, 'total_views': user_videos_views}
    return render(request, 'dashboard.html', params)


def add_sub(request, viewer):
    viewer_obj = UserData.objects.get_or_create(user=User.objects.get(username=viewer))[0]
    subscriber_obj = User.objects.get(username=request.user.username)

    subscribed = False
    if subscriber_obj in viewer_obj.subscribers.all():
        viewer_obj.subscribers.remove(subscriber_obj)
        subscribed = True
    else:
        viewer_obj.subscribers.add(subscriber_obj)
        subscribed = False

    return JsonResponse({'is_subscribed': subscribed, 'viewer_obj':viewer_obj.subscribers.all().count()})



def edit_video(request, video_id):
    if request.method == 'POST':
        new_title = request.POST['new_title']
        new_desc = request.POST['new_desc']
        new_cate = request.POST['new_cate']

        video_obj = VideoPost.objects.get(id=video_id)
        video_obj.title = new_title
        video_obj.desc = new_desc
        video_obj.category = new_cate
        video_obj.save()

        return HttpResponseRedirect(reverse('dashboard', args=[str(request.user.username)]))
    else:
        return HttpResponse('get')




def update_details(request):
    if request.method == 'POST':
        user_data = UserData.objects.get(user=request.user)

        aboutText = request.POST['about_text']
        try:
            imgFile = request.FILES['img_field']
            if imgFile:
                user_data.profile_pic = imgFile

        except:
            print('some error occured')


        user_data.about = aboutText
        user_data.save()

        return HttpResponseRedirect(reverse('dashboard', args=[str(request.user.username)]))
    return redirect('dashboard')



def delete_video(request):
    if request.method == 'GET':
        vid = request.GET['videoId']
        video_obj = VideoPost.objects.get(id=vid)
        video_obj.delete()

        user_videos = VideoPost.objects.filter(user__username=request.user.username)
        user_video_likes = 0
        for video in user_videos:
            user_video_likes += video.likes.count()
        return JsonResponse({'video_id': vid, 'videosCount': user_videos.count(), 'videosLikes': user_video_likes})
    else:
        return JsonResponse({'status': 'not ok'})




def signup(request):
    if request.method == 'POST':
        #first_name = request.POST['fname']
        last_name = request.POST['lname']
        mail = request.POST['emailOrPhone']
        pwd = request.POST['pwd']

        if User.objects.filter(username=mail):
            messages.warning(request, 'User name exist, change username!')
            messages.warning(request, 'Le nom d\'utilisateur existe, changez de nom d\'utilisateur !')
        else:
            new_user = User.objects.create_user(mail, mail, pwd)
            #new_user.first_name = first_name
            new_user.last_name = last_name
            new_user.save()
            messages.success(request, 'Account has been created successfully.')
    return redirect('home')


def user_login(request):
    if not request.user.is_authenticated:

        if request.method == 'POST':
            uname = request.POST['emailOrPhone2']
            pwd = request.POST['pwd']

            check_user = authenticate(username = uname.lower(), password = pwd)
            if check_user is not None:
                login(request, check_user)
                return redirect('home')
            else:
                messages.warning(request, 'Invalid Username or Password.')
                return redirect('home')
        return redirect('home')

    else:
        return redirect('home')



def user_logout(request):
    logout(request)
    return redirect('home')
