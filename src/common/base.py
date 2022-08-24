import factory


class BaseFactory(factory.django.DjangoModelFactory):
    @classmethod
    def _after_postgeneration(cls, instance, create, results=None):
        """Save again the instance if creating and at least one hook ran."""
        # if create and results:
        # Some post-generation hooks ran, and may have modified us.
        # instance.save()
        # THIS BEHAVIOUR IS DISABLED FOR PERFORMANCE REASONS !
