from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.conf import settings

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from munch.serializers import *
from munch.models import *

import requests
import re


# Inbox API

@api_view(['POST'])
def inbox(request, target_serial):
    payload_type = request.get('type')
    
    if payload_type == 'author':
        pass

    elif payload_type == 'follow':
        serializer = FollowRequestSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors)
    
    elif payload_type == 'entry':
        pass

    elif payload_type == 'comment':
        pass

    elif payload_type == 'like':
        pass

    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)