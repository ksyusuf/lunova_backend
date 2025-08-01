from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .permissions import IsExpertPermission
from .serializers import CreateMeetingSerializer


@api_view(['POST'])
@permission_classes([IsExpertPermission])
def create_zoom_meeting(request):
    """
    Create a new Zoom meeting
    
    POST /api/v1/zoom/meetings/
    {
        "topic": "Meeting Title",
        "start_time": "2024-01-15T10:00:00Z",
        "duration": 45
    }
    """
    serializer = CreateMeetingSerializer(data=request.data)
    if serializer.is_valid():
        result = serializer.save()
        
        if result.get('success'):
            return Response(result, status=status.HTTP_201_CREATED)
        else:
            return Response(
                {'error': result.get('error', 'Failed to create meeting')},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 