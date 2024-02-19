def create_client():
    from cdh_lava_core.databricks_service.dbx_db_rest import RestClient
    import os
    import configparser

    for path in (".databrickscfg", "~/.databrickscfg"):
        path = os.path.expanduser(path)
        if not os.path.exists(path):
            continue
        config = configparser.ConfigParser()
        config.read(path)
        if "DEFAULT" not in config:
            print("No Default")
            continue
        host = config["DEFAULT"]["host"].rstrip("/")
        token = config["DEFAULT"]["token"]
        return RestClient(token, host)
    return RestClient()


databricks = create_client()

if __name__ == "__main__":
    from cdh_lava_core.dbx_db_rest.tests.all import main

    main()
