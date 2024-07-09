from django.shortcuts import render

from django.shortcuts import render
from django.http import HttpResponse
from PIL import Image, ImageDraw, ImageFont
import imageio
import os
from .models import GeneratedVideo
import numpy
from django.views.decorators.csrf import csrf_exempt


def index(request):
    return render(request, 'index.html')


def resize_image(image, width, height):
    if width % 16 != 0:
        width += 16 - (width % 16)
    if height % 16 != 0:
        height += 16 - (height % 16)
    return image.resize((width, height))


def create_image(text, width, height, font, x_position, y_position):
    image = Image.new('RGB', (width, height), color='black')
    draw = ImageDraw.Draw(image)
    draw.text((x_position, y_position), text, font=font, fill='white')
    return image


def generate_frames(text="Hello, World!", width=100, height=100, font=ImageFont.load_default(), total_frames=120 * 3):
    frames = []
    for frame_number in range(total_frames):
        speed = (width + font.getbbox(text)[2]) / total_frames
        x_position = width - (frame_number * speed)
        y_position = (height - font.getbbox(text)[3]) // 2
        frame = create_image(text, width, height, font, x_position, y_position)
        frame = resize_image(frame, width, height)
        frames.append(frame)
    return frames


def save_video(frames, output_filename="running_text.mp4", fps=120):
    writer = imageio.get_writer(output_filename, fps=fps)
    for frame in frames:
        numpy_frame = numpy.array(frame)
        writer.append_data(numpy_frame)
    writer.close()

@csrf_exempt
def generate_video(request):
    if request.method == 'POST':
        text = request.POST.get('text', 'Hello, World!')
        filename = request.POST.get('filename', 'running_text.mp4')
        width, height = 100, 100
        duration = 3
        fps = 120
        total_frames = duration * fps
        font = ImageFont.load_default()
        frames = generate_frames(text, width, height, font, total_frames)
        save_video(frames, filename, fps)

        GeneratedVideo.objects.create(text=text, filename=filename)

        with open(filename, 'rb') as f:
            response = HttpResponse(f.read(), content_type='video/mp4')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            os.remove(filename)
            return response

    return HttpResponse("Invalid request", status=400)
