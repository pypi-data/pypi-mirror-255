CLUSTER_PASS_THROUGH_CREDS_SPARK_CONF_DEFAULT = """
                        "spark.databricks.cluster.profile": "serverless",
                        "spark.databricks.passthrough.enabled": "true",
                        "spark.databricks.delta.preview.enabled": "true",
                        "spark.databricks.pyspark.enableProcessIsolation": "true",
                        "spark.driver.maxResultSize": "16g",
                        "spark.databricks.service.server.enabled": "true",
                        "spark.databricks.repl.allowedLanguages": "python,sql"
                        """


CLUSTER_NON_PASS_THROUGH_CREDS_SPARK_CONF = """
                        "spark.databricks.delta.preview.enabled": "true",
                        "spark.driver.maxResultSize": "16g",
                        "spark.databricks.repl.allowedLanguages": "python,sql"
                        """