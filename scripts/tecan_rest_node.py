"""Example REST-based client for a WEI module"""
import json
from argparse import ArgumentParser
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse

from wei.core.data_classes import ModuleStatus, StepResponse, StepStatus

from tecan_driver.autorun_tecan import Tecan

global state, module_resources

@asynccontextmanager
async def lifespan(app: FastAPI):
    global tecan, state, module_resources
    """Initial run function for the Tecan app, initializes the state
        Parameters
        ----------
        app : FastApi
           The REST API app being initialized

        Returns
        -------
        None"""
    try:
        # Do any instrument configuration here
        tecan = Tecan()
        state = ModuleStatus.IDLE
        module_resources = []
    except Exception as err:
        print(err)
        state = ModuleStatus.ERROR

    # Yield control to the application
    yield

    # Do any cleanup here
    pass


app = FastAPI(
    lifespan=lifespan,
)


@app.get("/state")
def get_state():
    """Returns the current state of the module"""
    global state
    return JSONResponse(content={"State": state})


@app.get("/about")
async def about():
    """Returns a description of the actions and resources the module supports"""
    global state
    return JSONResponse(content={"name": "peeler",
            "model": "Tecan",
            "version": "0.0.1",
            "actions": {
             "open_gate": "config : %s",  
             "close_gate": "config : %s",  
             "run_tecan": "config : %s",  

             },
            "repo": "https://github.com/AD-SDL/tecan_module.git"
            })

@app.get("/resources")
async def resources():
    """Returns the current resources available to the module"""
    global state, module_resources
    resource_info = ""
    if not (module_resources == ""):
        with open(module_resources) as f:
            resource_info = f.read()
    return JSONResponse(content={"Resources": resource_info})


@app.post("/action")
def do_action(
    action_handle: str,  # The action to be performed
    action_vars: str,  # Any arguments necessary to run that action
) -> StepResponse:
    global state
    if state == ModuleStatus.BUSY:
        return StepResponse(
            action_response=StepStatus.FAILED,
            action_msg="",
            action_log="Tecan is busy",
        )
    state = ModuleStatus.BUSY

    try:
        if action_handle == "open_gate":
            if "protocol_file_path" in action_vars.keys():
                file_path = action_vars.get("protocol_file_path")
                result = tecan.open_tecan(protocol_file_path = file_path)
            else:
                result = tecan.open_tecan() 

            state = ModuleStatus.IDLE
            return StepResponse(
                action_response=StepStatus.SUCCEEDED,
                action_msg=result,
                action_log="",
            )
        elif action_handle == "close_gate":

            if "tecan_file_path" in action_vars.keys():
                kwargs = {
                    'tecan_file_path': action_vars.get("tecan_file_path"),
                }
                result = tecan.close_tecan(**kwargs)
            else: 
                result = tecan.close_tecan()

            state = ModuleStatus.IDLE
            return StepResponse(
                action_response=StepStatus.SUCCEEDED,
                action_msg=result,
                action_log="",
            )
        elif action_handle == "do_action_return_file":
            state = ModuleStatus.IDLE
            # Use the FileResponse class to return files
            file_name = json.loads(action_vars)["file_name"]
            return FileResponse(
                path=file_name,
                content={
                    "action_response": StepStatus.SUCCEEDED,
                    "action_msg": file_name,
                    "action_log": "",
                },
            )
        else:
            # Handle Unsupported actions
            state = ModuleStatus.IDLE
            return StepResponse(
                action_response=StepStatus.FAILED,
                action_msg="",
                action_log="Unsupported action",
            )
    except Exception as e:
        print(str(e))
        state = ModuleStatus.IDLE
        return StepResponse(
            action_response=StepStatus.FAILED,
            action_msg="",
            action_log=str(e),
        )


if __name__ == "__main__":
    import uvicorn

    parser = ArgumentParser()
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host IP")
    parser.add_argument("--port", type=str, default="2000", help="Host IP")
    # Add any additional arguments here
    args = parser.parse_args()

    uvicorn.run(
        "tecan_rest_node:app",
        host=args.host,
        port=int(args.port),
        reload=True,
    )