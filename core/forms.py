import json
import logging

from django import forms

from core.models import Challenge, Student

logger = logging.getLogger("sirius")


class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["courses"].required = False
        self.fields["challenges"].required = False


class ChallengeTextForm(forms.ModelForm):
    challenge = forms.CharField(required=True, widget=forms.Textarea)
    hints = forms.CharField(widget=forms.Textarea, required=False)
    is_code_challenge = forms.BooleanField(required=False)
    programming_language = forms.ChoiceField(
        choices=[
            ("", "No programming language"),
            ("javascript", "JavaScript"),
            ("python", "Python"),
        ],
        required=False,
    )
    estimated_solution_time = forms.IntegerField(required=False)
    use_cases_input = forms.CharField(widget=forms.Textarea, required=False)
    use_cases_output = forms.CharField(widget=forms.Textarea, required=False)

    class Meta:
        model = Challenge
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["text"].widget.attrs["readonly"] = True

        if self.instance and self.instance.text:
            try:
                data = json.loads(self.instance.text)
                self.fields["challenge"].initial = data.get("challenge", "")
                self.fields["hints"].initial = (
                    "\n".join(data.get("hints", []))
                    if isinstance(data.get("hints"), list)
                    else ""
                )
                self.fields["is_code_challenge"].initial = data.get(
                    "is_code_challenge", False
                )
                self.fields["programming_language"].initial = data.get(
                    "programming_language", ""
                )
                self.fields["estimated_solution_time"].initial = data.get(
                    "estimated_solution_time", ""
                )
                self.fields["use_cases_input"].initial = (
                    "\n".join(data.get("use_cases_input", []))
                    if isinstance(data.get("use_cases_input"), list)
                    else ""
                )
                self.fields["use_cases_output"].initial = (
                    "\n".join(data.get("use_cases_output", []))
                    if isinstance(data.get("use_cases_output"), list)
                    else ""
                )
            except Exception as e:
                # raise ValidationError("Invalid JSON in the text field.")
                self.fields["challenge"].initial = self.instance.text

    def save(self, commit=True):
        data = {
            "challenge": self.cleaned_data["challenge"],
            "hints": [
                hint.strip()
                for hint in self.cleaned_data["hints"].splitlines()
                if hint.strip()
            ],
            "is_code_challenge": self.cleaned_data["is_code_challenge"],
            "programming_language": self.cleaned_data["programming_language"],
            "estimated_solution_time": self.cleaned_data["estimated_solution_time"],
            "use_cases_input": [
                line.strip()
                for line in self.cleaned_data["use_cases_input"].splitlines()
                if line.strip()
            ],
            "use_cases_output": [
                line.strip()
                for line in self.cleaned_data["use_cases_output"].splitlines()
                if line.strip()
            ],
        }
        self.instance.text = json.dumps(data, indent=4)
        return super().save(commit)
