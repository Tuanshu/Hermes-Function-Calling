from utils_settings import get_env_variable, determine_environment

environment = determine_environment(dotenv_path="center_user/.env")

USER_DATABASE_URL = get_env_variable("USER_DATABASE_URL", environment)

PORT = get_env_variable("PORT", environment)
NUMBER_UVICORN_WORKER = get_env_variable("NUMBER_UVICORN_WORKER", environment)


PORT = get_env_variable("PORT", environment)
PORT_STANDALONE= get_env_variable("PORT_STANDALONE", environment)