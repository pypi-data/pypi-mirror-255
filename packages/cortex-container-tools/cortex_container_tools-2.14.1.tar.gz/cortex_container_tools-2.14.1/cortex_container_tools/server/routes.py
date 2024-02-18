from fastapi import APIRouter, HTTPException, Request

router = APIRouter()

@router.get('/health')
async def get_health(request: Request):
    """
    Health check endpoint. 

    Checks if the service is reachable.
    """
    return {'status': 'OK'}


@router.get('/readiness')
async def get_readiness(request: Request):
    """
    Readiness check endpoint.

    Checks if the server is ready to receive requests.
    """
    if request.app.model_instance:
        return {'status': 'Ready'}

    else:
        raise HTTPException(status_code=503, detail='Not ready')


@router.post('/infer')
async def infer(request: Request):
    """
    Readiness check endpoint.

    Checks if the service is ready to receive requests.
    """
    # Just in case you somehow try an inference at this before passing a ready
    # check...
    if not request.app.model_instance:
        raise HTTPException(status_code=503, detail='Not ready')

    model   = request.app.model_instance
    handler = request.app.model_handler

    input_data = handler.decode_input(await request.body())
    response   = handler.infer(model, input_data)
    return handler.encode_output(response)
