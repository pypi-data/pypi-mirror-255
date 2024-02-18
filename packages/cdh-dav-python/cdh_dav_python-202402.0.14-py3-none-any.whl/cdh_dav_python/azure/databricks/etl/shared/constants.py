import os

# orchestrator passes this environment variable when invoking jobs
CDH_ENVIRONMENT = os.getenv("CDH_ENVIRONMENT", default="DEV")
   
def get_secret_scope():
    scope = ""
    if CDH_ENVIRONMENT.casefold() == "prod":
        scope = "dbs-scope-prod-kv-CDH"
    else:
        scope =  "dbs-scope-dev-kv-CDH"
     
    print(f"secret scope: {scope}")
    return scope
   