from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'eos/ip-security.j2'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_ip_security = resolve('ip_security')
    try:
        t_1 = environment.filters['arista.avd.default']
    except KeyError:
        @internalcode
        def t_1(*unused):
            raise TemplateRuntimeError("No filter named 'arista.avd.default' found.")
    try:
        t_2 = environment.filters['arista.avd.hide_passwords']
    except KeyError:
        @internalcode
        def t_2(*unused):
            raise TemplateRuntimeError("No filter named 'arista.avd.hide_passwords' found.")
    try:
        t_3 = environment.tests['arista.avd.defined']
    except KeyError:
        @internalcode
        def t_3(*unused):
            raise TemplateRuntimeError("No test named 'arista.avd.defined' found.")
    pass
    if t_3((undefined(name='ip_security') if l_0_ip_security is missing else l_0_ip_security)):
        pass
        yield '!\nip security\n'
        for l_1_ike_policy in t_1(environment.getattr((undefined(name='ip_security') if l_0_ip_security is missing else l_0_ip_security), 'ike_policies'), []):
            _loop_vars = {}
            pass
            yield '   !\n   ike policy '
            yield str(environment.getattr(l_1_ike_policy, 'name'))
            yield '\n'
            if t_3(environment.getattr(l_1_ike_policy, 'local_id')):
                pass
                yield '      local-id '
                yield str(environment.getattr(l_1_ike_policy, 'local_id'))
                yield '\n'
            if t_3(environment.getattr(l_1_ike_policy, 'ike_lifetime')):
                pass
                yield '      ike-lifetime '
                yield str(environment.getattr(l_1_ike_policy, 'ike_lifetime'))
                yield '\n'
            if t_3(environment.getattr(l_1_ike_policy, 'encryption')):
                pass
                yield '      encryption '
                yield str(environment.getattr(l_1_ike_policy, 'encryption'))
                yield '\n'
            if t_3(environment.getattr(l_1_ike_policy, 'dh_group')):
                pass
                yield '      dh-group '
                yield str(environment.getattr(l_1_ike_policy, 'dh_group'))
                yield '\n'
        l_1_ike_policy = missing
        for l_1_sa_policy in t_1(environment.getattr((undefined(name='ip_security') if l_0_ip_security is missing else l_0_ip_security), 'sa_policies'), []):
            _loop_vars = {}
            pass
            yield '   !\n   sa policy '
            yield str(environment.getattr(l_1_sa_policy, 'name'))
            yield '\n'
            if t_3(environment.getattr(environment.getattr(l_1_sa_policy, 'esp'), 'integrity')):
                pass
                if (environment.getattr(environment.getattr(l_1_sa_policy, 'esp'), 'integrity') == 'disabled'):
                    pass
                    yield '      esp integrity null\n'
                else:
                    pass
                    yield '      esp integrity '
                    yield str(environment.getattr(environment.getattr(l_1_sa_policy, 'esp'), 'integrity'))
                    yield '\n'
            if t_3(environment.getattr(environment.getattr(l_1_sa_policy, 'esp'), 'encryption')):
                pass
                if (environment.getattr(environment.getattr(l_1_sa_policy, 'esp'), 'encryption') == 'disabled'):
                    pass
                    yield '      esp encryption null\n'
                else:
                    pass
                    yield '      esp encryption '
                    yield str(environment.getattr(environment.getattr(l_1_sa_policy, 'esp'), 'encryption'))
                    yield '\n'
            if t_3(environment.getattr(l_1_sa_policy, 'pfs_dh_group')):
                pass
                yield '      pfs dh-group '
                yield str(environment.getattr(l_1_sa_policy, 'pfs_dh_group'))
                yield '\n'
        l_1_sa_policy = missing
        for l_1_profile in t_1(environment.getattr((undefined(name='ip_security') if l_0_ip_security is missing else l_0_ip_security), 'profiles'), []):
            l_1_hide_passwords = resolve('hide_passwords')
            _loop_vars = {}
            pass
            yield '   !\n   profile '
            yield str(environment.getattr(l_1_profile, 'name'))
            yield '\n'
            if t_3(environment.getattr(l_1_profile, 'ike_policy')):
                pass
                yield '      ike-policy '
                yield str(environment.getattr(l_1_profile, 'ike_policy'))
                yield '\n'
            if t_3(environment.getattr(l_1_profile, 'sa_policy')):
                pass
                yield '      sa-policy '
                yield str(environment.getattr(l_1_profile, 'sa_policy'))
                yield '\n'
            if t_3(environment.getattr(l_1_profile, 'connection')):
                pass
                yield '      connection '
                yield str(environment.getattr(l_1_profile, 'connection'))
                yield '\n'
            if t_3(environment.getattr(l_1_profile, 'shared_key')):
                pass
                yield '      shared-key 7 '
                yield str(t_2(environment.getattr(l_1_profile, 'shared_key'), (undefined(name='hide_passwords') if l_1_hide_passwords is missing else l_1_hide_passwords)))
                yield '\n'
            if ((t_3(environment.getattr(environment.getattr(l_1_profile, 'dpd'), 'interval')) and t_3(environment.getattr(environment.getattr(l_1_profile, 'dpd'), 'time'))) and t_3(environment.getattr(environment.getattr(l_1_profile, 'dpd'), 'action'))):
                pass
                yield '      dpd '
                yield str(environment.getattr(environment.getattr(l_1_profile, 'dpd'), 'interval'))
                yield ' '
                yield str(environment.getattr(environment.getattr(l_1_profile, 'dpd'), 'time'))
                yield ' '
                yield str(environment.getattr(environment.getattr(l_1_profile, 'dpd'), 'action'))
                yield '\n'
            if t_3(environment.getattr(l_1_profile, 'mode')):
                pass
                yield '      mode '
                yield str(environment.getattr(l_1_profile, 'mode'))
                yield '\n'
        l_1_profile = l_1_hide_passwords = missing
        if t_3(environment.getattr((undefined(name='ip_security') if l_0_ip_security is missing else l_0_ip_security), 'key_controller')):
            pass
            yield '   !\n   key controller\n'
            if t_3(environment.getattr(environment.getattr((undefined(name='ip_security') if l_0_ip_security is missing else l_0_ip_security), 'key_controller'), 'profile')):
                pass
                yield '      profile '
                yield str(environment.getattr(environment.getattr((undefined(name='ip_security') if l_0_ip_security is missing else l_0_ip_security), 'key_controller'), 'profile'))
                yield '\n'
        if t_3(environment.getattr((undefined(name='ip_security') if l_0_ip_security is missing else l_0_ip_security), 'hardware_encryption_disabled'), True):
            pass
            yield '   hardware encryption disabled\n'

blocks = {}
debug_info = '7=30&10=33&12=37&13=39&14=42&16=44&17=47&19=49&20=52&22=54&23=57&26=60&28=64&29=66&30=68&33=74&36=76&37=78&40=84&43=86&44=89&47=92&49=97&50=99&51=102&53=104&54=107&56=109&57=112&59=114&60=117&62=119&63=122&65=128&66=131&69=134&72=137&73=140&76=142'