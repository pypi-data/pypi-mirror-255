import click
import functools as ft


from .postman import PostmanClient, Postman
from .staircase import Staircase
from .env_storage import EnvironmentStorage
from .env_manager import EnvironmentManager
from .config import get_user_cfg 



def user_config_provider():
    def decorator(f):
        @click.pass_context
        def wrapper(ctx, *args, **kwargs):
            user_config = get_user_cfg()
            return ctx.invoke(f, *args, **kwargs, user_config=user_config)

        return ft.update_wrapper(wrapper, f)

    return decorator


def staircase_provider():
    def decorator(f):
        @click.pass_context
        def wrapper(ctx, *args, **kwargs):
            user_config = get_user_cfg()
            staircase = Staircase(user_config)
            return ctx.invoke(f, *args, **kwargs, staircase=staircase)
        return ft.update_wrapper(wrapper, f)
    return decorator


def env_storage_provider():
    def decorator(f):
        @click.pass_context
        def wrapper(ctx, *args, **kwargs):
            env_storage = EnvironmentStorage()
            return ctx.invoke(f, *args, **kwargs, env_storage=env_storage)
        return ft.update_wrapper(wrapper, f)
    return decorator

def env_manager_provider():
    def decorator(f):
        @click.pass_context
        def wrapper(ctx, *args, **kwargs):
            obj = EnvironmentManager()
            return ctx.invoke(f, *args, **kwargs, env_manager=obj)
        return ft.update_wrapper(wrapper, f)
    return decorator


def postman_provider():
    def decorator(f):
        @click.pass_context
        def wrapper(ctx, *args, **kwargs):
            user_config = get_user_cfg()
            postman_client = PostmanClient(api_key=user_config.postman_api_key)
            postman = Postman(postman_client)
            return ctx.invoke(
                f, *args, **kwargs, postman_client=postman_client, postman=postman
            )

        return ft.update_wrapper(wrapper, f)

    return decorator
