# This file makes the controllers directory a Python package
from .auth_controller import AuthController
from .student_controller import StudentController
from .module_staff_controller import ModuleStaffController
from .welfare_staff_controller import WelfareStaffController
from .admin_controller import AdminController

__all__ = [
    'AuthController',
    'StudentController',
    'ModuleStaffController',
    'WelfareStaffController',
    'AdminController'
]

