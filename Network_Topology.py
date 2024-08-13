#####################
#
# Auther: Aizaz Ali
# Date: 25 June 2024
# Version v1
#
#####################

# DESCRIPTION:
# MAIN-FRAME
# THE PROGRAME HAS MANY LINKS WHICH HAS DIFFERENT LINK CHARACHTERS
# BW / LOSSES / QUEUE SIZE / DELAY
# 2 HOSTS AND 2 LINKS
# 10 LINKS BETWEEN THESE 2 SWITCHES
# NETWORK TOPOLOGY CREATED
#
# RYU CONTROLLER
# ARP-HANDLER OTHER-WISE ARP FLOODING HAPPEND IN THE SYSTEM
#


from mininet.net import Mininet
from mininet.node import RemoteController, OVSSwitch
from mininet.cli import CLI
from mininet.link import TCLink
from mininet.log import setLogLevel, info
from mininet.topo import Topo

from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.lib.packet import arp
from ryu.lib.packet import ipv6
from ryu.lib import mac


class SimpleARP13(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(SimpleARP13, self).__init__(*args, **kwargs)
        self.mac_to_port = {}
        self.arp_table = {}
        self.sw = {}

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        # install table-miss flow entry
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                          ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, 0, match, actions)
        self.logger.info("switch:%s connected", datapath.id)

    def add_flow(self, datapath, priority, match, actions):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                             actions)]

        mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
                                idle_timeout=5, hard_timeout=15,
                                match=match, instructions=inst)
        datapath.send_msg(mod)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        in_port = msg.match['in_port']

        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocols(ethernet.ethernet)[0]
        dst = eth.dst
        src = eth.src
        dpid = datapath.id

        if pkt.get_protocol(ipv6.ipv6):  # Drop IPV6 packets
            match = parser.OFPMatch(eth_type=eth.ethertype)
            actions = []
            self.add_flow(datapath, 1, match, actions)
            return None

        arp_pkt = pkt.get_protocol(arp.arp)

        if arp_pkt:
            self.arp_table[arp_pkt.src_ip] = src  # ARP learning
            self.logger.info(" ARP: %s -> %s", arp_pkt.src_ip, arp_pkt.dst_ip)
            if self.arp_handler(msg):  # answer or drop
                return None

        self.mac_to_port.setdefault(dpid, {})
        self.logger.info("packet in %s %s %s %s", dpid, src, dst, in_port)

        # Learn a mac address to avoid FLOOD next time.
        if src not in self.mac_to_port[dpid]:
            self.mac_to_port[dpid][src] = in_port

        if dst in self.mac_to_port[dpid]:
            out_port = self.mac_to_port[dpid][dst]
        else:
            out_port = ofproto.OFPP_FLOOD

        actions = [parser.OFPActionOutput(out_port)]

        # Install a flow to avoid packet_in next time
        if out_port != ofproto.OFPP_FLOOD:
            self.logger.info(" install flow_mod:%s -> %s ", in_port, out_port)
            match = parser.OFPMatch(in_port=in_port, eth_dst=dst)
            self.add_flow(datapath, 1, match, actions)

        data = None
        if msg.buffer_id == ofproto.OFP_NO_BUFFER:
            data = msg.data
        out = parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id,
                                  in_port=in_port, actions=actions, data=data)

        datapath.send_msg(out)

    def arp_handler(self, msg):
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        in_port = msg.match['in_port']

        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocols(ethernet.ethernet)[0]
        arp_pkt = pkt.get_protocol(arp.arp)

        if eth:
            eth_dst = eth.dst
            eth_src = eth.src

        # Break the loop for avoiding ARP broadcast storm
        if eth_dst == mac.BROADCAST_STR:  # and arp_pkt:
            arp_dst_ip = arp_pkt.dst_ip
            arp_src_ip = arp_pkt.src_ip

            if (datapath.id, arp_src_ip, arp_dst_ip) in self.sw:
                # packet come back at different port.
                if self.sw[(datapath.id, arp_src_ip, arp_dst_ip)] != in_port:
                    datapath.send_packet_out(in_port=in_port, actions=[])
                    return True
            else:
                self.sw[(datapath.id, arp_src_ip, arp_dst_ip)] = in_port
                self.mac_to_port.setdefault(datapath.id, {})
                self.mac_to_port[datapath.id][eth_src] = in_port

        # Try to reply arp request
        if arp_pkt:
            if arp_pkt.opcode == arp.ARP_REQUEST:
                arp_src_ip = arp_pkt.src_ip
                arp_dst_ip = arp_pkt.dst_ip
                if arp_dst_ip in self.arp_table:
                    actions = [parser.OFPActionOutput(in_port)]
                    ARP_Reply = packet.Packet()
                    ARP_Reply.add_protocol(ethernet.ethernet(
                        ethertype=eth.ethertype,
                        dst=eth_src,
                        src=self.arp_table[arp_dst_ip]))
                    ARP_Reply.add_protocol(arp.arp(
                        opcode=arp.ARP_REPLY,
                        src_mac=self.arp_table[arp_dst_ip],
                        src_ip=arp_dst_ip,
                        dst_mac=eth_src,
                        dst_ip=arp_src_ip))
                    ARP_Reply.serialize()
                    out = parser.OFPPacketOut(
                        datapath=datapath,
                        buffer_id=ofproto.OFP_NO_BUFFER,
                        in_port=ofproto.OFPP_CONTROLLER,
                        actions=actions, data=ARP_Reply.data)
                    datapath.send_msg(out)
                    return True
        return False


class MyTopo(Topo):
    def build(self):
        h1 = self.addHost('h1')
        h2 = self.addHost('h2')
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')
        self.addLink(h1, s1, cls=TCLink)
        self.addLink(h2, s2, cls=TCLink)

        link_options = [
            {'bw': 10, 'delay': '5ms', 'loss': 1, 'max_queue_size': 2000},
            {'bw': 20, 'delay': '10ms', 'loss': 1, 'max_queue_size': 2000},
            {'bw': 30, 'delay': '50ms', 'loss': 20, 'max_queue_size': 100},
            {'bw': 40, 'delay': '7ms', 'loss': 2, 'max_queue_size': 4000},
            {'bw': 50, 'delay': '7ms', 'loss': 5, 'max_queue_size': 50000},
            {'bw': 60, 'delay': '15ms', 'loss': 80, 'max_queue_size': 8000},
            {'bw': 70, 'delay': '40ms', 'loss': 25, 'max_queue_size': 150},
            {'bw': 80, 'delay': '25ms', 'loss': 3, 'max_queue_size': 8000},
            {'bw': 90, 'delay': '10ms', 'loss': 4, 'max_queue_size': 9000},
            {'bw': 100, 'delay': '1ms', 'loss': 1, 'max_queue_size': 10000},
        ]

        # Add links with the specified options
        for i in range(10):
            self.addLink(s1, s2, cls=TCLink, **link_options[i])

def setup_failover():
    import os
    os.system('ovs-ofctl add-group s1 group_id=1,type=ff,bucket=watch_port=2,output=2,bucket=watch_port=3,output=3,bucket=watch_port=4,output=4')
    os.system('ovs-ofctl add-flow s1 "priority=200,in_port=1,actions=group:1"')

def run():
    topo = MyTopo()
    net = Mininet(topo=topo, link=TCLink, controller=None, switch=OVSSwitch)

    # Add Ryu controller
    controller_ip = '127.0.0.1'  # Replace with actual IP if Ryu is running on a different machine
    controller_port = 6633  # Default port for Ryu
    net.addController('c0', controller=RemoteController, ip=controller_ip, port=controller_port)

    net.start()

    # Set up the fast failover group and flows
    setup_failover()

    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    run()
topos = {'mytopo': (lambda: MyTopo())}
