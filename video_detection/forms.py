from django import forms
from .models import VideoDetection

class VideoUploadForm(forms.ModelForm):
    class Meta:
        model = VideoDetection
        fields = ['video_file']
        widgets = {
            'video_file': forms.FileInput(attrs={
                'accept': 'video/*',
                'class': 'block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-green-50 file:text-green-700 hover:file:bg-green-100'
            })
        }
    
    def clean_video_file(self):
        video_file = self.cleaned_data.get('video_file')
        if video_file:
            # Check file extension
            allowed_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.webm']
            if not any(video_file.name.lower().endswith(ext) for ext in allowed_extensions):
                raise forms.ValidationError('Only video files are allowed (.mp4, .avi, .mov, .mkv, .webm).')
            
            # Check file size (100MB limit)
            if video_file.size > 100 * 1024 * 1024:
                raise forms.ValidationError('Video file size must be less than 100MB.')
        
        return video_file