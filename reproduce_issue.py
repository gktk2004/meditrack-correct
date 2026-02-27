
import os
import django
from django.conf import settings

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'meditrack.settings')
django.setup()

from django.test import RequestFactory
from userapp.models import User, Complaint, ComplaintImage
from meditrackapp.models import Department, Doctor, BloodDonationAdmin
from userapp.views import SubmitComplaintAPIView
from meditrackapp.views import admin_complaints_view, add_doctor, add_blood_donation_admin
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.messages.storage.fallback import FallbackStorage

def setup_request(request):
    """Add session and message support to request."""
    middleware = SessionMiddleware(lambda x: None)
    middleware.process_request(request)
    request.session.save()
    messages = FallbackStorage(request)
    setattr(request, '_messages', messages)
    return request

def test_complaint_api():
    print("\n--- Testing Complaint API ---")
    
    # create user
    user, created = User.objects.get_or_create(
        email="test@example.com", 
        defaults={"username": "testuser", "password": "password", "gender": "Male", "blood_group": "A+"}
    )
    
    # mock image
    image = SimpleUploadedFile("test_image.jpg", b"file_content", content_type="image/jpeg")
    
    factory = RequestFactory()
    data = {
        "user": user.id,
        "category": "Technical",
        "description": "This is a test complaint.",
        "images": [image]
    }
    
    request = factory.post('/user/submit_complaints/', data, format='multipart')
    view = SubmitComplaintAPIView.as_view()
    response = view(request)
    
    print(f"API Response Status: {response.status_code}")
    print(f"API Response Data: {response.data}")
    
    if response.status_code == 201:
        print("✅ Complaint submitted successfully.")
        complaint = Complaint.objects.get(id=response.data['data']['id'])
        print(f"Complaint Created: {complaint}")
        print(f"Images count: {complaint.images.count()}")
    else:
        print("❌ Complaint submission failed.")

def test_admin_complaints_view():
    print("\n--- Testing Admin Complaint View ---")
    factory = RequestFactory()
    request = factory.get('/admin/complaints/')
    
    # The view renders a template, so we check status code
    try:
        response = admin_complaints_view(request)
        print(f"View Response Status: {response.status_code}")
        if response.status_code == 200:
             print("✅ Admin complaint view rendered successfully.")
        else:
             print("❌ Admin complaint view failed.")
    except Exception as e:
        print(f"❌ Error rendering view: {e}")

def test_add_doctor():
    print("\n--- Testing Add Doctor ---")
    
    # Create a department first
    dept, _ = Department.objects.get_or_create(department="Cardiology")
    
    factory = RequestFactory()
    data = {
        "name": "Dr. Test",
        "phone_number": "1234567890",
        "email": "drtest@example.com",
        "password": "password",
        "specialization": dept.id
    }
    
    request = factory.post('/add_doctor', data)
    setup_request(request) # Add session/messages
    
    response = add_doctor(request)
    
    print(f"Response Status Code: {response.status_code}") # Should be 302 (redirect)
    
    if Doctor.objects.filter(email="drtest@example.com").exists():
        print("✅ Doctor added successfully.")
    else:
        print(f"❌ Doctor not added. Doctors count: {Doctor.objects.count()}")

def test_add_blood_admin():
    print("\n--- Testing Add Blood Donation Admin ---")
    
    # Clean up existing to test creation
    BloodDonationAdmin.objects.all().delete()
    
    factory = RequestFactory()
    data = {
        "username": "bloodadmin",
        "email": "bloodadmin@example.com",
        "password": "password",
        "phone_number": "9876543210"
    }
    
    request = factory.post('/admin/blood-donation-admin/add/', data)
    setup_request(request)
    
    # Need admin session
    request.session['admin_id'] = 1 
    
    response = add_blood_donation_admin(request)
    
    print(f"Response Status Code: {response.status_code}")
    
    if BloodDonationAdmin.objects.filter(username="bloodadmin").exists():
        print("✅ Blood Donation Admin added successfully.")
    else:
        print("❌ Blood Donation Admin not added.")

if __name__ == "__main__":
    test_complaint_api()
    test_admin_complaints_view()
    test_add_doctor()
    test_add_blood_admin()
