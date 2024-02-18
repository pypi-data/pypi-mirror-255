import jmespath
from convisoappsec.flow.graphql_api.beta.models.issues.iac import CreateIacFindingInput
from convisoappsec.flow.graphql_api.beta.models.issues.sast import CreateSastFindingInput
from convisoappsec.flow.graphql_api.beta.models.issues.sca import CreateScaFindingInput
from convisoappsec.flow.graphql_api.beta.schemas import mutations
from convisoappsec.flow.graphql_api.v1.schemas import resolvers


class IssuesAPI(object):
    """ To operations on Issues's (aka, findings and vulnerabilities)) in Conviso Platform. """

    def __init__(self, conviso_graphql_client):
        self.__conviso_graphql_client = conviso_graphql_client

    def create_sast(self, sast_issue_model: CreateSastFindingInput):
        graphql_variables = {
            "input": sast_issue_model.to_graphql_dict()
        }

        graphql_body_response = self.__conviso_graphql_client.execute(
            mutations.CREATE_SAST_FINDING_INPUT,
            graphql_variables
        )

        expected_path = 'createSastFinding.issue'

        issue = jmespath.search(
            expected_path,
            graphql_body_response,
        )

        return issue

    def create_sca(self, sca_issue_model: CreateScaFindingInput):
        graphql_variables = {
            "input": sca_issue_model.to_graphql_dict()
        }

        graphql_body_response = self.__conviso_graphql_client.execute(
            mutations.CREATE_SCA_FINDING_INPUT,
            graphql_variables
        )

        expected_path = 'createScaFinding.issue'

        issue = jmespath.search(
            expected_path,
            graphql_body_response,
        )

        return issue

    def create_iac(self, issue_model: CreateIacFindingInput):
        graphql_variables = {
            "input": issue_model.to_graphql_dict()
        }

        graphql_body_response = self.__conviso_graphql_client.execute(
            mutations.CREATE_SAST_FINDING_INPUT,
            graphql_variables
        )

        expected_path = 'createSastFinding.issue'

        issue = jmespath.search(
            expected_path,
            graphql_body_response,
        )

        return issue

    def auto_close_vulnerabilities(self, company_id, asset_id, vulnerability_type):
        """ entry point for auto closing vulnerabilities on conviso platform """
        graphql_variables = {
            'company_id': company_id,
            'asset_id': asset_id,
            'page': 1,
            'per_page': 100,
            'statuses': ['CREATED', 'IDENTIFIED', 'IN_PROGRESS', 'AWAITING_VALIDATION'],
            'failure_types': [vulnerability_type]
        }

        graphql_body_response = self.__conviso_graphql_client.execute(
            resolvers.GET_ISSUES_FINGERPRINT,
            graphql_variables
        )

        expected_path = 'issues.collection'

        issues = jmespath.search(
            expected_path,
            graphql_body_response
        )

        return issues

    def update_issue_status(self, issue_id):
        """ Update issue status on conviso platform """

        graphql_variables = {
            'issueId': issue_id,
            'status': 'FIX_ACCEPTED',
            'reason': 'Status changed by Conviso AST.'
        }

        graphql_body_response = self.__conviso_graphql_client.execute(
            mutations.UPDATE_ISSUE_STATUS,
            graphql_variables
        )

        expected_path = 'changeIssueStatus.issue'

        issue = jmespath.search(
            expected_path,
            graphql_body_response,
        )

        return issue
