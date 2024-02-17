from whatap.trace.mod.application_wsgi import interceptor, trace_handler, \
    interceptor_error


def instrument(module):
    def wrapper(fn):
        @trace_handler(fn, True)
        def trace(*args, **kwargs):
            environ = args[0]
            callback = interceptor((fn, environ), *args, **kwargs)
            return callback
        
        return trace
    if hasattr(module, "application"):
        
        module.application = wrapper(module.application)
    