from django.shortcuts import render, HttpResponse, HttpResponseRedirect, reverse, get_list_or_404
from users.models import VerifiedUser
from .models import Image, Tag
from django.core.exceptions import ObjectDoesNotExist
import boto3
import zipfile
import os
import time
import datetime


def index(request):
    if request.user.is_authenticated:
        try:
            print(VerifiedUser.objects.get(user=request.user, verified=True))
        except ObjectDoesNotExist:
            return HttpResponseRedirect(reverse("login", kwargs={"extra_context": "Your account needs to be verified by"
                                                                                  " an admin before you can continue."}))
        else:
            return render(request, "image_search/index.html", {'username': request.user.username})
    else:
        return HttpResponseRedirect(reverse("login"))


def search(request):
    if request.user.is_authenticated:
        try:
            print(VerifiedUser.objects.get(user=request.user, verified=True))
        except ObjectDoesNotExist:
            return HttpResponseRedirect(reverse("login", kwargs={"extra_context": "Your account needs to be verified by"
                                                                                  " an admin before you can continue."}))
        else:
            return render(request, "image_search/search.html", {"tags": Tag.objects.all(), 'username': request.user.username})
    else:
        return HttpResponseRedirect(reverse("login"))


def upload(request):
    if request.user.is_authenticated:
        try:
            print(VerifiedUser.objects.get(user=request.user, verified=True))
        except ObjectDoesNotExist:
            return HttpResponseRedirect(reverse("login", kwargs={"extra_context": "Your account needs to be verified by"
                                                                                  " an admin before you can continue."}))
        else:
            return render(request, "image_search/upload.html", {"tags": Tag.objects.all(), 'username': request.user.username})
    else:
        return HttpResponseRedirect(reverse("login"))


def add_tag(request):
    if request.user.is_authenticated:
        try:
            print(VerifiedUser.objects.get(user=request.user, verified=True))
        except ObjectDoesNotExist:
            return HttpResponseRedirect(reverse("login", kwargs={"extra_context": "Your account needs to be verified by"
                                                                                  " an admin before you can continue."}))
        else:
            return render(request, "image_search/add_tag.html", {'username': request.user.username})
    else:
        return HttpResponseRedirect(reverse("login"))


def view(request, image_ids):
    if request.user.is_authenticated:
        try:
            print(VerifiedUser.objects.get(user=request.user, verified=True))
        except ObjectDoesNotExist:
            return HttpResponseRedirect(reverse("login", kwargs={"extra_context": "Your account needs to be verified by"
                                                                                  " an admin before you can continue"}))
        else:
            try:
                image_ids = image_ids.split(",")
            except ValueError:
                image_ids = [image_ids]

            images = Image.objects.filter(pk__in=image_ids)
            print(images)
            for image in images:
                print(image.s3_url)
            return render(request, "image_search/view.html", {"images": images, 'username': request.user.username})
    else:
        return HttpResponseRedirect(reverse("login"))


def result(request, result_text):
    return render(request, "image_search/result.html", {"result_text": result_text, 'username': request.user.username})


def search_processing(request):
    print("=" * 100)
    images = Image.objects.all()
    print(f"Selected tags: {request.POST.getlist('tag_select')}")

    for tag_name in request.POST.getlist('tag_select'):
        images = images.filter(tags__name=tag_name)
    print(f"Images to display: {images}")

    if len(images) == 0:
        return HttpResponseRedirect(reverse("result", kwargs={"result_text": "No images found",
                                                              'username': request.user.username}))
    else:

        image_ids = ",".join([str(image.id) for image in images])

        print(f"Display image(s) id(s): {image_ids}")
        print("=" * 100)

        return HttpResponseRedirect(reverse("view", kwargs={"image_ids": image_ids}))


def upload_processing(request):
    print("=" * 100)
    print(request.POST)
    print(request.FILES["image"], type(request.FILES["image"]), str(request.FILES["image"]))
    try:
        if request.FILES["image"].name.endswith(".zip"):
            with zipfile.ZipFile(request.FILES["image"], "r") as zipped_images:
                zipped_images.extractall("temp_images")
            if len(os.listdir("temp_images")) == 1:
                for file in os.listdir(f"temp_images/{os.listdir('temp_images')[0]}"):
                    with open(f"temp_images/{os.listdir('temp_images')[0]}/{file}", "rb") as unzipped_image:
                        tags = Tag.objects.filter(name__in=request.POST.getlist("tag_add"))
                        image = Image()
                        image.save()
                        for tag in tags:
                            image.tags.add(tag)
                            image.save()

                        image.name = f"IMG-{str(datetime.datetime.now()).replace(':', '-').replace(' ', '--').replace('.', '-')}"
                        image.save()

                        image.s3_url = upload_aws_s3("boto3-nick-test", unzipped_image, image.name)
                        image.save()

                        print(image.name, image.s3_url)
                        os.remove(f"temp_images/{os.listdir('temp_images')[0]}/{file}")
                        time.sleep(0.5)

                os.rmdir(f"temp_images/{os.listdir('temp_images')[0]}")
                print("=" * 100)

            elif len(os.listdir("temp_images")) > 1:
                for file in os.listdir("temp_images"):
                    with open(f"temp_images/{file}", "rb") as unzipped_image:
                        tags = Tag.objects.filter(name__in=request.POST.getlist("tag_add"))
                        image = Image()
                        image.save()
                        for tag in tags:
                            image.tags.add(tag)
                            image.save()

                        image.name = f"IMG-{str(datetime.datetime.now()).replace(':', '-').replace(' ', '--').replace('.', '-')}"
                        image.save()

                        image.s3_url = upload_aws_s3("boto3-nick-test", unzipped_image, image.name)
                        image.save()

                        print(image.name, image.s3_url)
                        os.remove(f"temp_images/{file}")
                        time.sleep(0.5)

            return HttpResponseRedirect(reverse("result", kwargs={"result_text": "Images successfully uploaded"}))

        else:
            tags = Tag.objects.filter(name__in=request.POST.getlist("tag_add"))
            image = Image()
            image.save()
            for tag in tags:
                image.tags.add(tag)
                image.save()

            image.name = f"IMG-{str(datetime.datetime.now()).replace(':', '-').replace(' ', '--').replace('.', '-')}"
            image.save()

            image.s3_url = upload_aws_s3("boto3-nick-test", request.FILES["image"], image.name)
            image.save()

            print("=" * 100)
            return HttpResponseRedirect(reverse("result", kwargs={"result_text": "Image successfully uploaded"}))
    except Exception as e:
        print(e)
        return HttpResponseRedirect(reverse("result", kwargs={"result_text": f"Upload Failed"}))


def add_tag_processing(request):
    if len(Tag.objects.filter(name=request.POST["tag_name"])) == 0:
        tag = Tag(name=request.POST["tag_name"])
        tag.save()
        return HttpResponseRedirect(reverse("result", kwargs={"result_text": "Tag successfully created"}))
    else:
        return HttpResponseRedirect(reverse("result", kwargs={"result_text": "Tag name conflicts with other tags"}))


def upload_aws_s3(bucket, file, key):
    aws_client = boto3.client("s3", aws_access_key_id=None, aws_secret_access_key=None)
    aws_client.upload_fileobj(file, bucket, key)
    aws_client.put_object_acl(Bucket=bucket, Key=key, ACL="public-read")
    return f"https://s3.us-east-1.amazonaws.com/{bucket}/{key}"


def create_upload_image_object(request):
    tags = Tag.objects.filter(name__in=request.POST.getlist("tag_add"))
    image = Image()
    image.save()
    for tag in tags:
        image.tags.add(tag)
        image.save()

    image.name = f"IMG-{str(datetime.datetime.now()).replace(':', '-').replace(' ', '--').replace('.', '-')}"
    image.save()

    image.s3_url = upload_aws_s3("boto3-nick-test", request.FILES["image"], image.name)
    image.save()
