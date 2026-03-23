from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.conf import settings

from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework import status

from munch.models import Server
from munch.serializers import AuthorSerializer, ServerSerializer

import requests

@login_required
def settings_page(request): #renamed to settings_page its overwriting our import settings from django
    return render(request, 'munch/settings.html')

@login_required
def node_management_page(request):
    nodes = Server.objects.filter(is_approved=True)
    context = {
        'nodes': nodes
    }
    return render(request, 'munch/node-management.html', context)


# Node Connection API

class ConnectNode(APIView):

    def post(self, request):
        serializer = ServerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ManageNode(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAdminUser]

    def delete(self, request, node_url):
        node = get_object_or_404(Server, url=node_url, is_approved=True)
        node.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def post(self, request, node_url):
        node = get_object_or_404(Server, url=node_url, is_approved=True)

        response = requests.get(
            f"{node.url}/api/authors", 
            auth=(settings.AUTH_USERNAME, settings.AUTH_PASSWORD),
            headers={
                'Origin':settings.BACKEND_URL
            })
        if not response.ok:
            return Response(
                data={'error': f"Failed to get authors from node {node.url}: {response.status_code}"},
                status=response.status_code
            )
        
        data=response.json()
        serializer = AuthorSerializer(data=data, many=True)
        if not serializer.is_valid():
            return Response(
                data={
                    'error': f"Invalid author data from node {node.url}",
                    'details': serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response(data, status=status.HTTP_200_OK)
