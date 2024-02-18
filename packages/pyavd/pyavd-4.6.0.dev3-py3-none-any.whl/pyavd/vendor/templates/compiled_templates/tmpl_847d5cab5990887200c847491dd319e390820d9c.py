from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'documentation/management-security.j2'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_management_security = resolve('management_security')
    l_0_ssl_profiles_certs = resolve('ssl_profiles_certs')
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
        t_3 = environment.filters['join']
    except KeyError:
        @internalcode
        def t_3(*unused):
            raise TemplateRuntimeError("No filter named 'join' found.")
    try:
        t_4 = environment.filters['length']
    except KeyError:
        @internalcode
        def t_4(*unused):
            raise TemplateRuntimeError("No filter named 'length' found.")
    try:
        t_5 = environment.tests['arista.avd.defined']
    except KeyError:
        @internalcode
        def t_5(*unused):
            raise TemplateRuntimeError("No test named 'arista.avd.defined' found.")
    pass
    if t_5((undefined(name='management_security') if l_0_management_security is missing else l_0_management_security)):
        pass
        yield '\n## Management Security\n\n### Management Security Summary\n\n| Settings | Value |\n| -------- | ----- |\n'
        if t_5(environment.getattr((undefined(name='management_security') if l_0_management_security is missing else l_0_management_security), 'entropy_source')):
            pass
            yield '| Entropy source | '
            yield str(environment.getattr((undefined(name='management_security') if l_0_management_security is missing else l_0_management_security), 'entropy_source'))
            yield ' |\n'
        if t_5(environment.getattr(environment.getattr((undefined(name='management_security') if l_0_management_security is missing else l_0_management_security), 'password'), 'encryption_key_common')):
            pass
            yield '| Common password encryption key | '
            yield str(environment.getattr(environment.getattr((undefined(name='management_security') if l_0_management_security is missing else l_0_management_security), 'password'), 'encryption_key_common'))
            yield ' |\n'
        if t_5(environment.getattr(environment.getattr((undefined(name='management_security') if l_0_management_security is missing else l_0_management_security), 'password'), 'encryption_reversible')):
            pass
            yield '| Reversible password encryption | '
            yield str(environment.getattr(environment.getattr((undefined(name='management_security') if l_0_management_security is missing else l_0_management_security), 'password'), 'encryption_reversible'))
            yield ' |\n'
        if t_5(environment.getattr(environment.getattr((undefined(name='management_security') if l_0_management_security is missing else l_0_management_security), 'password'), 'minimum_length')):
            pass
            yield '| Minimum password length | '
            yield str(environment.getattr(environment.getattr((undefined(name='management_security') if l_0_management_security is missing else l_0_management_security), 'password'), 'minimum_length'))
            yield ' |\n'
        if t_5(environment.getattr((undefined(name='management_security') if l_0_management_security is missing else l_0_management_security), 'ssl_profiles')):
            pass
            yield '\n### Management Security SSL Profiles\n\n| SSL Profile Name | TLS protocol accepted | Certificate filename | Key filename | Cipher List | CRLs |\n| ---------------- | --------------------- | -------------------- | ------------ | ----------- | ---- |\n'
            l_0_ssl_profiles_certs = []
            context.vars['ssl_profiles_certs'] = l_0_ssl_profiles_certs
            context.exported_vars.add('ssl_profiles_certs')
            for l_1_ssl_profile in t_2(environment.getattr((undefined(name='management_security') if l_0_management_security is missing else l_0_management_security), 'ssl_profiles')):
                l_1_crls = l_1_tmp_cert = missing
                _loop_vars = {}
                pass
                l_1_crls = '-'
                _loop_vars['crls'] = l_1_crls
                if t_5(environment.getattr(l_1_ssl_profile, 'certificate_revocation_lists')):
                    pass
                    l_1_crls = t_3(context.eval_ctx, t_2(environment.getattr(l_1_ssl_profile, 'certificate_revocation_lists')), '<br>')
                    _loop_vars['crls'] = l_1_crls
                yield '| '
                yield str(t_1(environment.getattr(l_1_ssl_profile, 'name'), '-'))
                yield ' | '
                yield str(t_1(environment.getattr(l_1_ssl_profile, 'tls_versions'), '-'))
                yield ' | '
                yield str(t_1(environment.getattr(environment.getattr(l_1_ssl_profile, 'certificate'), 'file'), '-'))
                yield ' | '
                yield str(t_1(environment.getattr(environment.getattr(l_1_ssl_profile, 'certificate'), 'key'), '-'))
                yield ' | '
                yield str(t_1(environment.getattr(l_1_ssl_profile, 'cipher_list'), '-'))
                yield ' | '
                yield str((undefined(name='crls') if l_1_crls is missing else l_1_crls))
                yield ' |\n'
                l_1_tmp_cert = {}
                _loop_vars['tmp_cert'] = l_1_tmp_cert
                if t_5(environment.getattr(l_1_ssl_profile, 'trust_certificate')):
                    pass
                    l_1_tmp_cert = {'trust_certificate': environment.getattr(l_1_ssl_profile, 'trust_certificate')}
                    _loop_vars['tmp_cert'] = l_1_tmp_cert
                if t_5(environment.getattr(l_1_ssl_profile, 'chain_certificate')):
                    pass
                    context.call(environment.getattr((undefined(name='tmp_cert') if l_1_tmp_cert is missing else l_1_tmp_cert), 'update'), {'chain_certificate': environment.getattr(l_1_ssl_profile, 'chain_certificate')}, _loop_vars=_loop_vars)
                if (t_4((undefined(name='tmp_cert') if l_1_tmp_cert is missing else l_1_tmp_cert)) > 0):
                    pass
                    context.call(environment.getattr((undefined(name='tmp_cert') if l_1_tmp_cert is missing else l_1_tmp_cert), 'update'), {'name': environment.getattr(l_1_ssl_profile, 'name')}, _loop_vars=_loop_vars)
                    context.call(environment.getattr((undefined(name='ssl_profiles_certs') if l_0_ssl_profiles_certs is missing else l_0_ssl_profiles_certs), 'append'), (undefined(name='tmp_cert') if l_1_tmp_cert is missing else l_1_tmp_cert), _loop_vars=_loop_vars)
            l_1_ssl_profile = l_1_crls = l_1_tmp_cert = missing
            for l_1_ssl_profile in t_2((undefined(name='ssl_profiles_certs') if l_0_ssl_profiles_certs is missing else l_0_ssl_profiles_certs), 'name'):
                l_1_trust_certs = resolve('trust_certs')
                l_1_requirement = resolve('requirement')
                l_1_tmp_requirement = resolve('tmp_requirement')
                l_1_policy = resolve('policy')
                l_1_system = resolve('system')
                l_1_chain_certs = resolve('chain_certs')
                _loop_vars = {}
                pass
                yield '\n### SSL profile '
                yield str(environment.getattr(l_1_ssl_profile, 'name'))
                yield ' Certificates Summary\n'
                if t_5(environment.getattr(l_1_ssl_profile, 'trust_certificate')):
                    pass
                    yield '\n| Trust Certificates | Requirement | Policy | System |\n| ------------------ | ----------- | ------ | ------ |\n'
                    l_1_trust_certs = t_3(context.eval_ctx, t_1(environment.getattr(environment.getattr(l_1_ssl_profile, 'trust_certificate'), 'certificates'), '-'), ', ')
                    _loop_vars['trust_certs'] = l_1_trust_certs
                    l_1_requirement = '-'
                    _loop_vars['requirement'] = l_1_requirement
                    if t_5(environment.getattr(environment.getattr(l_1_ssl_profile, 'trust_certificate'), 'requirement')):
                        pass
                        l_1_tmp_requirement = []
                        _loop_vars['tmp_requirement'] = l_1_tmp_requirement
                        if t_5(environment.getattr(environment.getattr(environment.getattr(l_1_ssl_profile, 'trust_certificate'), 'requirement'), 'basic_constraint_ca'), True):
                            pass
                            context.call(environment.getattr((undefined(name='tmp_requirement') if l_1_tmp_requirement is missing else l_1_tmp_requirement), 'append'), 'Basic Constraint CA', _loop_vars=_loop_vars)
                        if t_5(environment.getattr(environment.getattr(environment.getattr(l_1_ssl_profile, 'trust_certificate'), 'requirement'), 'hostname_fqdn'), True):
                            pass
                            context.call(environment.getattr((undefined(name='tmp_requirement') if l_1_tmp_requirement is missing else l_1_tmp_requirement), 'append'), 'Hostname must be FQDN', _loop_vars=_loop_vars)
                        if (t_4((undefined(name='tmp_requirement') if l_1_tmp_requirement is missing else l_1_tmp_requirement)) > 0):
                            pass
                            l_1_requirement = t_3(context.eval_ctx, (undefined(name='tmp_requirement') if l_1_tmp_requirement is missing else l_1_tmp_requirement), ', ')
                            _loop_vars['requirement'] = l_1_requirement
                    l_1_policy = '-'
                    _loop_vars['policy'] = l_1_policy
                    if t_5(environment.getattr(environment.getattr(l_1_ssl_profile, 'trust_certificate'), 'policy_expiry_date_ignore'), True):
                        pass
                        l_1_policy = 'Ignore Expiry Date'
                        _loop_vars['policy'] = l_1_policy
                    if t_5(environment.getattr(environment.getattr(l_1_ssl_profile, 'trust_certificate'), 'system'), True):
                        pass
                        l_1_system = 'Enabled'
                        _loop_vars['system'] = l_1_system
                    else:
                        pass
                        l_1_system = '-'
                        _loop_vars['system'] = l_1_system
                    yield '| '
                    yield str((undefined(name='trust_certs') if l_1_trust_certs is missing else l_1_trust_certs))
                    yield ' | '
                    yield str((undefined(name='requirement') if l_1_requirement is missing else l_1_requirement))
                    yield ' | '
                    yield str((undefined(name='policy') if l_1_policy is missing else l_1_policy))
                    yield ' | '
                    yield str((undefined(name='system') if l_1_system is missing else l_1_system))
                    yield ' |\n'
                if t_5(environment.getattr(l_1_ssl_profile, 'chain_certificate')):
                    pass
                    yield '\n| Chain Certificates | Requirement |\n| ------------------ | ----------- |\n'
                    l_1_chain_certs = t_3(context.eval_ctx, t_1(environment.getattr(environment.getattr(l_1_ssl_profile, 'chain_certificate'), 'certificates'), '-'), ', ')
                    _loop_vars['chain_certs'] = l_1_chain_certs
                    l_1_requirement = '-'
                    _loop_vars['requirement'] = l_1_requirement
                    if t_5(environment.getattr(environment.getattr(l_1_ssl_profile, 'chain_certificate'), 'requirement')):
                        pass
                        l_1_tmp_requirement = []
                        _loop_vars['tmp_requirement'] = l_1_tmp_requirement
                        if t_5(environment.getattr(environment.getattr(environment.getattr(l_1_ssl_profile, 'chain_certificate'), 'requirement'), 'basic_constraint_ca'), True):
                            pass
                            context.call(environment.getattr((undefined(name='tmp_requirement') if l_1_tmp_requirement is missing else l_1_tmp_requirement), 'append'), 'Basic Constraint CA', _loop_vars=_loop_vars)
                        if t_5(environment.getattr(environment.getattr(environment.getattr(l_1_ssl_profile, 'chain_certificate'), 'requirement'), 'include_root_ca'), True):
                            pass
                            context.call(environment.getattr((undefined(name='tmp_requirement') if l_1_tmp_requirement is missing else l_1_tmp_requirement), 'append'), 'Root CA Included', _loop_vars=_loop_vars)
                        if (t_4((undefined(name='tmp_requirement') if l_1_tmp_requirement is missing else l_1_tmp_requirement)) > 0):
                            pass
                            l_1_requirement = t_3(context.eval_ctx, (undefined(name='tmp_requirement') if l_1_tmp_requirement is missing else l_1_tmp_requirement), ', ')
                            _loop_vars['requirement'] = l_1_requirement
                    yield '| '
                    yield str((undefined(name='chain_certs') if l_1_chain_certs is missing else l_1_chain_certs))
                    yield ' | '
                    yield str((undefined(name='requirement') if l_1_requirement is missing else l_1_requirement))
                    yield ' |\n'
            l_1_ssl_profile = l_1_trust_certs = l_1_requirement = l_1_tmp_requirement = l_1_policy = l_1_system = l_1_chain_certs = missing
        if t_5(environment.getattr(environment.getattr((undefined(name='management_security') if l_0_management_security is missing else l_0_management_security), 'password'), 'policies')):
            pass
            yield '\n### Password Policies\n\n| Policy Name | Digits | Length | Lowercase letters | Special characters | Uppercase letters | Repetitive characters | Sequential characters |\n|-------------|--------|--------|-------------------|--------------------|-------------------|-----------------------|----------------------|\n'
            for l_1_policy in t_2(environment.getattr(environment.getattr((undefined(name='management_security') if l_0_management_security is missing else l_0_management_security), 'password'), 'policies'), 'name'):
                l_1_min_digits = l_1_min_length = l_1_min_lower = l_1_min_special = l_1_min_upper = l_1_max_repetitive = l_1_max_sequential = missing
                _loop_vars = {}
                pass
                l_1_min_digits = (environment.getattr(environment.getattr(l_1_policy, 'minimum'), 'digits') if t_5(environment.getattr(environment.getattr(l_1_policy, 'minimum'), 'digits')) else 'N/A')
                _loop_vars['min_digits'] = l_1_min_digits
                l_1_min_length = (environment.getattr(environment.getattr(l_1_policy, 'minimum'), 'length') if t_5(environment.getattr(environment.getattr(l_1_policy, 'minimum'), 'length')) else 'N/A')
                _loop_vars['min_length'] = l_1_min_length
                l_1_min_lower = (environment.getattr(environment.getattr(l_1_policy, 'minimum'), 'lower') if t_5(environment.getattr(environment.getattr(l_1_policy, 'minimum'), 'lower')) else 'N/A')
                _loop_vars['min_lower'] = l_1_min_lower
                l_1_min_special = (environment.getattr(environment.getattr(l_1_policy, 'minimum'), 'special') if t_5(environment.getattr(environment.getattr(l_1_policy, 'minimum'), 'special')) else 'N/A')
                _loop_vars['min_special'] = l_1_min_special
                l_1_min_upper = (environment.getattr(environment.getattr(l_1_policy, 'minimum'), 'upper') if t_5(environment.getattr(environment.getattr(l_1_policy, 'minimum'), 'upper')) else 'N/A')
                _loop_vars['min_upper'] = l_1_min_upper
                l_1_max_repetitive = (environment.getattr(environment.getattr(l_1_policy, 'maximum'), 'repetitive') if t_5(environment.getattr(environment.getattr(l_1_policy, 'maximum'), 'repetitive')) else 'N/A')
                _loop_vars['max_repetitive'] = l_1_max_repetitive
                l_1_max_sequential = (environment.getattr(environment.getattr(l_1_policy, 'maximum'), 'sequential') if t_5(environment.getattr(environment.getattr(l_1_policy, 'maximum'), 'sequential')) else 'N/A')
                _loop_vars['max_sequential'] = l_1_max_sequential
                yield '| '
                yield str(environment.getattr(l_1_policy, 'name'))
                yield ' | > '
                yield str((undefined(name='min_digits') if l_1_min_digits is missing else l_1_min_digits))
                yield ' | > '
                yield str((undefined(name='min_length') if l_1_min_length is missing else l_1_min_length))
                yield ' | > '
                yield str((undefined(name='min_lower') if l_1_min_lower is missing else l_1_min_lower))
                yield ' | > '
                yield str((undefined(name='min_special') if l_1_min_special is missing else l_1_min_special))
                yield ' | > '
                yield str((undefined(name='min_upper') if l_1_min_upper is missing else l_1_min_upper))
                yield ' | < '
                yield str((undefined(name='max_repetitive') if l_1_max_repetitive is missing else l_1_max_repetitive))
                yield ' | < '
                yield str((undefined(name='max_sequential') if l_1_max_sequential is missing else l_1_max_sequential))
                yield ' |\n'
            l_1_policy = l_1_min_digits = l_1_min_length = l_1_min_lower = l_1_min_special = l_1_min_upper = l_1_max_repetitive = l_1_max_sequential = missing
        yield '\n### Management Security Device Configuration\n\n```eos\n'
        template = environment.get_template('eos/management-security.j2', 'documentation/management-security.j2')
        for event in template.root_render_func(template.new_context(context.get_all(), True, {'ssl_profiles_certs': l_0_ssl_profiles_certs})):
            yield event
        yield '```\n'

blocks = {}
debug_info = '7=43&15=46&16=49&18=51&19=54&21=56&22=59&24=61&25=64&27=66&33=69&34=72&35=76&36=78&37=80&39=83&40=95&41=97&42=99&44=101&45=103&47=104&48=106&49=107&52=109&54=119&55=121&59=124&60=126&61=128&62=130&63=132&64=134&66=135&67=137&69=138&70=140&73=142&74=144&75=146&77=148&78=150&80=154&82=157&84=165&88=168&89=170&90=172&91=174&92=176&93=178&95=179&96=181&98=182&99=184&102=187&106=192&112=195&113=199&114=201&115=203&116=205&117=207&118=209&119=211&120=214&127=232'