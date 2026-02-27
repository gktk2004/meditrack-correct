
import os
import django
from django.core.files.uploadedfile import SimpleUploadedFile

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'meditrack.settings')
django.setup()

from userapp.models import User, Complaint, ComplaintImage
from userapp.views import ComplaintCreateView
from rest_framework.test import APIRequestFactory

def test_complaint_creation():
    # 1. Ensure user exists
    user, created = User.objects.get_or_create(
        email="test_complaint_user@example.com",
        defaults={
            "username": "test_complaint_user",
            "password": "password123",
            "phone": "1234567890",
            "blood_group": "O+",
            "gender": "Male"
        }
    )
    print(f"User ID: {user.id}")

    # 2. Simulate Image File
    image_content = b"fake_image_content"
    image = SimpleUploadedFile("test_image.jpg", image_content, content_type="image/jpeg")

    # 3. Prepare Request Data
    data = {
        'user_id': user.id,
        'category': 'Service Issue',
        'description': 'The waiting time was too long.',
        'image': image
    }

    # 4. Make Request
    factory = APIRequestFactory()
    request = factory.post('/api/complaint/create/', data, format='multipart')
    view = ComplaintCreateView.as_view()
    response = view(request)

    print(f"Response Status: {response.status_code}")
    print(f"Response Data: {response.data}")

    if response.status_code == 201:
        complaint_id = response.data['complaint_id']
        complaint = Complaint.objects.get(id=complaint_id)
        print(f"Complaint Created: {complaint}")
        print(f"Description: {complaint.description}")
        
        # Check Images
        images = ComplaintImage.objects.filter(complaint=complaint)
        print(f"Images Count: {images.count()}")
        for img in images:
            print(f"Image URL: {img.image.url}")
            # Clean up
            if os.path.exists(img.image.path):
                os.remove(img.image.path)
                print("Test image deleted.")
        
        # Cleanup Complaint
        complaint.delete()
        print("Test complaint deleted.")
    else:
        print("Failed to create complaint.")

if __name__ == "__main__":
    test_complaint_creation()
