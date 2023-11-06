from rest_framework import serializers
from .models import *
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username']


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField()     
    # subscribe = serializers.BooleanField()            
    
    
    # def validate(self, data):
    #     subscribe = data.get('subscribe')
    #     email = data.get('email')
    #     if subscribe is True:
    #         MailModel.objects.create(email=email, subscribe=True)
    #     return data
    
    
    
    def validate_password(self, data):
        try:
            validate_password(data) 
        except Exception as e:
            raise serializers.ValidationError(str(e))
        
        return data

    def validate_username(self, data):
        if User.objects.filter(username=data).exists():
            raise serializers.ValidationError('Username is already taken')
        
        return data
    
    def validate_email(self, data):
        if User.objects.filter(email=data).exists():
            raise serializers.ValidationError("Email is already exists")
        
        return data
    
    def create(self, validated_data):
        username = validated_data['username']
        email = validated_data['email']
        password = validated_data['password']

        user = User.objects.create(username=username, email=email)
        user.set_password(password)
        user.save()
        return user
    

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = TagModel
        fields = ["tag"]


class BlogSerializer(serializers.ModelSerializer):

    # user = UserSerializer()
    # tag = TagSerializer(many=True)
    class Meta:
        model = BlogModel
        fields = '__all__'
        # depth = 1




class CommentSerializer(serializers.ModelSerializer):

    # user = UserSerializer()
    class Meta:
        model = CommentModel
        fields = '__all__'
        # depth = 1




class SearchSerializer(serializers.Serializer):
    search = serializers.CharField(max_length=100, required=False)