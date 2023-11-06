from django.shortcuts import render
from .models import *
from .serializers import * 

from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.models import User

from rest_framework.decorators import api_view,permission_classes,authentication_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated,AllowAny,IsAdminUser
from rest_framework.generics import ListAPIView,ListCreateAPIView,RetrieveUpdateDestroyAPIView
from rest_framework import permissions
from rest_framework.authentication import TokenAuthentication,SessionAuthentication
from .permission import IsSuperuserOrOwner 
from django.core.mail import send_mail
from django.db.models import Q

@api_view(['GET'])
@permission_classes([IsAdminUser])
def msg(request):
    return Response({"message":"this is a message"})




class RegisterAPI(APIView):
    def post(self, request):
        # import pdb
        # pdb.set_trace()

        data = request.data
        serializer = RegisterSerializer(data=data)
        if serializer.is_valid():
            user=serializer.save()
            token=Token.objects.create(user=user)
            return Response({"message": "User Created"})
        return Response(serializer.errors, status=400)
    

class LoginAPI(APIView):

    def post(self,request):
        data = request.data
        serializer = LoginSerializer(data=data)
        if serializer.is_valid():
            user = authenticate(username = serializer.data['username'],password = serializer.data['password'])
            if user:
                token, create = Token.objects.get_or_create(user=user)
                return Response({"message": "Login Successful", 'token': str(token)})
            else:
                return Response({"message": "Login Failed"}, status=401)
        return Response(serializer.errors, status=400)
    

class UserListAPI(ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class SearchAPI(APIView):
    
    permission_classes=[AllowAny]
    def get(self,request):
        search = request.query_params.get('search', '')
        blogs = BlogModel.objects.filter(
            Q(tag__tag__icontains=search) |
            Q(about__icontains=search) |
            Q(title__icontains=search) ).distinct()
        if not request.user.is_superuser:
            blogs = blogs.filter(status__icontains='Approved')
        
        serializer = BlogSerializer(blogs, many=True) 
        return Response(serializer.data)

class Blogs(APIView):

    def get(self, request):
        if request.user.is_superuser:
            blogs = BlogModel.objects.all().distinct()
        else:
            blogs = BlogModel.objects.filter(status__icontains='Approved').distinct()
        serializer = BlogSerializer(blogs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class BlogAPI(APIView):
    
    authentication_classes = [TokenAuthentication]
    permission_classes=[IsAuthenticated]

    def post(self, request):
        data = {
            'title': request.data.get('title'),
            'about': request.data.get('about'),
            'user': request.user.id,
            'tag': request.data.get('tag'),
            'status': "Pending",
        }

        serializer = BlogSerializer(data=data)
        if serializer.is_valid():
            new_blog = serializer.save()

            subject = f'New Blog: {new_blog.title}'
            from_email = "vishvaic001@gmail.com"
            message = (
                f"New blog post: {new_blog.title}\n\n"
                f"Blog Description: {new_blog.about}.\n\n"
                f"Blog Status: {new_blog.status}.\n\n"
                f"From user {request.user}\n\nThe Email of the user is {request.user.email}"
            )

            superuser = User.objects.filter(is_superuser=True).first()
            if superuser:
                receiver = [superuser.email]
                send_mail(subject, message, from_email, receiver)
            else:
                receiver = ['mforspamers@gmail.com']
                send_mail(subject, message, from_email, receiver)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        blog_id = request.data.get('id')
        try:
            blog = BlogModel.objects.get(id=blog_id)

            if blog.user != request.user and not request.user.is_superuser:
                return Response({"detail": "You are not the owner of this blog."}, status=status.HTTP_403_FORBIDDEN)

            data = {
                'title': request.data.get('title'),
                'about': request.data.get('about'),
                'tag': request.data.get('tag'),
                'status': "Pending",
            }

            serializer = BlogSerializer(blog, data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except BlogModel.DoesNotExist:
            return Response({"detail": "Blog not found."}, status=status.HTTP_404_NOT_FOUND)
    
    
    def patch(self, request):
        blog_id = request.data.get('id')
        try:
            blog = BlogModel.objects.get(id=blog_id)

            if blog.user == request.user or request.user.is_superuser :
                data = {
                    'title': request.data.get('title', blog.title),
                    'about': request.data.get('about', blog.about),
                    'tag': request.data.get('tag', blog.tag),
                    'status': "Pending",
                }

                serializer = BlogSerializer(blog, data=data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_200_OK)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            return Response({"detail": "You are not the owner of this blog."}, status=status.HTTP_403_FORBIDDEN)
        except BlogModel.DoesNotExist:
            return Response({"detail": "Blog not found."}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, *args, **kwargs):
        data = request.data
        blog_id = data.get('id')
        try:
            blog = BlogModel.objects.get(id=blog_id)

            if blog.user != request.user and not request.user.is_superuser:
                return Response({"detail": "You are not the owner of this blog."}, status=status.HTTP_403_FORBIDDEN)

            blog.delete()
            return Response(status=status.HTTP_200_OK)
        except BlogModel.DoesNotExist:
            return Response({"detail": "Blog not found."}, status=status.HTTP_404_NOT_FOUND)

class CommentAPI(APIView):

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        comments = CommentModel.objects.all()
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        data = {
            'comment': request.data.get('comment'),
            'user': request.user.id, 
            'blog_id': request.data.get('blog')
        }

        serializer = CommentSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request):
        comment_id = request.data.get('id')
        try:
            comment = CommentModel.objects.get(id=comment_id)
            data = request.data  
            serializer = CommentSerializer(comment, data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except CommentModel.DoesNotExist: 
            return Response({"detail": "Comment not found."}, status=status.HTTP_404_NOT_FOUND)

    def patch(self, request):
        comment_id = request.data.get('id')
        try:
            comments = CommentModel.objects.get(id=comment_id)
            data = {
                'comment': request.data.get('comment')
            }
            serializer = CommentSerializer(comments, data=data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except CommentModel.DoesNotExist: 
            return Response({"detail": "Comment not found."}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, *args, **kwargs):
        comment_id = request.data.get('id')
        try:
            comment = CommentModel.objects.get(id=comment_id)
            comment.delete()
            return Response(status=status.HTTP_200_OK)
        except CommentModel.DoesNotExist:
            return Response({"detail": "Comment not found."}, status=status.HTTP_404_NOT_FOUND)



 
@api_view(["PATCH"])
def status_Approved(request, pk):
    try:
        blog = BlogModel.objects.get(id=pk)
        data = {
            'status': 'Approved'
        }
        serializer = BlogSerializer(blog, data=data, partial=True)
        if serializer.is_valid():
            blog = serializer.save()

            subject = "Blog Approved"
            message = (
                f"New blog post: {blog.title}\n\n"
                f"Blog Description: {blog.about}.\n\n"
                f"Blog Status: {blog.status}.\n\n"
                f"The Email of the user is {blog.user.email}"
            )

            from_email = 'mforspamers@gmail.com'
            receiver = [blog.user.email]  
            try:
                send_mail(subject, message, from_email, receiver)
                return Response(serializer.data)
            except Exception as e:
                return Response({"detail": f"Error sending email: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except BlogModel.DoesNotExist:
        return Response({"detail": "Blog not found."}, status=status.HTTP_404_NOT_FOUND)

@api_view(["PATCH"])
def status_Rejected(request, pk):
    try:
        blog = BlogModel.objects.get(id=pk)
        data = {
            'status': 'Rejected'
        }
        serializer = BlogSerializer(blog, data=data, partial=True)
        if serializer.is_valid():
            blog = serializer.save()

            subject = "Blog Rejected"
            message = (
                f"New blog post: {blog.title}\n\n"
                f"Blog Description: {blog.about}.\n\n"
                f"Blog Status: {blog.status}.\n\n"
                f"The Email of the user is {blog.user.email}"
            )

            from_email = 'mforspamers@gmail.com'
            receiver = [blog.user.email]  
            try:
                send_mail(subject, message, from_email, receiver)
                return Response(serializer.data)
            except Exception as e:
                return Response({"detail": f"Error sending email: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except BlogModel.DoesNotExist:
        return Response({"detail": "Blog not found."}, status=status.HTTP_404_NOT_FOUND)
    


class TagsListCreateAPI(ListCreateAPIView):
    queryset = TagModel.objects.all()
    serializer_class = TagSerializer

class TagsRetrieveUpdateDestroyAPI(RetrieveUpdateDestroyAPIView):
    queryset = TagModel.objects.all()
    serializer_class = TagSerializer



@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def test_token(request):
    return Response("authentication sucessful")





# self.authentication_classes = [TokenAuthentication,SessionAuthentication]
# self.permission_classes = [IsAuthenticated]

