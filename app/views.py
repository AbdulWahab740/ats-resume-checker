from django.http import JsonResponse
from django.shortcuts import render
from django.conf import settings
from .app import docs_to_words, keyword_test, skill_check, formating_check, Keyword, skills, Formatting, pdf_reader
import os
from .models import Document
from .forms import UploadFileForm
from django.http import HttpResponseRedirect
from django.shortcuts import render
from .forms import UploadFileForm
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import FileSystemStorage
from django.conf import settings
import os

def handle_uploaded_file(uploaded_file):
    fs = FileSystemStorage()
    filename = fs.save(uploaded_file.name, uploaded_file)  # saves in MEDIA_ROOT
    full_path = os.path.join(settings.MEDIA_ROOT, filename)  # full disk path
    return full_path
def upload_docs(request):
    if request.method == 'POST' and request.FILES.get('resume'):
        uploaded_file = request.FILES['resume']
        saved_path = handle_uploaded_file(uploaded_file)
        
        # Now you have the full media path to the uploaded file
        print("Saved at:", saved_path)

        # Proceed with parsing or processing the file here...
        return JsonResponse({'file_path': saved_path})

    return JsonResponse({'error': 'No file uploaded'}, status=400)
def calculate_ats(job, skillReq, resume, uploaded_file):
    try:
        file_extension = os.path.splitext(uploaded_file.name)[1].lower()

        docdata = ""  # Default initialization to avoid UnboundLocalError

        if file_extension == ".pdf":
            docdata = pdf_reader(resume)
        elif file_extension in [".docx", ".doc"]:
            docdata = docs_to_words(resume)
        else:
            raise ValueError("Unsupported file format")

        keywor = keyword_test(docdata, job) * Keyword
        skillVal = skill_check(resume, skillReq) * skills
        formating = formating_check(docdata) * Formatting
        total = keywor + skillVal + formating
        return total
    except Exception as e:
        print(f"Error in ATS calculation: {e}")
        return None

def index(request):
    return render(request, "index.html")


@csrf_exempt  # Only use if you're not passing csrf_token properly
def upload_docs(request):
    print("Request received")  # Log to confirm request is coming in
    if request.method == 'POST':
        # Retrieve the fields from the request
        uploaded_file = request.FILES.get('resume')  # Field name must match the file input's 'name' attribute
        job_description = request.POST.get('job_description')
        skills = request.POST.get('skills')  # Corrected field name to match the JS field

        # Validate if all fields are provided
        if not uploaded_file or not job_description or not skills:
            return JsonResponse({'error': 'All fields are required'}, status=400)

        print(f"File: {uploaded_file.name}, Job Description: {job_description}, Skills: {skills}")

        try:
            upload_path = handle_uploaded_file(uploaded_file)
            ats_score = calculate_ats(job_description, skills, upload_path,uploaded_file)  # Call the ATS calculation function
            print(f"Calculated ATS Score: {ats_score}")  # Log the ATS score

            # Return the ATS score if calculation is successful
            if ats_score is not None:
                return JsonResponse({
                    "status": "success",
                    "message": "✅ Your results are ready.",
                    "ats": ats_score  # Return ATS score in response
                })
            else:
                return JsonResponse({"status": "error", "message": "ATS calculation failed."})
        except Exception as e:
            # Log the exception and return a generic error message
            return JsonResponse({"status": "error", "message": f"Upload failed: {str(e)}"})
    
    return JsonResponse({"status": "error", "message": "Invalid request method."})