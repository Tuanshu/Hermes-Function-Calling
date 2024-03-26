# infrastructure, db
import os


def is_running_in_docker() -> bool:
    """Check if the application is running in a Docker container."""
    try:
        with open("/proc/1/cgroup", "rt") as ifh:
            return "docker" in ifh.read()
    except Exception:
        return False


def is_running_in_k8s() -> bool:
    """Check if the application is running in a Kubernetes pod."""
    return "KUBERNETES_SERVICE_HOST" in os.environ


def determine_environment(
    dotenv_path=None, shared_dotenv_path="shared_component/.env.common"
):
    """
    Determine the running environment.

    :return: A string representing the environment ('local', 'docker', or 'k8s').
    """
    if is_running_in_k8s():
        print("Running in Kubernetes")
        return "k8s"
    elif is_running_in_docker():
        print("Running in Docker")
        return "docker"
    else:
        print("Running directly, not in Docker or Kubernetes")
        from dotenv import load_dotenv

        print("Laoding .env.common via dotenv.")
        load_dotenv(dotenv_path=shared_dotenv_path)

        print("Laoding project specified .env via dotenv.")
        load_dotenv(dotenv_path=dotenv_path)

        return "local"


def get_env_variable(var_name, environment="local", default=None):
    """
    Get the environment variable based on the specified environment.
    If running in a local environment, it first tries to fetch 'var_name_LOCAL'.
    If not found, it falls back to 'var_name'. In Docker or Kubernetes, it directly fetches 'var_name'.

    :param environment: The environment state ('local', 'docker', or 'k8s').
    :param var_name: The base name of the environment variable.
    :param default: Default value if the environment variable is not set.
    :return: The value of the environment variable.
    """
    if environment == "local":
        local_var_name = f"{var_name}_LOCAL"
        value = os.environ.get(local_var_name)
        if value is not None:
            return value

    return os.environ.get(var_name, default)
