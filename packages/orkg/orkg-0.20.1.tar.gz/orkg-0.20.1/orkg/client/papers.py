import os
import re
from ast import literal_eval
from typing import Dict, List, Optional, Tuple, Union

from deprecated import deprecated
from pandas import read_csv

from orkg.out import OrkgResponse
from orkg.utils import NamespacedClient, dict_to_url_params, query_params


class PapersClient(NamespacedClient):
    def add(
        self, params: Optional[Dict] = None, merge_if_exists: bool = False
    ) -> OrkgResponse:
        """
        Create a new paper in the ORKG instance
        :param params: paper Object
        :param merge_if_exists: merge the papers if they exist in the graph and append contributions
        :return: an OrkgResponse object containing the newly created paper resource
        """
        self.client.backend._append_slash = True
        response = self.client.backend.papers.POST(
            json=params, params={"mergeIfExists": merge_if_exists}, headers=self.auth
        )
        return self.client.wrap_response(response)

    @query_params("file", "standard_statements")
    @deprecated(
        version="0.16.3",
        reason="The CSV import functionality will be removed in a future update :( Please use our lovely frontend instead!",
    )
    def add_csv(self, params: Optional[Dict] = None) -> OrkgResponse:
        """
        Create a new paper in the ORKG instance
        :param file: csv file containing the papers, with at least a column with title: "paper:title"
        :param params: string representation of dict (e.g. "{'name': 1}") with default statements, should contain CSV_PLACEHOLDER (optional)
        :return: OrkgResponse object of the added paper
        """
        if "file" not in params:
            raise ValueError(
                "missing file parameter!, please pass the path to a csv file"
            )
        if not os.path.exists(params["file"]):
            raise ValueError(f"file path doesn't exist!, path={params['file']}")
        df = read_csv(params["file"], dtype=str)
        contribution_ids = []
        for index in range(len(df)):
            paper = df.iloc[index].to_dict()
            # at least a paper title should be present
            if "paper:title" not in paper:  # TODO: enable crossref lookup based on DOI
                print('Skipping paper, column "paper:title" not found')
                continue
            # extract and format paper info
            (
                paper,
                paper_metadata,
                standard_statements,
            ) = PapersClient._get_paper_statements_and_metadata(paper, params)
            # generate the statements
            research_problems, contribution_statements = self._extract_statements(paper)
            # add default statements if they are present
            # TODO: only works for one level now, make it recursive
            statements_to_insert = standard_statements.copy()
            if len(statements_to_insert) > 0:
                contribution_statements = self._insert_standard_statements(
                    contribution_statements, statements_to_insert
                )
            # add research problem to the contribution
            if len(research_problems) > 0:
                contribution_statements = self._insert_research_problem(
                    contribution_statements, research_problems
                )
            # check if a paper with this title already exists
            existing_papers = self.client.resources.get(
                q=paper_metadata["title"], exact=True
            ).content
            existing_paper_id = 0
            for existing_paper in existing_papers:
                if "Paper" in existing_paper["classes"]:
                    existing_paper_id = existing_paper["id"]
                    break
            # paper does not yet exist
            if existing_paper_id == 0:
                paper_metadata["contributions"] = [
                    {"name": "Contribution 1", "values": contribution_statements}
                ]
                paper = {
                    "paper": paper_metadata  # now the full paper, not just metadata
                }
                contribution_ids = self._add_new_paper(contribution_ids, paper)
            # paper exists already, so add a contribution
            else:
                contribution_ids = self._add_new_contribution(
                    contribution_ids, contribution_statements, existing_paper_id
                )
        return self.client.wrap_response(content=contribution_ids, status_code="201")

    def by_doi(self, doi: str) -> OrkgResponse:
        """
        Get the paper resource in the ORKG associated with the given DOI.
        :param doi: The DOI of the paper, could be a full url or just the DOI
        :return: A list of paper objects
        """
        # Disable appending a slash to the base URL
        self.client.backend._append_slash = False

        # Extract the DOI from the input if it's a full URL
        if "doi.org" in doi:
            doi = doi.split("doi.org/")[-1]

        # Send an HTTP GET request to fetch paper information
        response = self.client.backend.papers.GET(params={"doi": doi})

        return self.client.wrap_response(response)

    def by_title(self, title: str) -> OrkgResponse:
        """
        Retrieve a paper object based on its title.
        :param title: The title of the research paper.
        :return: A list of paper objects
        """
        # Disable appending a slash to the base URL
        self.client.backend._append_slash = False

        # Send an HTTP GET request to fetch paper information
        response = self.client.backend.papers.GET(params={"title": title})

        return self.client.wrap_response(response)

    @query_params("page", "size", "sort", "desc")
    def in_research_field(
        self,
        research_field_id: str,
        include_subfields: Optional[bool] = False,
        params: Optional[Dict] = None,
    ) -> OrkgResponse:
        """
        Get all papers in a research field
        :param research_field_id: the id of the research field
        :param include_subfields: True/False whether to include papers from subfields, default is False (optional)
        :param page: the page number (optional)
        :param size: number of items per page (optional)
        :param sort: key to sort on (optional)
        :param desc: true/false to sort desc (optional)
        :return: OrkgResponse object
        """
        url = self.client.backend("research-fields")(research_field_id)
        if include_subfields:
            url = url.subfields.papers
        else:
            url = url.papers
        if len(params) > 0:
            self.client.backend._append_slash = False
            response = url.GET(dict_to_url_params(params))
        else:
            self.client.backend._append_slash = True
            response = url.GET()
        return self.client.wrap_response(response)

    @staticmethod
    def _get_paper_statements_and_metadata(
        paper: Dict, params: Dict
    ) -> Tuple[Dict, Dict, Dict]:
        """
        Format paper statement values and add default values for missing data.
        Separate into dictionaries for statements and metadata.

        :param paper: dict of all info extracted from csv file
        :param params: string representation of dict (e.g. "{'name': 1}") dict with default statements, should contain CSV_PLACEHOLDER (optional)
        :return:
            - dict of paper statements (without metadata)
            - dict of paper metadata
            - dict of standard statements or empty dict if no standard statements
        """
        title = paper["paper:title"]
        authors = (
            [
                {"label": author.strip()}
                for author in str(paper["paper:authors"]).split(";")
            ]
            if "paper:authors" in paper
            and paper["paper:authors"] == paper["paper:authors"]
            else []
        )
        publication_month = paper.get("paper:publication_month", 1)
        publication_year = paper.get("paper:publication_year", 2000)
        research_field = paper.get("paper:research_field", "R11")  # "Science"
        doi = paper.get("paper:doi", "")
        url = ""
        published_in = ""
        paper_metadata = {
            "title": title,
            "authors": authors,
            "publicationMonth": publication_month,
            "publicationYear": publication_year,
            "researchField": research_field,
            "doi": doi,
            "url": url,
            "publishedIn": published_in,
        }
        standard_statements = (
            literal_eval(params["standard_statements"])
            if "standard_statements" in params
            else {}
        )
        # remove metadata from paper dict, already added above
        metadata_headers = [
            "paper:title",
            "paper:authors",
            "paper:publication_month",
            "paper:publication_year",
            "paper:doi",
            "paper:research_field",
        ]
        [paper.pop(key) if key in paper else paper for key in metadata_headers]
        return paper, paper_metadata, standard_statements

    def _add_new_paper(self, contribution_ids: List, paper: Dict) -> List:
        """
        Add new paper to ORKG instance and add contribution ID to list.

        :param contribution_ids: list of contribution ID strings
        :param paper: dict of paper statements and metadata
        :return: updated list of contribution ID strings
        """
        response = self.add(paper)
        if "id" in response.content:
            paper_id = response.content["id"]
            paper_statements = self.client.statements.get_by_subject(
                subject_id=paper_id, size=10000
            ).content
            for statement in paper_statements:
                if statement["predicate"]["id"] == "P31":
                    contribution_ids.append(statement["object"]["id"])
                    print("Added paper:", str(paper_id))
        else:
            print("Error adding paper: ", str(response.content))
        return contribution_ids

    def _add_new_contribution(
        self,
        contribution_ids: List,
        contribution_statements: Dict[str, List],
        existing_paper_id: str,
    ) -> List:
        """
        Add contribution to existing paper in ORKG instance and add contribution ID to list.

        :param contribution_ids: list of contribution ID strings
        :param contribution_statements: dict of predicate IDs and their objects
        :param existing_paper_id: paper ID string
        :return: updated list of contribution ID strings
        """
        paper_statements = self.client.statements.get_by_subject(
            subject_id=existing_paper_id, size=10000
        ).content
        contribution_amount = 0
        for paper_statement in paper_statements:
            if paper_statement["predicate"]["id"] == "P31":  # "Contribution"
                contribution_amount += 1
        contribution_id = self.client.resources.add(
            label="Contribution " + str(contribution_amount + 1),
            classes=["Contribution"],
        ).content["id"]
        self.client.statements.add(
            subject_id=existing_paper_id,
            predicate_id="P31",
            object_id=contribution_id,
        )
        self._create_statements(contribution_id, contribution_statements)
        contribution_ids.append(contribution_id)
        print(
            "Added contribution:",
            str(contribution_id),
            "to paper:",
            str(existing_paper_id),
        )
        return contribution_ids

    def _insert_research_problem(
        self, contribution_statements: Dict[str, List], research_problems: List[str]
    ) -> Dict[str, List]:
        """
        Add research problem(s) by resource ID to contribution statements dictionary.

        :param contribution_statements: dict of predicate IDs and their objects
        :param research_problems: list of (one or many) research problem(s) as strings
        :return: updated dict of contribution statements
        """
        contribution_statements["P32"] = []
        for research_problem in research_problems:
            research_problem_id = self.client.resources.find_or_add(
                label=research_problem, classes=["Problem"]
            ).content["id"]
            # P32 has research problem
            contribution_statements["P32"].append({"@id": research_problem_id})
        return contribution_statements

    def _insert_standard_statements(
        self, contribution_statements: Dict[str, List], statements_to_insert: Dict
    ) -> Dict[str, Union[str, List]]:
        """
        Create new standard statements dict with predicate IDs as keys and predicate labels as values.

        :param contribution_statements: dict of predicate IDs and their objects
        :param statements_to_insert: dict with default statements, should contain CSV_PLACEHOLDER
        :return: dict of standard statements' predicate IDs to predicate labels
        """
        for predicate in statements_to_insert:
            if isinstance(statements_to_insert[predicate], list):  # if is array
                for i in range(len(statements_to_insert[predicate])):
                    if (
                        statements_to_insert[predicate][i]["values"]
                        == "CSV_PLACEHOLDER"
                    ):
                        statements_to_insert[predicate][i][
                            "values"
                        ] = contribution_statements
            if not re.search("^P+[a-zA-Z0-9]*$", predicate):
                predicate_id = self.client.predicates.find_or_add(
                    label=predicate
                ).content["id"]
                statements_to_insert[predicate_id] = statements_to_insert[predicate]
                del statements_to_insert[predicate]
        return statements_to_insert

    def _extract_statements(self, paper: Dict) -> Tuple[List[str], Dict]:
        """
        Create a dictionary of predicate-object pairs formatted/typed for the ORKG.
        Predicates: find an existing ID matching the label, or create a new one.
        Objects: if resource, find an existing ID matching the label, or create a new one. Otherwise, add as literal.
        Also creates a list of research problem label(s).

        :param paper: dict of paper statements as extracted from CSV
        :return:
            - list of research problem label(s)
            - dict of predicate IDs and their objects
        """
        contribution_statements = {}
        research_problems = []
        for predicate in paper:
            value = paper[predicate]
            # add research problem (one or more)
            if predicate.startswith("contribution:research_problem"):
                research_problem = paper.get("predicate", "")
                if research_problem != "":
                    research_problems.append(research_problem)
                continue
            # filter out nan values
            if value != value:
                continue
            # to make columns unique, pandas appends a dot and number to duplicate columns, remove this here
            predicate = re.sub(r"\.[1-9]+$", "", predicate)
            value_is_resource = False
            # if predicate starts with resource:, insert it as resource instead of literal
            if predicate.startswith("resource:"):
                value_is_resource = True
                predicate = predicate[len("resource:") :]
            predicate_id = self.client.predicates.find_or_add(label=predicate).content[
                "id"
            ]
            if not value_is_resource:
                if predicate_id in contribution_statements:
                    contribution_statements[predicate_id].append({"text": value})
                else:
                    contribution_statements[predicate_id] = [{"text": value}]
            else:
                resource_id = self.client.resources.find_or_add(label=value).content[
                    "id"
                ]
                if predicate_id in contribution_statements:
                    contribution_statements[predicate_id].append({"@id": resource_id})
                else:
                    contribution_statements[predicate_id] = [{"@id": resource_id}]
        return research_problems, contribution_statements

    def _create_statements(self, subject_id: str, statements: Dict):
        """
        Add statements to ORKG instance.

        :param subject_id: string of subject resource ID
        :param statements: dict of predicate IDs and their objects
        """
        for predicate_id in statements:
            values = statements[predicate_id]
            for value in values:
                if "text" in value:
                    literal_id = self.client.literals.add(label=value["text"]).content[
                        "id"
                    ]
                    self.client.statements.add(
                        subject_id=subject_id,
                        predicate_id=predicate_id,
                        object_id=literal_id,
                    )
                elif "@id" in value:
                    self.client.statements.add(
                        subject_id=subject_id,
                        predicate_id=predicate_id,
                        object_id=value["@id"],
                    )
                elif "label" in value:
                    resource_id = self.client.resources.add(
                        label=value["label"]
                    ).content["id"]
                    self.client.statements.add(
                        subject_id=subject_id,
                        predicate_id=predicate_id,
                        object_id=resource_id,
                    )
                    self._create_statements(resource_id, value["values"])
