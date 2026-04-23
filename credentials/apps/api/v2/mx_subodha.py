import logging
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from credentials.apps.credentials.models import UserCredential, ProgramCertificate, Program
from threading import Thread
import time
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.urls import reverse
from django.core.management import call_command

log = logging.getLogger(__name__)

@require_GET
def get_program_certificate_detail(request):
    requested_username = request.GET.get('username')
    program_uuid = request.GET.get('program_uuid')
    program_name = ""
    if not requested_username or not program_uuid:
        return JsonResponse({"error": "Both 'username' and 'program_uuid' are required"}, status=400)

    try:
        program = Program.objects.filter(uuid=program_uuid).first()
        program_name = program.title 

    except Program.DoesNotExist:
        return JsonResponse({
            "status": False,
            "certificate_url": None,
            "program_name": "",
            "message": ""
        }, status=200)

    try:
        program_cert = ProgramCertificate.objects.filter(program_uuid=program_uuid).first()
        if not program_cert:
            return JsonResponse({
                "status": False,
                "certificate_url": None,
                "program_name": '',
                "message": "",
            }, status=200)
        user_credential = UserCredential.objects.select_related('credential_content_type').get(
            username=requested_username,
            status=UserCredential.AWARDED,
            program_credentials=program_cert,          
        )

        certificate_url = request.build_absolute_uri(user_credential.get_absolute_url())
        message = f"Congratulations! You've completed the {program_name} program."
        return JsonResponse({
            "status": True,
            "certificate_url": certificate_url,
            "program_name": program_name,
            "message": message
        }, status=200)

    # except ProgramCertificate.DoesNotExist:
    #     return JsonResponse({
    #         "status": False,
    #         "certificate_url": None,
    #         "program_name": '',
    #         "message": ""
    #     }, status=200)

    except UserCredential.DoesNotExist:
        return JsonResponse({
            "status": False,
            "certificate_url": None,
            "program_name": "",
            "message": ""
        }, status=200)

    except Exception as exc:
        log.exception("Error fetching program certificate")
        return JsonResponse({"error": "Internal server error"}, status=500)
 

@require_GET
def get_program_certificate_from_uuid(request):
    requested_username = request.GET.get('username')
    program_uuid = request.GET.get('program_uuid')
    program_name = ""
    if not requested_username or not program_uuid:
        return JsonResponse({"error": "Both 'username' and 'program_uuid' are required"}, status=400)

    try:
        program = Program.objects.filter(uuid=program_uuid).first()
        program_name = program.title 

    except Program.DoesNotExist:
        return JsonResponse({
            "status": False,
            "certificate_url": None,
            "program_name": "",
            "message": ""
        }, status=200)

    try:
        program_cert = ProgramCertificate.objects.filter(program_uuid=program_uuid).first()

        user_credential = UserCredential.objects.select_related('credential_content_type').get(
            username=requested_username,
            status=UserCredential.AWARDED,
            program_credentials=program_cert,          
        )
        if not program_cert:
            return JsonResponse({
                "status": False,
                "certificate_url": None,
                "program_name": '',
                "message": "",
                "type": "no-certificate-config"
            }, status=200)
        
        certificate_url = request.build_absolute_uri(user_credential.get_absolute_url())
        message = f"Congratulations! You've completed the {program_name} program."
        return JsonResponse({
            "status": True,
            "certificate_url": certificate_url,
            "program_name": program_name,
            "message": message
        }, status=200)

    # except ProgramCertificate.DoesNotExist:
    #     return JsonResponse({
    #         "status": False,
    #         "certificate_url": None,
    #         "program_name": '',
    #         "message": "",
    #         "type": "no-certificate-config"
    #     }, status=200)

    except UserCredential.DoesNotExist:
        return JsonResponse({
            "status": False,
            "certificate_url": None,
            "program_name": "",
            "message": "",
            "type": "not-egilible"

        }, status=200)

    except Exception as exc:
        log.exception("Error fetching program certificate")
        return JsonResponse({"error": "Internal server error"}, status=500)
 
 