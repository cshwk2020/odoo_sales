import os
import hvac

client = hvac.Client(
    url=os.environ["VAULT_ADDR"],
    token=os.environ["VAULT_TOKEN"]
)

#
def vault_get_secret(path):
    return client.secrets.kv.read_secret_version(path=path)["data"]["data"]


def vault_get_odoo_user():
   
    app_secrets = vault_get_secret("app")
    odoo_user = app_secrets["odoo_user"]
    print("Odoo user:", odoo_user)
    return odoo_user
  
 
def vault_get_odoo_pass():
 
    app_secrets = vault_get_secret("app")
    odoo_pass = app_secrets["odoo_pass"]
    print("Odoo pass:", odoo_pass)
    return odoo_pass
 
 
def vault_get_deepseek_key():
 
    app_secrets = vault_get_secret("app")
    deepseek_key = app_secrets["deepseek_key"]
    print("DeepSeek key:", deepseek_key)
    return deepseek_key



