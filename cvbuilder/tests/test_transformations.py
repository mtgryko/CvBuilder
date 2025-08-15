import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from notion.education import EducationClient
from notion.experience import ExperienceClient


def test_education_transform():
    client = EducationClient()
    data = [
        {
            "level": "Bachelor",
            "university": "MIT",
            "field": "Computer Science",
            "specialization": "AI",
            "start_date": "2018",
            "end_date": "2022",
            "duration_years": 4,
        }
    ]
    transformed = client.transform_for_latex(data)
    assert transformed == [
        {
            "school": "MIT",
            "degree": "Bachelor in Computer Science",
            "details": "Specialization in AI [4 years]",
            "dates": "2018 – 2022",
        }
    ]


def test_experience_transform():
    client = ExperienceClient()
    data = [
        {
            "role": "Engineer",
            "company": "Acme",
            "start_date": "2020",
            "end_date": None,
            "employment_type": "Full-time",
            "duration": "1 yr",
        }
    ]
    transformed = client.transform_for_latex(data)
    assert transformed == [
        {
            "company": "Acme",
            "position": "Engineer",
            "description": "Full-time – 1 yr",
            "dates": "2020 – Present",
        }
    ]

