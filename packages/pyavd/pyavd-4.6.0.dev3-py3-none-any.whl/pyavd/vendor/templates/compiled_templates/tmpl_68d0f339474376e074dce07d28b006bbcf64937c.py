from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'eos/interface-ip-nat.j2'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_interface_ip_nat = resolve('interface_ip_nat')
    try:
        t_1 = environment.filters['arista.avd.default']
    except KeyError:
        @internalcode
        def t_1(*unused):
            raise TemplateRuntimeError("No filter named 'arista.avd.default' found.")
    try:
        t_2 = environment.filters['arista.avd.natural_sort']
    except KeyError:
        @internalcode
        def t_2(*unused):
            raise TemplateRuntimeError("No filter named 'arista.avd.natural_sort' found.")
    try:
        t_3 = environment.tests['arista.avd.defined']
    except KeyError:
        @internalcode
        def t_3(*unused):
            raise TemplateRuntimeError("No test named 'arista.avd.defined' found.")
    pass
    for l_1_nat in t_2(t_1(environment.getattr(environment.getattr((undefined(name='interface_ip_nat') if l_0_interface_ip_nat is missing else l_0_interface_ip_nat), 'source'), 'static'), []), 'original_ip'):
        l_1_nat_cli = resolve('nat_cli')
        _loop_vars = {}
        pass
        if ((not (t_3(environment.getattr(l_1_nat, 'access_list')) and t_3(environment.getattr(l_1_nat, 'group')))) and (not ((not t_3(environment.getattr(l_1_nat, 'original_port'))) and t_3(environment.getattr(l_1_nat, 'translated_port'))))):
            pass
            l_1_nat_cli = 'ip nat source'
            _loop_vars['nat_cli'] = l_1_nat_cli
            if t_3(environment.getattr(l_1_nat, 'direction')):
                pass
                l_1_nat_cli = str_join(((undefined(name='nat_cli') if l_1_nat_cli is missing else l_1_nat_cli), ' ', environment.getattr(l_1_nat, 'direction'), ))
                _loop_vars['nat_cli'] = l_1_nat_cli
            l_1_nat_cli = str_join(((undefined(name='nat_cli') if l_1_nat_cli is missing else l_1_nat_cli), ' static ', environment.getattr(l_1_nat, 'original_ip'), ))
            _loop_vars['nat_cli'] = l_1_nat_cli
            if t_3(environment.getattr(l_1_nat, 'original_port')):
                pass
                l_1_nat_cli = str_join(((undefined(name='nat_cli') if l_1_nat_cli is missing else l_1_nat_cli), ' ', environment.getattr(l_1_nat, 'original_port'), ))
                _loop_vars['nat_cli'] = l_1_nat_cli
            if t_3(environment.getattr(l_1_nat, 'access_list')):
                pass
                l_1_nat_cli = str_join(((undefined(name='nat_cli') if l_1_nat_cli is missing else l_1_nat_cli), ' access-list ', environment.getattr(l_1_nat, 'access_list'), ))
                _loop_vars['nat_cli'] = l_1_nat_cli
            l_1_nat_cli = str_join(((undefined(name='nat_cli') if l_1_nat_cli is missing else l_1_nat_cli), ' ', environment.getattr(l_1_nat, 'translated_ip'), ))
            _loop_vars['nat_cli'] = l_1_nat_cli
            if t_3(environment.getattr(l_1_nat, 'translated_port')):
                pass
                l_1_nat_cli = str_join(((undefined(name='nat_cli') if l_1_nat_cli is missing else l_1_nat_cli), ' ', environment.getattr(l_1_nat, 'translated_port'), ))
                _loop_vars['nat_cli'] = l_1_nat_cli
            if t_3(environment.getattr(l_1_nat, 'protocol')):
                pass
                l_1_nat_cli = str_join(((undefined(name='nat_cli') if l_1_nat_cli is missing else l_1_nat_cli), ' protocol ', environment.getattr(l_1_nat, 'protocol'), ))
                _loop_vars['nat_cli'] = l_1_nat_cli
            if t_3(environment.getattr(l_1_nat, 'group')):
                pass
                l_1_nat_cli = str_join(((undefined(name='nat_cli') if l_1_nat_cli is missing else l_1_nat_cli), ' group ', environment.getattr(l_1_nat, 'group'), ))
                _loop_vars['nat_cli'] = l_1_nat_cli
            if t_3(environment.getattr(l_1_nat, 'comment')):
                pass
                l_1_nat_cli = str_join(((undefined(name='nat_cli') if l_1_nat_cli is missing else l_1_nat_cli), ' comment ', environment.getattr(l_1_nat, 'comment'), ))
                _loop_vars['nat_cli'] = l_1_nat_cli
            yield '   '
            yield str((undefined(name='nat_cli') if l_1_nat_cli is missing else l_1_nat_cli))
            yield '\n'
    l_1_nat = l_1_nat_cli = missing
    for l_1_nat in t_2(t_1(environment.getattr(environment.getattr((undefined(name='interface_ip_nat') if l_0_interface_ip_nat is missing else l_0_interface_ip_nat), 'source'), 'dynamic'), []), 'access_list'):
        l_1_valid = l_1_nat_cli = missing
        _loop_vars = {}
        pass
        l_1_valid = False
        _loop_vars['valid'] = l_1_valid
        l_1_nat_cli = str_join(('ip nat source dynamic access-list ', environment.getattr(l_1_nat, 'access_list'), ))
        _loop_vars['nat_cli'] = l_1_nat_cli
        if (environment.getattr(l_1_nat, 'nat_type') == 'overload'):
            pass
            l_1_nat_cli = str_join(((undefined(name='nat_cli') if l_1_nat_cli is missing else l_1_nat_cli), ' overload', ))
            _loop_vars['nat_cli'] = l_1_nat_cli
            l_1_valid = True
            _loop_vars['valid'] = l_1_valid
        elif t_3(environment.getattr(l_1_nat, 'pool_name')):
            pass
            l_1_nat_cli = str_join(((undefined(name='nat_cli') if l_1_nat_cli is missing else l_1_nat_cli), ' pool ', environment.getattr(l_1_nat, 'pool_name'), ))
            _loop_vars['nat_cli'] = l_1_nat_cli
            l_1_valid = True
            _loop_vars['valid'] = l_1_valid
            if (environment.getattr(l_1_nat, 'nat_type') == 'pool-address-only'):
                pass
                l_1_nat_cli = str_join(((undefined(name='nat_cli') if l_1_nat_cli is missing else l_1_nat_cli), ' address-only', ))
                _loop_vars['nat_cli'] = l_1_nat_cli
            elif (environment.getattr(l_1_nat, 'nat_type') == 'pool-full-cone'):
                pass
                l_1_nat_cli = str_join(((undefined(name='nat_cli') if l_1_nat_cli is missing else l_1_nat_cli), ' full-cone', ))
                _loop_vars['nat_cli'] = l_1_nat_cli
        if (undefined(name='valid') if l_1_valid is missing else l_1_valid):
            pass
            if (t_1(environment.getattr(l_1_nat, 'priority'), 0) > 0):
                pass
                l_1_nat_cli = str_join(((undefined(name='nat_cli') if l_1_nat_cli is missing else l_1_nat_cli), ' priority ', environment.getattr(l_1_nat, 'priority'), ))
                _loop_vars['nat_cli'] = l_1_nat_cli
            if t_3(environment.getattr(l_1_nat, 'comment')):
                pass
                l_1_nat_cli = str_join(((undefined(name='nat_cli') if l_1_nat_cli is missing else l_1_nat_cli), ' comment ', environment.getattr(l_1_nat, 'comment'), ))
                _loop_vars['nat_cli'] = l_1_nat_cli
            yield '   '
            yield str((undefined(name='nat_cli') if l_1_nat_cli is missing else l_1_nat_cli))
            yield '\n'
    l_1_nat = l_1_valid = l_1_nat_cli = missing
    for l_1_nat in t_2(t_1(environment.getattr(environment.getattr((undefined(name='interface_ip_nat') if l_0_interface_ip_nat is missing else l_0_interface_ip_nat), 'destination'), 'static'), []), 'original_ip'):
        l_1_nat_cli = resolve('nat_cli')
        _loop_vars = {}
        pass
        if ((not (t_3(environment.getattr(l_1_nat, 'access_list')) and t_3(environment.getattr(l_1_nat, 'group')))) and (not ((not t_3(environment.getattr(l_1_nat, 'original_port'))) and t_3(environment.getattr(l_1_nat, 'translated_port'))))):
            pass
            l_1_nat_cli = 'ip nat destination'
            _loop_vars['nat_cli'] = l_1_nat_cli
            if t_3(environment.getattr(l_1_nat, 'direction')):
                pass
                l_1_nat_cli = str_join(((undefined(name='nat_cli') if l_1_nat_cli is missing else l_1_nat_cli), ' ', environment.getattr(l_1_nat, 'direction'), ))
                _loop_vars['nat_cli'] = l_1_nat_cli
            l_1_nat_cli = str_join(((undefined(name='nat_cli') if l_1_nat_cli is missing else l_1_nat_cli), ' static ', environment.getattr(l_1_nat, 'original_ip'), ))
            _loop_vars['nat_cli'] = l_1_nat_cli
            if t_3(environment.getattr(l_1_nat, 'original_port')):
                pass
                l_1_nat_cli = str_join(((undefined(name='nat_cli') if l_1_nat_cli is missing else l_1_nat_cli), ' ', environment.getattr(l_1_nat, 'original_port'), ))
                _loop_vars['nat_cli'] = l_1_nat_cli
            if t_3(environment.getattr(l_1_nat, 'access_list')):
                pass
                l_1_nat_cli = str_join(((undefined(name='nat_cli') if l_1_nat_cli is missing else l_1_nat_cli), ' access-list ', environment.getattr(l_1_nat, 'access_list'), ))
                _loop_vars['nat_cli'] = l_1_nat_cli
            l_1_nat_cli = str_join(((undefined(name='nat_cli') if l_1_nat_cli is missing else l_1_nat_cli), ' ', environment.getattr(l_1_nat, 'translated_ip'), ))
            _loop_vars['nat_cli'] = l_1_nat_cli
            if t_3(environment.getattr(l_1_nat, 'translated_port')):
                pass
                l_1_nat_cli = str_join(((undefined(name='nat_cli') if l_1_nat_cli is missing else l_1_nat_cli), ' ', environment.getattr(l_1_nat, 'translated_port'), ))
                _loop_vars['nat_cli'] = l_1_nat_cli
            if t_3(environment.getattr(l_1_nat, 'protocol')):
                pass
                l_1_nat_cli = str_join(((undefined(name='nat_cli') if l_1_nat_cli is missing else l_1_nat_cli), ' protocol ', environment.getattr(l_1_nat, 'protocol'), ))
                _loop_vars['nat_cli'] = l_1_nat_cli
            if t_3(environment.getattr(l_1_nat, 'group')):
                pass
                l_1_nat_cli = str_join(((undefined(name='nat_cli') if l_1_nat_cli is missing else l_1_nat_cli), ' group ', environment.getattr(l_1_nat, 'group'), ))
                _loop_vars['nat_cli'] = l_1_nat_cli
            if t_3(environment.getattr(l_1_nat, 'comment')):
                pass
                l_1_nat_cli = str_join(((undefined(name='nat_cli') if l_1_nat_cli is missing else l_1_nat_cli), ' comment ', environment.getattr(l_1_nat, 'comment'), ))
                _loop_vars['nat_cli'] = l_1_nat_cli
            yield '   '
            yield str((undefined(name='nat_cli') if l_1_nat_cli is missing else l_1_nat_cli))
            yield '\n'
    l_1_nat = l_1_nat_cli = missing
    for l_1_nat in t_2(t_1(environment.getattr(environment.getattr((undefined(name='interface_ip_nat') if l_0_interface_ip_nat is missing else l_0_interface_ip_nat), 'destination'), 'dynamic'), []), 'access_list'):
        l_1_nat_cli = missing
        _loop_vars = {}
        pass
        l_1_nat_cli = str_join(('ip nat destination dynamic access-list ', environment.getattr(l_1_nat, 'access_list'), ' pool ', environment.getattr(l_1_nat, 'pool_name'), ))
        _loop_vars['nat_cli'] = l_1_nat_cli
        if (t_1(environment.getattr(l_1_nat, 'priority'), 0) > 0):
            pass
            l_1_nat_cli = str_join(((undefined(name='nat_cli') if l_1_nat_cli is missing else l_1_nat_cli), ' priority ', environment.getattr(l_1_nat, 'priority'), ))
            _loop_vars['nat_cli'] = l_1_nat_cli
        if t_3(environment.getattr(l_1_nat, 'comment')):
            pass
            l_1_nat_cli = str_join(((undefined(name='nat_cli') if l_1_nat_cli is missing else l_1_nat_cli), ' comment ', environment.getattr(l_1_nat, 'comment'), ))
            _loop_vars['nat_cli'] = l_1_nat_cli
        yield '   '
        yield str((undefined(name='nat_cli') if l_1_nat_cli is missing else l_1_nat_cli))
        yield '\n'
    l_1_nat = l_1_nat_cli = missing

blocks = {}
debug_info = '8=30&9=34&11=36&12=38&13=40&15=42&16=44&17=46&19=48&20=50&22=52&23=54&24=56&26=58&27=60&29=62&30=64&32=66&33=68&35=71&39=74&40=78&41=80&42=82&43=84&44=86&45=88&46=90&47=92&48=94&49=96&50=98&51=100&54=102&55=104&56=106&58=108&59=110&61=113&65=116&66=120&68=122&69=124&70=126&72=128&73=130&74=132&76=134&77=136&79=138&80=140&81=142&83=144&84=146&86=148&87=150&89=152&90=154&92=157&96=160&97=164&98=166&99=168&101=170&102=172&104=175'