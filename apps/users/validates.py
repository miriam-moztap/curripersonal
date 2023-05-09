"""
Function to validate a role user with email
"""

from ..general.models import Role


def validate_role_email(email, role):
    if (email or role) is None:
        return False, f'El rol o email deben ser no nulos'
    role_find = Role.objects.filter(id=role).first()
    host_email = email.split('@')[1]
    if role_find:
        if role_find.host == '*':
            return True, 'El rol es válido con el email'
        elif role_find.host == host_email:
            return True, 'El rol es válido con el email'
        else:
            return False, 'No está autorizado para este rol'
    return False, f'No existe el rol dado'
