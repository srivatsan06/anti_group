from .base_model import BaseModel
from .user import UserModel
from .student import StudentModel
from .course import CourseModel
from .module import ModuleModel
from .attendance import AttendanceModel
from .survey import SurveyModel
from .deadline import DeadlineModel
from .grade import GradeModel
__all__ = [
    'BaseModel',
    'UserModel',
    'StudentModel',
    'CourseModel',
    'ModuleModel',
    'AttendanceModel',
    'SurveyModel',
    'DeadlineModel',
    'GradeModel'
]
