from ewoksserver.app import routes

ROOT_ALL_VERSIONS = (
    f"{routes.BACKEND_PREFIX}",
    f"{routes.BACKEND_PREFIX}/v1",
    f"{routes.BACKEND_PREFIX}/v1_1_0",
    f"{routes.BACKEND_PREFIX}/v1_0_0",
)

ROOT_V1_1_0 = (
    f"{routes.BACKEND_PREFIX}",
    f"{routes.BACKEND_PREFIX}/v1",
    f"{routes.BACKEND_PREFIX}/v1_1_0",
)
