# shortener/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.conf import settings
from .models import URL
from .forms import URLForm
import qrcode
import io


def home(request):
    if request.method == 'POST':
        form = URLForm(request.POST)
        if form.is_valid():
            url = form.save(commit=False)
            url.short_code = URL.create_short_code()
            url.save()
            messages.success(request, 'URL shortened successfully!')
            return render(request, 'success.html', {'url': url})
        else:
            messages.error(request, 'Please enter a valid URL.')
    else:
        form = URLForm()

    recent_urls = URL.objects.order_by('-created_at')[:5]
    return render(request, 'home.html', {
        'form': form,
        'recent_urls': recent_urls
    })


def create_url(request):
    if request.method == 'POST':
        form = URLForm(request.POST)
        if form.is_valid():
            url = form.save(commit=False)
            url.short_code = URL.create_short_code()
            url.save()
            messages.success(request, 'URL shortened successfully!')
            return redirect('shortener:url_detail_stats', short_code=url.short_code)
    return redirect('shortener:home')


def redirect_to_original(request, short_code):
    url = get_object_or_404(URL, short_code=short_code)
    url.clicks += 1
    url.save()
    return redirect(url.original_url)


def url_stats(request):
    urls = URL.objects.order_by('-clicks')
    return render(request, 'stats.html', {'urls': urls})

def url_detail_stats(request, short_code):
    url = get_object_or_404(URL, short_code=short_code)
    return render(request, 'url_detail_stats.html', {'url': url})


@require_POST
def delete_url(request, short_code):
    url = get_object_or_404(URL, short_code=short_code)
    url.delete()
    messages.success(request, 'URL deleted successfully!')
    return redirect('shortener:stats')


def generate_qr(request, short_code):
    url = get_object_or_404(URL, short_code=short_code)

    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url.get_absolute_url())
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    # Create response
    response = HttpResponse(content_type='image/png')
    img_io = io.BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)
    response.write(img_io.getvalue())

    return response


# API Views
def url_list_api(request):
    urls = URL.objects.all().values(
        'original_url',
        'short_code',
        'clicks',
        'created_at'
    )
    return JsonResponse({'urls': list(urls)})


@require_POST
def create_url_api(request):
    try:
        original_url = request.POST.get('url')
        if not original_url:
            return JsonResponse({'error': 'URL is required'}, status=400)

        url = URL.objects.create(
            original_url=original_url,
            short_code=URL.create_short_code()
        )

        return JsonResponse({
            'original_url': url.original_url,
            'short_url': url.get_absolute_url(),
            'short_code': url.short_code
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)