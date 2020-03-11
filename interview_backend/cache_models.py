from django.core.exceptions import ObjectDoesNotExist
from .models import Interview
from django.core.cache import caches

_current_interviews = caches['current_interviews']
_submission_results = caches['submission_results']


class CurrentInterview:
    def __init__(self, user_id):
        self.user_id = user_id

    def set(self, interview: Interview, **kwargs):
        return _current_interviews.set(self.user_id, interview.id, **kwargs)

    def get(self) -> [Interview, None]:
        interview_id = _current_interviews.get(self.user_id)
        if interview_id is not None:
            try:
                interview = Interview.objects.get(id=interview_id)
                return interview
            except ObjectDoesNotExist:
                return None

    def unset(self):
        return _current_interviews.delete(self.user_id)
