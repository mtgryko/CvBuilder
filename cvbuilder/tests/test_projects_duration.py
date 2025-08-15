from notion.projects import Projects


def test_extract_project_duration():
    notion_data = {
        "results": [
            {
                "properties": {
                    "Project name": {"title": [{"text": {"content": "Test Project"}}]},
                    "Status": {"select": {"name": "Done"}},
                    "Category": {"select": {"name": "AI"}},
                    "Tech Stack": {"multi_select": [{"name": "Python"}]},
                    "Description": {"rich_text": [{"text": {"content": "Desc"}}]},
                    "Detailed Notes": {"rich_text": [{"text": {"content": "Notes"}}]},
                    "Start Date": {"date": {"start": "2023-01-01"}},
                    "End Date": {"date": {"start": "2023-04-01"}},
                    "Role": {"select": {"name": "Dev"}},
                    "Tags": {"multi_select": [{"name": "ML"}]},
                }
            }
        ]
    }
    projects = Projects().extract(notion_data)
    assert projects[0].duration == "3 mo"
    dump = projects[0].model_dump()
    assert "start_date" not in dump and "end_date" not in dump
