from semantha_sdk.api.model_rule import ModelRuleEndpoint
from semantha_sdk.model.rule import Rule
from semantha_sdk.model.rule import RuleSchema
from semantha_sdk.model.rule_overview import RuleOverview
from semantha_sdk.model.rule_overview import RuleOverviewSchema
from semantha_sdk.rest.rest_client import MediaType
from semantha_sdk.rest.rest_client import RestClient, RestEndpoint
from typing import List

class ModelRulesEndpoint(RestEndpoint):
    """ author semantha, this is a generated class do not change manually! 
    
    """

    @property
    def _endpoint(self) -> str:
        return self._parent_endpoint + "/rules"

    def __init__(
        self,
        session: RestClient,
        parent_endpoint: str,
    ) -> None:
        super().__init__(session, parent_endpoint)
    def __call__(
            self,
            id: str,
    ) -> ModelRuleEndpoint:
        return ModelRuleEndpoint(self._session, self._endpoint, id)

    def get(
        self,
    ) -> List[RuleOverview]:
        """
        Get all rules
        Args:
            """
        q_params = {}
    
        return self._session.get(self._endpoint, q_params=q_params, headers=RestClient.to_header(MediaType.JSON)).execute().to(RuleOverviewSchema)

    def post(
        self,
        body: Rule = None,
    ) -> Rule:
        """
        Create a rule
        Args:
        body (Rule): 
        """
        q_params = {}
        response = self._session.post(
            url=self._endpoint,
            json=RuleSchema().dump(body),
            headers=RestClient.to_header(MediaType.JSON),
            q_params=q_params
        ).execute()
        return response.to(RuleSchema)

    
    def delete(
        self,
    ) -> None:
        """
        Delete all rules
        """
        self._session.delete(
            url=self._endpoint,
        ).execute()

    