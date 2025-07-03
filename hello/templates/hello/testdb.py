from hello.models import GeneratedAudio
latest = GeneratedAudio.objects.last()
print(latest.voice, latest.style, latest.rate, latest.pitch, latest.volume)
