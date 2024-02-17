from typing import Dict, List, Optional, Tuple

from orkg.common import ComparisonType, ThingType
from orkg.out import OrkgResponse
from orkg.utils import NamespacedClient, dict_to_url_params, query_params


class ComparisonsClient(NamespacedClient):
    def publish(
        self,
        contribution_ids: Optional[List[str]] = None,
        title: Optional[str] = None,
        description: Optional[str] = None,
        reference: Optional[str] = None,
        comparison_method: ComparisonType = ComparisonType.PATH,
        predicates: Optional[List[str]] = None,
        transposed: bool = False,
        data: Optional[Dict] = None,
    ) -> OrkgResponse:
        """
        Create a comparison resource in backend and a corresponding thing reference in SimComp
        :param contribution_ids: a list of contributions' ids to compare (optional)
        :param title: the title of the comparison
        :param description: the description of the comparison (optional)
        :param reference: the reference of the comparison (optional)
        :param comparison_method: the method used to compare the contributions - PATH or MERGE (default: PATH)
        :param predicates: the list predicates to strict the comparison view (optional)
        :param transposed: whether to transpose the comparison view (default: False)
        :param data: the data of the comparison - should be valid data according to SimComp specifications (optional)
        :return: the response of the request
        """
        if title is None:
            raise ValueError("title should be provided")

        if contribution_ids is None and data is None:
            raise ValueError(
                "either contribution_ids or precomputed data should be provided"
            )

        description, reference = self._validate_comparison_components(
            contribution_ids, description, reference
        )
        comparison_id, comparison_response = self._create_comparison_in_graph(
            title, description, reference, contribution_ids
        )

        self._save_comparison_to_simcomp(
            comparison_id,
            contribution_ids,
            comparison_method,
            predicates,
            transposed,
            data,
        )

        return comparison_response

    @query_params("page", "size", "sort", "desc")
    def in_research_field(
        self,
        research_field_id: str,
        include_subfields: Optional[bool] = False,
        params: Optional[Dict] = None,
    ) -> OrkgResponse:
        """
        Get all comparisons in a research field
        :param research_field_id: the id of the research field
        :param include_subfields: True/False whether to include comparisons from subfields, default is False (optional)
        :param page: the page number (optional)
        :param size: number of items per page (optional)
        :param sort: key to sort on (optional)
        :param desc: true/false to sort desc (optional)
        :return: OrkgResponse object
        """
        url = self.client.backend("research-fields")(research_field_id)
        if include_subfields:
            url = url.subfields.comparisons
        else:
            url = url.comparisons
        if len(params) > 0:
            self.client.backend._append_slash = False
            response = url.GET(dict_to_url_params(params))
        else:
            self.client.backend._append_slash = True
            response = url.GET()
        return self.client.wrap_response(response)

    def _create_comparison_in_graph(
        self,
        title: str,
        description: str,
        reference: str,
        contribution_ids: Optional[List[str]],
    ) -> Tuple[str, OrkgResponse]:
        """
        Create a comparison resource in ORKG
        :param title: the title of the comparison
        :param description: the description of the comparison
        :param reference: the reference of the comparison
        :param contribution_ids: a list of contributions' ids to compare (optional)
        :return: the id of the comparison and the response of the request
        """
        # create the comparison resource
        comparison_response = self.client.resources.add(
            label=title, classes=["Comparison"]
        )
        # create the literals
        comparison_id = comparison_response.content["id"]
        description_id = self.client.literals.add(label=description).content["id"]
        reference_id = self.client.literals.add(label=reference).content["id"]
        # add the statements
        self.client.statements.add(
            subject_id=comparison_id,
            predicate_id="description",
            object_id=description_id,
        )
        self.client.statements.add(
            subject_id=comparison_id, predicate_id="reference", object_id=reference_id
        )
        # If a list of contributions is provided, add them to the comparison
        if contribution_ids is not None:
            for contribution_id in contribution_ids:
                self.client.statements.add(
                    subject_id=comparison_id,
                    predicate_id="compareContribution",
                    object_id=contribution_id,
                )
        return comparison_id, comparison_response

    def _validate_comparison_components(
        self,
        contribution_ids: Optional[List[str]],
        description: Optional[str],
        reference: Optional[str],
    ) -> Tuple[str, str]:
        """
        Validate the components of the comparison
        :param contribution_ids: a list of contributions' ids to compare
        :param description: the description of the comparison (optional)
        :param reference: the reference of the comparison (optional)
        :return: the validated description and reference of the comparison
        """
        if contribution_ids is not None:
            for contribution_id in contribution_ids:
                contribution_resource = self.client.resources.by_id(
                    id=contribution_id
                ).content

                if "Contribution" not in contribution_resource["classes"]:
                    raise ValueError(
                        "this ID is not a contribution: " + str(contribution_id)
                    )
        description = description if description is not None else ""
        reference = reference if reference is not None else ""
        return description, reference

    def _save_comparison_to_simcomp(
        self,
        comparison_id: str,
        contribution_ids: List[str],
        comparison_type: ComparisonType,
        predicates: Optional[List[str]],
        transposed: bool,
        data: Optional[Dict],
    ):
        """
        Save the comparison to SimComp. Either computes a fresh comparison or uses the provided data
        :param comparison_id: the id of the comparison
        :param contribution_ids: a list of contributions' ids to compare
        :param comparison_type: the method used to compare the contributions - PATH or MERGE
        :param predicates: the list predicates that customize the comparison view (optional)
        :param transposed: whether to transpose the comparison view
        :param data: the data of the comparison - should be valid data according to SimComp specifications (optional)
        """
        if data is None:
            # Compute a fresh comparison
            data = self.client.contributions.compare(
                contributions=contribution_ids,
                comparison_type=comparison_type,
            ).content["payload"]["comparison"]
        # Use the provided data
        config = {
            "contributions": contribution_ids,
            "transpose": transposed,
            "type": comparison_type.value.upper().strip(),
        }
        if predicates is not None:
            config["predicates"] = predicates
        self.client.json.save_json(
            thing_key=comparison_id,
            thing_type=ThingType.COMPARISON,
            data=data,
            config=config,
        )
