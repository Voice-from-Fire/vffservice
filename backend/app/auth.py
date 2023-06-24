from app.db.models import User, Sample


def can_access_sample(user: User, sample: Sample) -> bool:
    return user.id == sample.owner or user.is_reviewer_or_more()
