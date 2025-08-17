from sqlmodel import SQLModel, Field, Relationship, Column, JSON
from datetime import datetime, time
from typing import Optional, List, Dict, Any
from enum import Enum


class DayOfWeek(str, Enum):
    MONDAY = "MONDAY"
    TUESDAY = "TUESDAY"
    WEDNESDAY = "WEDNESDAY"
    THURSDAY = "THURSDAY"
    FRIDAY = "FRIDAY"
    SATURDAY = "SATURDAY"
    SUNDAY = "SUNDAY"


class CourseType(str, Enum):
    THEORY = "THEORY"
    LAB = "LAB"
    PRACTICAL = "PRACTICAL"
    SEMINAR = "SEMINAR"
    PROJECT = "PROJECT"


class RoomType(str, Enum):
    CLASSROOM = "CLASSROOM"
    LAB = "LAB"
    AUDITORIUM = "AUDITORIUM"
    SEMINAR_HALL = "SEMINAR_HALL"
    CONFERENCE_ROOM = "CONFERENCE_ROOM"


class TimetableStatus(str, Enum):
    DRAFT = "DRAFT"
    PUBLISHED = "PUBLISHED"
    ARCHIVED = "ARCHIVED"


# Persistent models (stored in database)
class Department(SQLModel, table=True):
    __tablename__ = "departments"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=100, unique=True)
    code: str = Field(max_length=10, unique=True)
    description: Optional[str] = Field(default=None, max_length=500)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    semesters: List["Semester"] = Relationship(back_populates="department")
    teachers: List["Teacher"] = Relationship(back_populates="department")
    courses: List["Course"] = Relationship(back_populates="department")
    rooms: List["Room"] = Relationship(back_populates="department")


class Semester(SQLModel, table=True):
    __tablename__ = "semesters"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=50)  # e.g., "Fall 2024", "Semester 1"
    year: int = Field(ge=2020, le=2050)
    semester_number: int = Field(ge=1, le=8)  # 1-8 for typical degree programs
    start_date: datetime = Field()
    end_date: datetime = Field()
    department_id: int = Field(foreign_key="departments.id")
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    department: Department = Relationship(back_populates="semesters")
    sections: List["Section"] = Relationship(back_populates="semester")
    timetables: List["Timetable"] = Relationship(back_populates="semester")


class Section(SQLModel, table=True):
    __tablename__ = "sections"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=10)  # e.g., "A", "B", "CS-A"
    capacity: int = Field(ge=1, le=200)
    semester_id: int = Field(foreign_key="semesters.id")
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    semester: Semester = Relationship(back_populates="sections")
    timetable_entries: List["TimetableEntry"] = Relationship(back_populates="section")


class Teacher(SQLModel, table=True):
    __tablename__ = "teachers"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    employee_id: str = Field(max_length=20, unique=True)
    first_name: str = Field(max_length=50)
    last_name: str = Field(max_length=50)
    email: str = Field(max_length=255, unique=True)
    phone: Optional[str] = Field(default=None, max_length=20)
    department_id: int = Field(foreign_key="departments.id")
    specializations: List[str] = Field(default=[], sa_column=Column(JSON))
    max_hours_per_week: int = Field(default=20, ge=1, le=40)
    preferred_time_slots: List[int] = Field(default=[], sa_column=Column(JSON))  # time_slot IDs
    unavailable_days: List[str] = Field(default=[], sa_column=Column(JSON))  # DayOfWeek values
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    department: Department = Relationship(back_populates="teachers")
    course_assignments: List["CourseAssignment"] = Relationship(back_populates="teacher")
    timetable_entries: List["TimetableEntry"] = Relationship(back_populates="teacher")


class Room(SQLModel, table=True):
    __tablename__ = "rooms"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    room_number: str = Field(max_length=20)
    building: str = Field(max_length=50)
    floor: Optional[int] = Field(default=None)
    capacity: int = Field(ge=1, le=500)
    room_type: RoomType = Field()
    equipment: List[str] = Field(default=[], sa_column=Column(JSON))  # projector, whiteboard, computers, etc.
    department_id: Optional[int] = Field(default=None, foreign_key="departments.id")
    is_available: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    department: Optional[Department] = Relationship(back_populates="rooms")
    timetable_entries: List["TimetableEntry"] = Relationship(back_populates="room")


class Course(SQLModel, table=True):
    __tablename__ = "courses"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    course_code: str = Field(max_length=20, unique=True)
    name: str = Field(max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    credits: int = Field(ge=1, le=10)
    course_type: CourseType = Field()
    hours_per_week: int = Field(ge=1, le=10)
    required_room_type: Optional[RoomType] = Field(default=None)
    required_equipment: List[str] = Field(default=[], sa_column=Column(JSON))
    semester_number: int = Field(ge=1, le=8)  # Which semester this course belongs to
    department_id: int = Field(foreign_key="departments.id")
    prerequisites: List[int] = Field(default=[], sa_column=Column(JSON))  # course IDs
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    department: Department = Relationship(back_populates="courses")
    course_assignments: List["CourseAssignment"] = Relationship(back_populates="course")
    timetable_entries: List["TimetableEntry"] = Relationship(back_populates="course")


class TimeSlot(SQLModel, table=True):
    __tablename__ = "time_slots"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=50)  # e.g., "Period 1", "Morning Lab"
    start_time: time = Field()
    end_time: time = Field()
    day_of_week: DayOfWeek = Field()
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    timetable_entries: List["TimetableEntry"] = Relationship(back_populates="time_slot")


class CourseAssignment(SQLModel, table=True):
    __tablename__ = "course_assignments"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    teacher_id: int = Field(foreign_key="teachers.id")
    course_id: int = Field(foreign_key="courses.id")
    assigned_at: datetime = Field(default_factory=datetime.utcnow)
    is_primary: bool = Field(default=True)  # Primary teacher for the course
    is_active: bool = Field(default=True)

    # Relationships
    teacher: Teacher = Relationship(back_populates="course_assignments")
    course: Course = Relationship(back_populates="course_assignments")


class Timetable(SQLModel, table=True):
    __tablename__ = "timetables"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=100)
    semester_id: int = Field(foreign_key="semesters.id")
    status: TimetableStatus = Field(default=TimetableStatus.DRAFT)
    generation_rules: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    generated_at: Optional[datetime] = Field(default=None)
    generated_by: Optional[str] = Field(default=None, max_length=100)  # User or system info

    # Relationships
    semester: Semester = Relationship(back_populates="timetables")
    timetable_entries: List["TimetableEntry"] = Relationship(back_populates="timetable")


class TimetableEntry(SQLModel, table=True):
    __tablename__ = "timetable_entries"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    timetable_id: int = Field(foreign_key="timetables.id")
    course_id: int = Field(foreign_key="courses.id")
    teacher_id: int = Field(foreign_key="teachers.id")
    room_id: int = Field(foreign_key="rooms.id")
    section_id: int = Field(foreign_key="sections.id")
    time_slot_id: int = Field(foreign_key="time_slots.id")
    notes: Optional[str] = Field(default=None, max_length=500)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    timetable: Timetable = Relationship(back_populates="timetable_entries")
    course: Course = Relationship(back_populates="timetable_entries")
    teacher: Teacher = Relationship(back_populates="timetable_entries")
    room: Room = Relationship(back_populates="timetable_entries")
    section: Section = Relationship(back_populates="timetable_entries")
    time_slot: TimeSlot = Relationship(back_populates="timetable_entries")


# Non-persistent schemas (for validation, forms, API requests/responses)
class DepartmentCreate(SQLModel, table=False):
    name: str = Field(max_length=100)
    code: str = Field(max_length=10)
    description: Optional[str] = Field(default=None, max_length=500)


class DepartmentUpdate(SQLModel, table=False):
    name: Optional[str] = Field(default=None, max_length=100)
    code: Optional[str] = Field(default=None, max_length=10)
    description: Optional[str] = Field(default=None, max_length=500)
    is_active: Optional[bool] = Field(default=None)


class SemesterCreate(SQLModel, table=False):
    name: str = Field(max_length=50)
    year: int = Field(ge=2020, le=2050)
    semester_number: int = Field(ge=1, le=8)
    start_date: datetime
    end_date: datetime
    department_id: int


class SemesterUpdate(SQLModel, table=False):
    name: Optional[str] = Field(default=None, max_length=50)
    year: Optional[int] = Field(default=None, ge=2020, le=2050)
    semester_number: Optional[int] = Field(default=None, ge=1, le=8)
    start_date: Optional[datetime] = Field(default=None)
    end_date: Optional[datetime] = Field(default=None)
    is_active: Optional[bool] = Field(default=None)


class SectionCreate(SQLModel, table=False):
    name: str = Field(max_length=10)
    capacity: int = Field(ge=1, le=200)
    semester_id: int


class SectionUpdate(SQLModel, table=False):
    name: Optional[str] = Field(default=None, max_length=10)
    capacity: Optional[int] = Field(default=None, ge=1, le=200)
    is_active: Optional[bool] = Field(default=None)


class TeacherCreate(SQLModel, table=False):
    employee_id: str = Field(max_length=20)
    first_name: str = Field(max_length=50)
    last_name: str = Field(max_length=50)
    email: str = Field(max_length=255)
    phone: Optional[str] = Field(default=None, max_length=20)
    department_id: int
    specializations: List[str] = Field(default=[])
    max_hours_per_week: int = Field(default=20, ge=1, le=40)
    preferred_time_slots: List[int] = Field(default=[])
    unavailable_days: List[str] = Field(default=[])


class TeacherUpdate(SQLModel, table=False):
    first_name: Optional[str] = Field(default=None, max_length=50)
    last_name: Optional[str] = Field(default=None, max_length=50)
    email: Optional[str] = Field(default=None, max_length=255)
    phone: Optional[str] = Field(default=None, max_length=20)
    specializations: Optional[List[str]] = Field(default=None)
    max_hours_per_week: Optional[int] = Field(default=None, ge=1, le=40)
    preferred_time_slots: Optional[List[int]] = Field(default=None)
    unavailable_days: Optional[List[str]] = Field(default=None)
    is_active: Optional[bool] = Field(default=None)


class RoomCreate(SQLModel, table=False):
    room_number: str = Field(max_length=20)
    building: str = Field(max_length=50)
    floor: Optional[int] = Field(default=None)
    capacity: int = Field(ge=1, le=500)
    room_type: RoomType
    equipment: List[str] = Field(default=[])
    department_id: Optional[int] = Field(default=None)


class RoomUpdate(SQLModel, table=False):
    room_number: Optional[str] = Field(default=None, max_length=20)
    building: Optional[str] = Field(default=None, max_length=50)
    floor: Optional[int] = Field(default=None)
    capacity: Optional[int] = Field(default=None, ge=1, le=500)
    room_type: Optional[RoomType] = Field(default=None)
    equipment: Optional[List[str]] = Field(default=None)
    is_available: Optional[bool] = Field(default=None)


class CourseCreate(SQLModel, table=False):
    course_code: str = Field(max_length=20)
    name: str = Field(max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    credits: int = Field(ge=1, le=10)
    course_type: CourseType
    hours_per_week: int = Field(ge=1, le=10)
    required_room_type: Optional[RoomType] = Field(default=None)
    required_equipment: List[str] = Field(default=[])
    semester_number: int = Field(ge=1, le=8)
    department_id: int
    prerequisites: List[int] = Field(default=[])


class CourseUpdate(SQLModel, table=False):
    name: Optional[str] = Field(default=None, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    credits: Optional[int] = Field(default=None, ge=1, le=10)
    course_type: Optional[CourseType] = Field(default=None)
    hours_per_week: Optional[int] = Field(default=None, ge=1, le=10)
    required_room_type: Optional[RoomType] = Field(default=None)
    required_equipment: Optional[List[str]] = Field(default=None)
    prerequisites: Optional[List[int]] = Field(default=None)
    is_active: Optional[bool] = Field(default=None)


class TimeSlotCreate(SQLModel, table=False):
    name: str = Field(max_length=50)
    start_time: time
    end_time: time
    day_of_week: DayOfWeek


class TimeSlotUpdate(SQLModel, table=False):
    name: Optional[str] = Field(default=None, max_length=50)
    start_time: Optional[time] = Field(default=None)
    end_time: Optional[time] = Field(default=None)
    day_of_week: Optional[DayOfWeek] = Field(default=None)
    is_active: Optional[bool] = Field(default=None)


class CourseAssignmentCreate(SQLModel, table=False):
    teacher_id: int
    course_id: int
    is_primary: bool = Field(default=True)


class TimetableCreate(SQLModel, table=False):
    name: str = Field(max_length=100)
    semester_id: int
    generation_rules: Dict[str, Any] = Field(default={})


class TimetableUpdate(SQLModel, table=False):
    name: Optional[str] = Field(default=None, max_length=100)
    status: Optional[TimetableStatus] = Field(default=None)
    generation_rules: Optional[Dict[str, Any]] = Field(default=None)


class TimetableEntryCreate(SQLModel, table=False):
    timetable_id: int
    course_id: int
    teacher_id: int
    room_id: int
    section_id: int
    time_slot_id: int
    notes: Optional[str] = Field(default=None, max_length=500)


class TimetableEntryUpdate(SQLModel, table=False):
    course_id: Optional[int] = Field(default=None)
    teacher_id: Optional[int] = Field(default=None)
    room_id: Optional[int] = Field(default=None)
    section_id: Optional[int] = Field(default=None)
    time_slot_id: Optional[int] = Field(default=None)
    notes: Optional[str] = Field(default=None, max_length=500)
