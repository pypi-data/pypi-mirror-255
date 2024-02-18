def create_client():
    from cdh_ref_python.dbx_db_rest import cdh_ref_pythonRestClient
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
        return cdh_ref_pythonRestClient(token, host)
    return cdh_ref_pythonRestClient()


databricks = create_client()

if __name__ == "__main__":
    from cdh_ref_python.dbx_db_rest.tests.all import main

    main()
