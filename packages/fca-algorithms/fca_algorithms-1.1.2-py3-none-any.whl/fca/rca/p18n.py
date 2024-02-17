from .models import Exists, Forall

EXISTS = Exists()
FORALL = Forall()

Operators = {
    'exists': EXISTS,
    'forall': FORALL,
}
