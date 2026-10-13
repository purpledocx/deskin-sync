from abc import ABC, abstractmethod


class RoleStrategy(ABC):
    """Strategy: booking rules depend on user's role"""

    min_mins_before_change: int

    @abstractmethod
    def can_view_all(self) -> bool:
        ...

    @abstractmethod
    def can_manage_booking(self, booking, user) -> bool:
        ...


"""------------------------------------------------------------RULES------------------------------------------------------------"""

class StudentStrategy(RoleStrategy):
    
    min_mins_before_change = 30

    def can_view_all(self) -> bool:
        return False
   
    def can_manage_booking(self, booking, user):
        return booking.user_id == user.id



class TeacherStrategy(RoleStrategy):
    min_mins_before_change = 30

    def can_view_all(self) -> bool:
        return True
    
    def can_manage_booking(self, booking, user) -> bool:
        return True



class AdminStrategy(RoleStrategy):
    
    min_mins_before_change = 0
    
    def can_view_all(self) -> bool:
        return True
    
    def can_manage_booking(self, bookig, user) -> bool:
        return True



_STRATEGIES =   {
    "Student": StudentStrategy(),
    "Teacher": TeacherStrategy(),
    "Admin": AdminStrategy()
}


def get_strategy(user) -> RoleStrategy:

    role_name = getattr(user.role, "name", user.role)

    # unknown role -> least privileges 
    return _STRATEGIES.get(role_name, _STRATEGIES["Student"])