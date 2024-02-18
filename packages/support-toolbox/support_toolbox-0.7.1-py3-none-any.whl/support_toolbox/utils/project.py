import requests
import json

IMPLEMENTATION_QUERIES = [
    {
        "name": "01. First Login",
        "content": """
SELECT
displayname as UserID,
onboard_date as Firstlogin

FROM membership_current_last_90_days

WHERE email not like '%data.world%'

group BY
displayname,
onboard_date

order by 2,1 ASC""",
        "language": "SQL",
        "published": True
    },
    {
        "name": "02. Days Since Last Activity",
        "content": """
SELECT
displayname as User,
min(DATE_DIFF(lastseen, now() ,"day")) as days_since_active

From membership_current_by_org_last_90_days

Where email not like '%@data.world%'

Group by 
displayname

order by 2 ASCSample""",
        "language": "SQL",
        "published": True
    },
    {
        "name": "10. Views, Edits, and Creates Last 7 Days",
        "content": """
SELECT
owner as org,
displayname as user_id,
sum(views) as Resources_Viewed,
sum(Edits)as Resources_Edited,
sum(creates) as Resources_Created

FROM events_catalog_resources_pages_activity_by_day_last_90_days e
    INNER JOIN membership_current_last_90_days m ON e.agentid = m.agentid

WHERE email not like '%data.world%' and DATE_DIFF(DATE,NOW(),"day")<7

Group BY
Owner,
displayname

order by 1,2 ASC""",
        "language": "SQL",
        "published": True
    },
    {
        "name": "11. Production Catalog Resources Created and Edited last 7 days",
        "content": """
SELECT
case when creates > 0 then "Created" when edits > 0 then "Edited" else NULL END as Activity,
owner as Org,
date,
displayname as User_Id,
resourcetype as Resource_Type,
resourcename as Resource_Name

FROM events_catalog_resources_pages_activity_by_day_last_90_days e
    INNER JOIN membership_current_last_90_days m ON e.agentid = m.agentid

where (creates >0 or edits >0) and email not like '%data.world%'and owner like '%main%' and DATE_DIFF(DATE,NOW(),"day")<7

order by 1,2,3,4,5,6 ASC""",
        "language": "SQL",
        "published": True
    },
    {
        "name": "12. Suggestion Status",
        "content": """
SELECT 
e.event_date_utc as DATE,
e.org as Org,
m.displayname as Suggestor,
e.event_type Event_Type, 
suggestion_completedby as Suggestion_closed_by,
  CASE
    WHEN g.current_value LIKE '%://%'THEN REGEXP_REPLACE(g.current_value, '^.*/', '')
    ELSE g.current_value
  END AS Original_Value,
#current_value as original_value,
  CASE
    WHEN g.value LIKE '%://%'THEN REGEXP_REPLACE(g.value, '^.*/', '')
    ELSE g.value
  END AS New_Value
 #value as New_value

FROM audit_events_last_90_days e
    INNER JOIN membership_current_last_90_days m ON e.suggestion_requestor = m.agentid
    Inner JOIN audit_events_with_changes_last_90_days g on e.id = g.event_id

WHERE e.suggestion_id is not NULL""",
        "language": "SQL",
        "published": True
    },
    {
        "name": "20. [Last 90 Days] Production Catalog Resources Created and Edited by Date",
        "content": """
SELECT
case when creates > 0 then "Created" when edits > 0 then "Edited" else NULL END as Activity,
owner as Org,
date,
displayname as User_Id,
resourcetype as Resource_Type,
resourcename as Resource_Name

FROM events_catalog_resources_pages_activity_by_day_last_90_days e
    INNER JOIN membership_current_last_90_days m ON e.agentid = m.agentid

where (creates >0 or edits >0) and email not like '%data.world%'and owner like 'main'

order by 1,2,3,4,5,6 ASC""",
        "language": "SQL",
        "published": True
    },
    {
        "name": "30. Files uploaded to Datasets and Projects",
        "content": """
Select
rdf.owner as Org,
cdp.resource as `Dataset | Project Name`,
cdp.type as `Location Type`,
case 
    when rdf.file_materialized_or_virtualized like 'materialized' then 'stored in platform' else 'Virtualized'
end as `Mechanism`,
case 
    when cast(rdf.is_file_discoverable as string)  like 'true' then 'discoverable' else 'hidden'
end as `Status`,
displayname as `Uploaded By`,
rdf.file_created_date as `Date Uploaded`,
rdf.file_name as `File Name`,
concat (round (rdf.file_size_in_bytes/1000000,3),"Mb") as `File Size`, 
dsv.versionid as `Current Version ID`,
dsv.previousversionid as `Previous Version ID`,
case 
    when dsv.previousversionid is NOT NULL then DATE_FORMAT(dsv.updated, "yyyy.mm.dd") else "N/A"
end as `Updated On`

from events_create_dataset_project_events as cdp 
    join resources_dataset_files as rdf on rdf.resourceid = cdp.resourceid
    join membership_all_time_list as ma on file_createdby_agentid = ma.agentid 
    join datasetversions_last_90_days as dsv on agentdatasetid = CONCAT(rdf.owner,':',rdf.resource)

where cdp.email not like '%data%'
    and rdf.file_name not like '.data%'
    and rdf.file_materialized_or_virtualized like 'materialized'

order by 1,2,3,7 ASC""",
        "language": "SQL",
        "published": True
    }
]

summary = """
# *Project Team*

## *[data.world](http://data.world/) Team*

- *<name> - Project Manager (PM) |@Tag | Email*
- *<name> - Solution Architect (SA) | @Tag | Email*
- *<name> - Customer Success Director (CSD) | @Tag | Email*

## *<Customer> Team*

- *Name - Role/Title | @Tag | Email*
- *Name - Role/Title | @Tag | Email*
- *Name - Role/Title | @Tag | Email*

# *Project Plan*

## *Typical Implementation Overview*

*<insert diagram>*

## *<Customer> Project Schedule*

*<Insert Gantt Chart>*

# *Project Files*

- *Scope Acknowledgement*
- *Project Management Plan*
- *Initial Schedule*
- *Final Schedule*
- *Detailed Implementation Plan*
- *Project Kick-off Slide Deck*
- *Project Summary Doc*

# *Helpful Links*

- *[data.world University - Onboarding](https://university.data.world/page/customer-onboarding)*
- *[data.world connection manager setup](https://implementation.data.world/docs/collect-metadata-using-connection-manager)*
- *[data.world collector setup](https://docs.data.world/en/98627-connect-to-data.html#UUID-546857a2-0226-3d5e-cb99-0e81d072b63b)*
- *[Catalog Toolkit - source and metadata profile configuration](https://docs.data.world/en/201702-about-catalog-toolkit.html)*
- *[Eureka Automations](https://docs.data.world/en/203152-configure-eureka-automations.html)*
- *[Eureka Action Center](https://docs.data.world/en/98583-home-page.html)*
- *[Browse Card Setup - Organization](https://docs.data.world/en/200191-browse-card-for-organization-profile-pages.html)*
- *[Metrics](https://docs.data.world/en/114572-metrics-and-auditing.html)*

# *Status Reports*

- <date> - Status Report
- <date> - Status Report

# *Workshop/ Meeting Recordings:*

- <date> - data.world | <Customer> | <Meeting Description>
- <date> - data.world | <Customer> | <Meeting Description>
- <date> - data.world | <Customer> | <Meeting Description>

# *Support Tickets & Feature/ Enhancement Requests*

- *DWS-<Ticket #> - <Type> - <Short Description>*
"""


def create_saved_query(admin_token, q, org_id, project_id):
    create_saved_query_url = f"https://api.data.world/v0/projects/{org_id}/{project_id}/queries"

    header = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {admin_token}'
    }

    body = json.dumps(q)

    # Create the query
    response = requests.post(create_saved_query_url, body, headers=header)

    # Verify the creation
    if response.status_code == 200:
        response_json = response.json()
        print(response_json)
    else:
        print(response.text)


def create_project(admin_token, org_id, project_title, visibility):
    create_project_url = f"https://api.data.world/v0/projects/{org_id}"

    header = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {admin_token}'
    }

    payload = {
        "title": project_title,
        "summary": summary,
        "visibility": visibility
    }

    body = json.dumps(payload)

    # Create the project
    response = requests.post(create_project_url, body, headers=header)

    # Verify the creation
    if response.status_code == 200:
        print(f"created project: {project_title}")
    else:
        print(response.text)


def setup_implementation_project(admin_token, org_id, public_slug, visibility):
    project_title = f"{public_slug} Implementation Project"
    create_project(admin_token, org_id, project_title, visibility)

    project_id = project_title.replace(" ", "-").lower()
    for q in IMPLEMENTATION_QUERIES:
        create_saved_query(admin_token, q, org_id, project_id)
