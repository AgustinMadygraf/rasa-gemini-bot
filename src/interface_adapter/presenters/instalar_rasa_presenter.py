"""
Path: src/interface_adapter/presenters/instalar_rasa_presenter.py
"""
class InstalarRasaPresenter:
    "Presentador para mensajes de instalación de Rasa y Git"
    @staticmethod
    def mensaje_pregunta_proyecto_descargado():
        "Pregunta si el proyecto ha sido descargado"
        return {"response": "utter_ask_proyecto_descargado"}

    @staticmethod
    def mensaje_guia_clonar_proyecto():
        "Guía para clonar el proyecto"
        return {"response": "utter_guia_clonar_proyecto"}

    @staticmethod
    def mensaje_git_requerido():
        "Mensaje indicando que Git es requerido"
        return {"text": "Primero necesitarás instalar Git para poder descargar el proyecto."}
