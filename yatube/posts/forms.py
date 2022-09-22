from django import forms

from .models import Post, Comment


class PostForm(forms.ModelForm):
    """Форма для создание постов."""
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['group'].empty_label = 'Группа не выбрана'

    def clean_text(self):
        text = self.cleaned_data['text']
        if text.replace(' ', '') == '':
            raise forms.ValidationError('Поле не заполнено')
        return text


class CommentForm(forms.ModelForm):
    """Форма для создание постов."""
    class Meta:
        model = Comment
        fields = ('text',)
