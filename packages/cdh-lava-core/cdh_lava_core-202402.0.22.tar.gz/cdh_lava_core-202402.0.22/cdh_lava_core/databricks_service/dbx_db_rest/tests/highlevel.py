# Databricks notebook source
# MAGIC %pip install \
# MAGIC git+https://github.com/cdcent/cdh-ref-gems \
# MAGIC --quiet --disable-pip-version-check

# COMMAND ----------

import unittest

from cdh_lava_core.dbx_db_rest.tests import databricks


class TestHighLevelFeatures(unittest.TestCase):
    """
    General test of API connectivity for each of the main Databricks Workspace Rest APIs.
    """

    def testParentheses(self):
        result = databricks().workspace().ls("/")
        self.assertIsInstance(result, list)

    def testWorkspace(self):
        result = databricks.dbx_workspace.ls("/")
        self.assertIsInstance(result, list)

    def testClusters(self):
        result = databricks.clusters.list()
        self.assertIsNotNone(result)

    def testJobs(self):
        result = databricks.jobs.list()
        self.assertIsInstance(result, list)

    def testPermissions(self):
        jobs = databricks.jobs.list()
        if not jobs:
            return
        job_id = jobs[0]["job_id"]
        result = databricks.permissions.jobs.get(job_id)
        self.assertIsNotNone(result)

    def testPipelines(self):
        result = databricks.pipelines.list()
        self.assertIsInstance(result, list)

    def testRepos(self):
        result = databricks.repos.list()
        self.assertIsNotNone(result)

    def testRuns(self):
        result = databricks.runs.list()
        self.assertIsInstance(result, list)

    def testUsers(self):
        result = databricks.scim.users.list()
        self.assertIsInstance(result, list)

    def testGroups(self):
        result = databricks.scim.groups.list()
        self.assertIsInstance(result, list)

    def testSqlWarehouses(self):
        result = databricks.sql.endpoints.list()
        self.assertIsInstance(result, list)

    def testTokens(self):
        result = databricks.tokens.list()
        self.assertIsInstance(result, list)

    def testLegacyExecuteGet(self):
        """
        Test case for executing a legacy GET request.

        This method tests the functionality of executing a GET request using the legacy API.
        It calls the `databricks.dbx_workspace.get_status` method to get the status of the root directory ("/").
        It then asserts that the object type returned is "DIRECTORY".

        """
        result = databricks.dbx_workspace.get_status("/")
        self.assertEqual(result.get("object_type"), "DIRECTORY")


# COMMAND ----------


def main():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestHighLevelFeatures))
    runner = unittest.TextTestRunner()
    runner.run(suite)


# COMMAND ----------

if __name__ == "__main__":
    main()
