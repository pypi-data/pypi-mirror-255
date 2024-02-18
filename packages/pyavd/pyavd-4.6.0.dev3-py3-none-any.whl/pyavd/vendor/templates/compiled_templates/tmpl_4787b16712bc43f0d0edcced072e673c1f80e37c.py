from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'eos/custom-templates.j2'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_custom_templates = resolve('custom_templates')
    try:
        t_1 = environment.tests['arista.avd.defined']
    except KeyError:
        @internalcode
        def t_1(*unused):
            raise TemplateRuntimeError("No test named 'arista.avd.defined' found.")
    pass
    if t_1((undefined(name='custom_templates') if l_0_custom_templates is missing else l_0_custom_templates)):
        pass
        yield '!\n'
        for l_1_custom_template in (undefined(name='custom_templates') if l_0_custom_templates is missing else l_0_custom_templates):
            _loop_vars = {}
            pass
            template = environment.get_or_select_template(l_1_custom_template, 'eos/custom-templates.j2')
            for event in template.root_render_func(template.new_context(context.get_all(), True, {'custom_template': l_1_custom_template})):
                yield event
            yield '\n'
        l_1_custom_template = missing

blocks = {}
debug_info = '7=18&9=21&10=24'