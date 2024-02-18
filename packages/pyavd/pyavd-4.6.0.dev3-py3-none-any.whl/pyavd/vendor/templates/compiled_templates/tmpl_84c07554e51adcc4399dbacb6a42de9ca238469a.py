from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'eos/virtual-source-nat-vrfs.j2'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_virtual_source_nat_vrfs = resolve('virtual_source_nat_vrfs')
    try:
        t_1 = environment.filters['arista.avd.natural_sort']
    except KeyError:
        @internalcode
        def t_1(*unused):
            raise TemplateRuntimeError("No filter named 'arista.avd.natural_sort' found.")
    try:
        t_2 = environment.tests['arista.avd.defined']
    except KeyError:
        @internalcode
        def t_2(*unused):
            raise TemplateRuntimeError("No test named 'arista.avd.defined' found.")
    pass
    if t_2((undefined(name='virtual_source_nat_vrfs') if l_0_virtual_source_nat_vrfs is missing else l_0_virtual_source_nat_vrfs)):
        pass
        yield '!\n'
        for l_1_vrf in t_1((undefined(name='virtual_source_nat_vrfs') if l_0_virtual_source_nat_vrfs is missing else l_0_virtual_source_nat_vrfs), 'name'):
            _loop_vars = {}
            pass
            if t_2(environment.getattr(l_1_vrf, 'ip_address')):
                pass
                yield 'ip address virtual source-nat vrf '
                yield str(environment.getattr(l_1_vrf, 'name'))
                yield ' address '
                yield str(environment.getattr(l_1_vrf, 'ip_address'))
                yield '\n'
        l_1_vrf = missing

blocks = {}
debug_info = '7=24&9=27&10=30&11=33'