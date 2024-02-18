import contextvars

LLMInstance = contextvars.ContextVar("LLMInstance", default=None)


def set_llm_instance(llm_instance):
    LLMInstance.set(llm_instance)


def get_llm_instance():
    return LLMInstance.get()
