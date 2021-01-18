import connexion


def pico_post(body):
    return "Success"


options = {"swagger_ui": True}
app = connexion.App(__name__, specification_dir="openapi/", options=options)
app.add_api("picostatement.yaml")
app.run(port=8088)
