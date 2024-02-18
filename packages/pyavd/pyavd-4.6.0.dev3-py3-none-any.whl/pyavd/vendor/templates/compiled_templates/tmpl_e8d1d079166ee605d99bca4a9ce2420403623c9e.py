from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'documentation/event-handlers.j2'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_event_handlers = resolve('event_handlers')
    try:
        t_1 = environment.filters['arista.avd.natural_sort']
    except KeyError:
        @internalcode
        def t_1(*unused):
            raise TemplateRuntimeError("No filter named 'arista.avd.natural_sort' found.")
    try:
        t_2 = environment.filters['replace']
    except KeyError:
        @internalcode
        def t_2(*unused):
            raise TemplateRuntimeError("No filter named 'replace' found.")
    try:
        t_3 = environment.tests['arista.avd.defined']
    except KeyError:
        @internalcode
        def t_3(*unused):
            raise TemplateRuntimeError("No test named 'arista.avd.defined' found.")
    pass
    if t_3((undefined(name='event_handlers') if l_0_event_handlers is missing else l_0_event_handlers)):
        pass
        yield '\n### Event Handler\n\n#### Event Handler Summary\n\n| Handler | Action Type | Action | Trigger |\n| ------- | ----------- | ------ | ------- |\n'
        for l_1_handler in t_1((undefined(name='event_handlers') if l_0_event_handlers is missing else l_0_event_handlers), 'name'):
            l_1_action = missing
            _loop_vars = {}
            pass
            l_1_action = t_2(context.eval_ctx, environment.getattr(l_1_handler, 'action'), '|', '\\|')
            _loop_vars['action'] = l_1_action
            if (environment.getattr(l_1_handler, 'action_type') == 'bash'):
                pass
                l_1_action = str_join(('<code>', (undefined(name='action') if l_1_action is missing else l_1_action), '</code>', ))
                _loop_vars['action'] = l_1_action
            yield '| '
            yield str(environment.getattr(l_1_handler, 'name'))
            yield ' | '
            yield str(environment.getattr(l_1_handler, 'action_type'))
            yield ' | '
            yield str((undefined(name='action') if l_1_action is missing else l_1_action))
            yield ' | '
            yield str(environment.getattr(l_1_handler, 'trigger'))
            yield ' |\n'
        l_1_handler = l_1_action = missing
        yield '\n#### Event Handler Device Configuration\n\n```eos\n'
        template = environment.get_template('eos/event-handlers.j2', 'documentation/event-handlers.j2')
        for event in template.root_render_func(template.new_context(context.get_all(), True, {})):
            yield event
        yield '```\n'

blocks = {}
debug_info = '7=30&15=33&16=37&17=39&18=41&20=44&26=54'