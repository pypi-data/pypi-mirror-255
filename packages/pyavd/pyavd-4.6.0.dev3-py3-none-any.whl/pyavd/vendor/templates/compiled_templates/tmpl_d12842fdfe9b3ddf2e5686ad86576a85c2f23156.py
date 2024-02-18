from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'eos/lldp.j2'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_lldp = resolve('lldp')
    try:
        t_1 = environment.tests['arista.avd.defined']
    except KeyError:
        @internalcode
        def t_1(*unused):
            raise TemplateRuntimeError("No test named 'arista.avd.defined' found.")
    pass
    if t_1((undefined(name='lldp') if l_0_lldp is missing else l_0_lldp)):
        pass
        yield '!\n'
        if t_1(environment.getattr((undefined(name='lldp') if l_0_lldp is missing else l_0_lldp), 'run'), False):
            pass
            yield 'no lldp run\n'
        if t_1(environment.getattr((undefined(name='lldp') if l_0_lldp is missing else l_0_lldp), 'timer')):
            pass
            yield 'lldp timer '
            yield str(environment.getattr((undefined(name='lldp') if l_0_lldp is missing else l_0_lldp), 'timer'))
            yield '\n'
        if t_1(environment.getattr((undefined(name='lldp') if l_0_lldp is missing else l_0_lldp), 'timer_reinitialization')):
            pass
            yield 'lldp timer reinitialization '
            yield str(environment.getattr((undefined(name='lldp') if l_0_lldp is missing else l_0_lldp), 'timer_reinitialization'))
            yield '\n'
        if t_1(environment.getattr((undefined(name='lldp') if l_0_lldp is missing else l_0_lldp), 'holdtime')):
            pass
            yield 'lldp hold-time '
            yield str(environment.getattr((undefined(name='lldp') if l_0_lldp is missing else l_0_lldp), 'holdtime'))
            yield '\n'
        if t_1(environment.getattr((undefined(name='lldp') if l_0_lldp is missing else l_0_lldp), 'management_address')):
            pass
            yield 'lldp management-address '
            yield str(environment.getattr((undefined(name='lldp') if l_0_lldp is missing else l_0_lldp), 'management_address'))
            yield '\n'
        if t_1(environment.getattr((undefined(name='lldp') if l_0_lldp is missing else l_0_lldp), 'vrf')):
            pass
            yield 'lldp management-address vrf '
            yield str(environment.getattr((undefined(name='lldp') if l_0_lldp is missing else l_0_lldp), 'vrf'))
            yield '\n'
        if t_1(environment.getattr((undefined(name='lldp') if l_0_lldp is missing else l_0_lldp), 'receive_packet_tagged_drop'), True):
            pass
            yield 'lldp receive packet tagged drop\n'
        if t_1(environment.getattr((undefined(name='lldp') if l_0_lldp is missing else l_0_lldp), 'tlvs')):
            pass
            for l_1_tlv in environment.getattr((undefined(name='lldp') if l_0_lldp is missing else l_0_lldp), 'tlvs'):
                l_1_lldp_tlv_transmit_cli = resolve('lldp_tlv_transmit_cli')
                _loop_vars = {}
                pass
                if (t_1(environment.getattr(l_1_tlv, 'name')) and t_1(environment.getattr(l_1_tlv, 'transmit'))):
                    pass
                    l_1_lldp_tlv_transmit_cli = str_join(('lldp tlv transmit ', environment.getattr(l_1_tlv, 'name'), ))
                    _loop_vars['lldp_tlv_transmit_cli'] = l_1_lldp_tlv_transmit_cli
                    if t_1(environment.getattr(l_1_tlv, 'transmit'), False):
                        pass
                        l_1_lldp_tlv_transmit_cli = str_join(('no ', (undefined(name='lldp_tlv_transmit_cli') if l_1_lldp_tlv_transmit_cli is missing else l_1_lldp_tlv_transmit_cli), ))
                        _loop_vars['lldp_tlv_transmit_cli'] = l_1_lldp_tlv_transmit_cli
                    yield str((undefined(name='lldp_tlv_transmit_cli') if l_1_lldp_tlv_transmit_cli is missing else l_1_lldp_tlv_transmit_cli))
                    yield '\n'
            l_1_tlv = l_1_lldp_tlv_transmit_cli = missing

blocks = {}
debug_info = '7=18&9=21&12=24&13=27&15=29&16=32&18=34&19=37&21=39&22=42&24=44&25=47&27=49&30=52&31=54&32=58&33=60&34=62&35=64&37=66'