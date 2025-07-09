from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class UserRegisterSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['username','first_name','last_name','email','password','confirm_password']
        
    def save(self, **kwargs):
        username = self.validated_data['username']
        first_name = self.validated_data['first_name']
        last_name = self.validated_data['last_name']
        email = self.validated_data['email']
        password = self.validated_data['password']
        confirm_password = self.validated_data['confirm_password']
        
        if password != confirm_password:
            raise serializers.ValidationError({'error':"Password don't match"})
        
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError({'error':"Email already exist !!"})
        
        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError({'error':"Username already exist !!"})
        
        user = User(username=username,first_name=first_name,last_name=last_name,email=email)
        user.set_password(password)
        user.is_active = False
        user.save()
        
        return user

class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)

class UserSerializer(serializers.ModelSerializer): 
    class Meta:
        model = User
        fields = ['id','first_name','last_name','email','role','phone','address','date_joined']
        read_only_fields = ['id', 'email', 'date_joined', 'role']