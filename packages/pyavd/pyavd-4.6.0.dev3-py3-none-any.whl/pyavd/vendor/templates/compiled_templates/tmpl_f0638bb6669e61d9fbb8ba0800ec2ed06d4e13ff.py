from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'eos/transceiver-qsfp-default-mode.j2'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_transceiver_qsfp_default_mode_4x10 = resolve('transceiver_qsfp_default_mode_4x10')
    l_0_generate_default_config = resolve('generate_default_config')
    try:
        t_1 = environment.filters['arista.avd.default']
    except KeyError:
        @internalcode
        def t_1(*unused):
            raise TemplateRuntimeError("No filter named 'arista.avd.default' found.")
    pass
    if t_1((undefined(name='transceiver_qsfp_default_mode_4x10') if l_0_transceiver_qsfp_default_mode_4x10 is missing else l_0_transceiver_qsfp_default_mode_4x10), (undefined(name='generate_default_config') if l_0_generate_default_config is missing else l_0_generate_default_config), True):
        pass
        yield '!\ntransceiver qsfp default-mode 4x10G\n'

blocks = {}
debug_info = '8=19'