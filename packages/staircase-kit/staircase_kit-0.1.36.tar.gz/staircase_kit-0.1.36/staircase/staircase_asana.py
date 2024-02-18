import asana
from typing import Any
from itertools import product
from dataclasses import dataclass
from staircase.lib.fzf import prompt





class StaircaseAsana:
    """Incapsulates interaction with asana"""

    STAIRCASE_WORKSPACE_NAME = "Staircase"
    STAIRCASE_TEAMS = ["moore", "little", "bushnell", "torvalds", "cerf"]

    def __init__(self, token):
        self.client = self.get_client(token)
        # Disable warnings
        self.client.LOG_ASANA_CHANGE_WARNINGS = False

    def get_client(self, token):
        client = asana.Client.access_token(token)
        return client

    def get_staircase_workspace_id(self):
        staircase_ws = list(
            filter(
                lambda e: e["name"] == self.STAIRCASE_WORKSPACE_NAME,
                self.client.workspaces.get_workspaces(),
            )
        )[0]
        return staircase_ws["gid"]

    def get_staircase_teams(self):
        staircase_ws_id = self.get_staircase_workspace_id()
        all_teams = self.client.teams.get_teams_for_workspace(staircase_ws_id)
        staircase_teams = list(filter(lambda team: team['name'] in self.STAIRCASE_TEAMS, all_teams))
        return staircase_teams


    def get_projects_for_team(self, team_name):
        staircase_team = self.get_staircase_team_by_name(team_name)
        projects = self.client.projects.get_projects_for_team(staircase_team["gid"])
        return projects

    def get_staircase_team_by_name(self, team_name):
        staircase_ws_id = self.get_staircase_workspace_id()
        staircase_teams = list(
            self.client.teams.get_teams_for_workspace(staircase_ws_id)
        )
        for team in staircase_teams:
            if team["name"] == team_name:
                return team

    def get_sections_for_project(self, project_id: str):
        sections = list(self.client.sections.get_sections_for_project(project_id))
        return sections


    # def get_staircase_projects(self):
    #     staircase_ws_id = self._get_staircase_workspace_id(self.client)
    #     staircase_projects = list(
    #         self.client.projects.get_projects_for_workspace(staircase_ws_id)
    #     )
    #     return staircase_projects

    # def get_staircase_projects_by_team(self):
    #     staircase_teams = self.get_staircase_teams(self.client)

    #     staircase_projects_by_team = {}
    #     for team in staircase_teams:
    #         projects = list(self.client.projects.get_projects_for_team(team["gid"]))
    #         staircase_projects_by_team[team["name"]] = projects
    #     return staircase_projects_by_team


@dataclass
class BaseSearchByTeam:
    staircase_asana: StaircaseAsana
    team: Any  # Asana team

    @property
    def verbose_name(self):
        team_name = self.team["name"].capitalize()
        return f"{team_name} {self.base_name}"

    def get_id_of_company_team_name(self):
        team_name = self.team["name"]

        ws_id = self.staircase_asana.get_staircase_workspace_id()
        tags = list(self.staircase_asana.client.tags.find_by_workspace(ws_id))
        for tag in tags:
            if tag['name'] == f"company: {team_name}":
                return tag['gid']

    def create_query_params_for_projects(self, section_name):
        team_name = self.team["name"]

        query_parameter = ""

        projects = list(self.staircase_asana.get_projects_for_team(team_name))
        for i, project in enumerate(projects):
            proj_id = project["gid"]
            query_parameter += proj_id

            if section_name:
                sections = self.staircase_asana.get_sections_for_project(project["gid"])
                section = [
                    section for section in sections if section["name"] == section_name
                ][0]
                section_id = section["gid"]
                query_parameter += f"_column_{section_id}"

            is_last_project = i + 1 == len(projects)
            if not is_last_project:
                query_parameter += "~"

        return query_parameter


class TicketsInboxSearch(BaseSearchByTeam):
    base_name = "Tickets Inbox"

    @property
    def search_url(self):
        projects_query = self.create_query_params_for_projects(section_name="Tickets")

        return (
            "https://app.asana.com/0/search?"
            "sort=due_date&"
            "completion=incomplete&"
            "milestone=is_not_milestone&"
            "subtask=is_not_subtask&"
            "not_tags.ids=1202112126062384~1203874644775198&"
            f"any_projects.ids={projects_query}"
        )


class TicketsGroomedSearch(BaseSearchByTeam):
    base_name = "Tickets Groomed"

    @property
    def search_url(self):
        projects_query = self.create_query_params_for_projects(section_name="Tickets")

        return (
            "https://app.asana.com/0/search?"
            "sort=due_date&"
            "completion=incomplete&"
            "milestone=is_not_milestone&"
            "subtask=is_not_subtask&"
            "all_tags.ids=1202112126062384&"
            f"any_projects.ids={projects_query}"
        )


class BacklogSearch(BaseSearchByTeam):
    base_name = "Backlog"

    @property
    def search_url(self):
        projects_query = self.create_query_params_for_projects(section_name="Backlog")

        return (
            "https://app.asana.com/0/search?"
            "sort=due_date&"
            "completion=incomplete&"
            "milestone=is_milestone&"
            "any_tags.ids=1203326207155206&"
            f"any_projects.ids={projects_query}"
        )


class NextSearch(BaseSearchByTeam):
    base_name = "Next"

    @property
    def search_url(self):
        projects_query = self.create_query_params_for_projects(section_name="Next")

        return (
            "https://app.asana.com/0/search?"
            "sort=due_date&"
            "completion=incomplete&"
            "milestone=is_milestone&"
            "any_tags.ids=1202112126062384&"
            f"any_projects.ids={projects_query}"
        )


class InProgressSearch(BaseSearchByTeam):
    base_name = "In Progress"

    @property
    def search_url(self):
        projects_query = self.create_query_params_for_projects(
            section_name="In Progress"
        )

        return (
            "https://app.asana.com/0/search?"
            "sort=due_date&"
            "completion=incomplete&"
            "milestone=is_milestone&"
            "any_tags.ids=1202112126062384&"
            f"any_projects.ids={projects_query}"
        )


class BlockedSearch(BaseSearchByTeam):
    base_name = "Blocked"

    @property
    def search_url(self):
        projects_query = self.create_query_params_for_projects()

        return (
            "https://app.asana.com/0/search?"
            "sort=due_date&"
            "completion=incomplete&"
            "milestone=is_milestone&"
            "any_tags.ids=1199657336606014&"
            "not_tags.ids=1203874644775198&"
            f"any_projects.ids={projects_query}"
        )


class DeliveryAllSearch(BaseSearchByTeam):

    @property
    def verbose_name(self):
        team_name = self.team["name"].capitalize()
        return f" Delivery {team_name}: All"

    @property
    def search_url(self):
        company_team_tag_id = self.get_id_of_company_team_name()

        return (
            "https://app.asana.com/0/search?"
            "sort=due_date&"
            "milestone=is_milestone&"
            f"all_tags.ids=1203332567269502~{company_team_tag_id}&"
            "any_projects.ids=1203875233546411~1203844243602944~1204284245172775~1203877463529063"
        )

class DeliveryBacklogSearch(BaseSearchByTeam):

    @property
    def verbose_name(self):
        team_name = self.team["name"].capitalize()
        return f" Delivery {team_name}: Backlog"

    @property
    def search_url(self):
        company_team_tag_id = self.get_id_of_company_team_name()

        return (
            "https://app.asana.com/0/search?"
            "sort=due_date&"
            "milestone=is_milestone&"
            f"all_tags.ids=1203332567269502~{company_team_tag_id}&"
            "any_projects.ids=1203875233546411_column_1203929848027686~1203844243602944_column_1203929845423949~1204284245172775_column_1204284245172776~1203877463529063_column_1203929848027689"
        )
class DeliveryNextSearch(BaseSearchByTeam):
    @property
    def verbose_name(self):
        team_name = self.team["name"].capitalize()
        return f" Delivery {team_name}: Next"

    @property
    def search_url(self):
        company_team_tag_id = self.get_id_of_company_team_name()

        return (
            "https://app.asana.com/0/search?sort=due_date&"
            "milestone=is_milestone&"
            f"all_tags.ids=1203332567269502~{company_team_tag_id}&"
            "any_projects.ids=1203875233546411_column_1203929848027688~1203844243602944_column_1203929845423951~1204284245172775_column_1204284245172780~1203877463529063_column_1203929848027691"
        )


# Seaches by team name
SEARCHES_BY_TEAM = [
    TicketsInboxSearch,
    TicketsGroomedSearch,
    BacklogSearch,
    NextSearch,
    InProgressSearch,
    # BlockedSearch,
    DeliveryAllSearch,
    DeliveryBacklogSearch,
    DeliveryNextSearch
]

if __name__ == "__main__":
    asana = StaircaseAsana()

    teams = asana.get_staircase_teams()
    teams_names = map(lambda e: e["name"], teams)
    print(teams_names)


