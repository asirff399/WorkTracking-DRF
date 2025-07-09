from django.shortcuts import render
from rest_framework.views import APIView
from .serializers import UserRegisterSerializer,UserLoginSerializer,UserSerializer
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.shortcuts import redirect
from rest_framework.response import Response
from rest_framework import status
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.shortcuts import get_object_or_404

# Create your views here.
User = get_user_model()
 
class UserRegisterAPIView(APIView):
    serializer_class = UserRegisterSerializer

    def post(self,request):
        serializer = self.serializer_class(data=request.data)
        
        if serializer.is_valid():
            user = serializer.save()
            access = AccessToken.for_user(user=user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            confirm_link = f'http://127.0.0.1:8000/account/activate/{uid}/{access}'
            email_subject = 'Confirmation Email'
            email_body = render_to_string('Confirmation_mail.html',{'confirm_link':confirm_link})
            email = EmailMultiAlternatives(email_subject,'',to=[user.email])
            email.attach_alternative(email_body,'text/html')
            email.send()
            
            response = self.serializer_class(user)
            
            return Response({
                "success":True,
                "statusCode": status.HTTP_201_CREATED,
                "message":"Registation successful. Please Check your mail for confirmation.",
                "data": response.data,
            },status=status.HTTP_201_CREATED)
        else:
            return Response({
                "success":False,
                "statusCode":status.HTTP_400_BAD_REQUEST,
                "message":"Registation failed. Please check the provided data.",
                "error": serializer.errors,
            },status=status.HTTP_400_BAD_REQUEST)
            
def activate(self,uid64,token):
    try:
        uid = urlsafe_base64_decode(uid64).decode()
        user = User.objects.get(pk=uid)
    except(User.DoesNotExist,ValueError,TypeError):
        user = None
        return redirect("http://127.0.0.1:8000/account/register")
    
    try:
        access = AccessToken(token)
        token_user_id = access.payload.get('user_id')
        
        if user.id != token_user_id:
            raise InvalidToken("Token dose not match the user.")
        
        if user is not None and not user.is_active:
            user.is_active = True
            user.save()
            return redirect('http://127.0.0.1:8000/account/login')
        else:
            return redirect('http://127.0.0.1:8000/account/login')
    except (InvalidToken,TokenError):
        return redirect('http://127.0.0.1:8000/account/register')
    except Exception:
        return redirect('http://127.0.0.1:8000/account/register')
    
class UserLoginAPIView(APIView):
    serializer_class = UserLoginSerializer
    
    def post(self,request):
        serializer = UserLoginSerializer(data=request.data)
        
        if serializer.is_valid():
            username_or_email = serializer.validated_data['username']
            password = serializer.validated_data['password']
            
            user = User.objects.filter(username=username_or_email).first() or User.objects.filter(email=username_or_email).first()
            if user:
                authenticated_user = authenticate(username=user.username,password=password)
                if authenticated_user:
                    refresh = RefreshToken.for_user(authenticated_user)
                    login(request,authenticated_user)
                    
                    return Response({
                        "success":True,
                        "statusCode":status.HTTP_200_OK,
                        "message":"Looged in successfully",
                        "data":{
                            "refresh":str(refresh),
                            "access": str(refresh.access_token),
                            "user_id":authenticated_user.id,
                            "username":authenticated_user.username,
                        }
                    },status=status.HTTP_200_OK)
                else:
                    return Response({
                    "success":False,
                    "message":"Invalid credentials.",
                    "error":"Please check your username or password.",
                    "statusCode":status.HTTP_400_BAD_REQUEST,
                },status=status.HTTP_400_BAD_REQUEST)
            else:
               return Response({
                "success":False,
                "message":"Invalid username or email.",
                "error":"User not found.",
                "statusCode":status.HTTP_400_BAD_REQUEST
            },status=status.HTTP_400_BAD_REQUEST) 
        else:
            return Response({
                "success":False,
                "message":"Invalid input",
                "error": serializer.errors,
                "statusCode":status.HTTP_400_BAD_REQUEST
            },status=status.HTTP_400_BAD_REQUEST)    
            
class UserLogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self,request):
        logout(request)
        return Response({
            "success":True,
            "statusCode": status.HTTP_200_OK,
            "message":"Successfully logged out."
        },status=status.HTTP_200_OK)
        
class UserViewset(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    # permission_classes = [IsAuthenticated]
    
class UserProfileUpdateApiView(APIView):
    # permission_classes = [IsAuthenticated]

    def put(self,request,*args, **kwargs):
        user = request.user
        user = get_object_or_404(User,user=user)

        user_serializer = UserSerializer(user,data=request.data.get('user'))

        if user_serializer.is_valid():
            user_serializer.save()
            return Response({"user": user_serializer.data}, status=status.HTTP_200_OK)
        
        return Response({"user_errors": user_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)