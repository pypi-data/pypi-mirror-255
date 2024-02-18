from fastapi  import FastAPI, APIRouter
from .routes  import router
from .handler import BaseModelHandler




class ModelServer():
    def _setup_routes(self, app: FastAPI, routers: list[APIRouter]) -> None:
        """
        Helper to add all defined routes.

        Args:
            app(FastAPI):
            The FastAPI instance.

            routers(list[APIRouter]):
            List of FastAPI routers defined by routes.
        """
        for router in routers:
            app.include_router(router)

    def _create_model_server(self, model_handler: BaseModelHandler, model_path: str | None = None):
        """
        FastAPI application factory.

        Returns:
            FastAPI instance.
        """
        app = FastAPI(
            title   = 'Cortex FastAPI model server',
            version = '1.24.0'
        )

        # Requests will have a reference to the underlying FastAPI application.
        # We use this to store a few piece of data rather than jumping through
        # dependency injection hoops.
        app.model_handler  = model_handler
        app.model_instance = model_handler.load(model_path)

        self._setup_routes(app, [router])
        return app

    #---------------------------------------------------------------------------

    def __init__(self, model_handler: BaseModelHandler, model_path: str | None = None):
        """
        ModelServer constructor.

        Returns:
            FastAPI instance.
        """
        self._app = self._create_model_server(
            model_handler = model_handler,
            model_path    = model_path
        )
    
    def get_asgi_instance(self):
        """
        Returns the ModelServer's instance of an ASGI compatible server.

        Returns:
            ASGI instance.
        """

        # Even though this is pretty abstract, it's hardcoded to use FastAPI
        # internally for now
        return self._app
