from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from .models import Courses
class Step1Form(forms.ModelForm):
    class Meta:
        model = Courses
        fields = ['course_description', 'participants_info', 'prerequisite_knowledge', 'available_material', 'content_lang', 'course_type', 'optimized_for_mooc', 'project_based', 'assignment', 'long_course_support', 'knowledge_level', 'duration', 'practice']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'POST'
        self.helper.add_input(Submit('submit', 'Next'))
# Step 2: Contact Information
class Step2Form(forms.ModelForm):
    class Meta:
        model = Courses
        fields = ['course_title', 'course_description']


class Step3Form(forms.Form):
    def __init__(self, *args, **kwargs):
        learning_outcomes_data = kwargs.pop('learning_outcomes_data', [])
        super(Step3Form, self).__init__(*args, **kwargs)

        # Dynamically create fields for each learning outcome
        for index, outcome_data in enumerate(learning_outcomes_data):
            prefix = f'learning_outcome_{index}'
            self.fields[f'{prefix}_tag'] = forms.CharField(
                max_length=1,
                initial=outcome_data.get('tag', ''),
                label=f'Tag for Outcome {index + 1}',
                required=True
            )
            self.fields[f'{prefix}_number'] = forms.IntegerField(
                initial=outcome_data.get('number', ''),
                label=f'Number for Outcome {index + 1}',
                required=True
            )
            self.fields[f'{prefix}_outcome'] = forms.CharField(
                widget=forms.Textarea(attrs={'rows': 2}),
                initial=outcome_data.get('outcome', ''),
                label=f'Outcome {index + 1}',
                required=True
            )
            sub_items = outcome_data.get('sub_items', [])
            self.fields[f'{prefix}_sub_items'] = forms.CharField(
                widget=forms.Textarea(attrs={'rows': 3}),
                initial='\n'.join(sub_items) if sub_items else '',
                label=f'Sub Items for Outcome {index + 1} (One per line)',
                required=False
            )

            # Adding buttons for regenerate, edit, and delete
            self.fields[f'{prefix}_regenerate'] = forms.BooleanField(
                required=False,
                widget=forms.CheckboxInput(attrs={'class': 'regenerate-btn'}),
                label='Regenerate'
            )
            self.fields[f'{prefix}_delete'] = forms.BooleanField(
                required=False,
                widget=forms.CheckboxInput(attrs={'class': 'delete-btn'}),
                label='Delete'
            )

# Step 4: Account Information
class Step4Form(forms.Form):
    content_listing = forms.CharField(widget=forms.Textarea, required=False)


# Step 5: Preferences
class Step5Form(forms.Form):
    receive_newsletter = forms.BooleanField(required=False)
    preferred_contact_method = forms.ChoiceField(choices=[('email', 'Email'), ('phone', 'Phone')])

# Step 6: Confirmation
class Step6Form(forms.Form):
    confirm = forms.BooleanField(required=True)
